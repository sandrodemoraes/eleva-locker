/*
 * ELEVA LOCKER — Firmware ESP32 (offline-first, sync com servidor)
 *
 * Dependências (Arduino Library Manager):
 *   - ArduinoJson 6.x
 *
 * Fluxo:
 *   1. Cadastro 100% no servidor Flask (armários, compartimentos, encomendas)
 *   2. ESP sincroniza via GET /api/esp32/sync
 *   3. Sem internet: retirada por código usando cache local + fila de eventos
 *   4. Com internet: heartbeat + upload eventos + sync automático
 *
 * Configure abaixo: WIFI, SERVIDOR, TOKEN (copiar do painel /esp32)
 */

#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <ArduinoJson.h>

// ============ CONFIGURAÇÃO — EDITE AQUI ============
// Bancada ELEVA: ESP32 + BESTER 8ch | GPIO 16,17,18,19,21,22,23,27

const char* WIFI_SSID     = "ELEVA - ENERGIA SOLAR";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";

// IP do PC com python app.py (ipconfig) — NÃO use localhost
const char* SERVIDOR_URL  = "http://192.168.16.130:15000";

// Token: python tools/setup_bancada.py → copiar token
const char* ESP32_TOKEN   = "cole_o_token_aqui";

const int HTTP_PORT       = 80;
const int MIN_PORTAS      = 8;
const int MAX_PORTAS      = 32;

// GPIO padrão por relé (se servidor não enviar gpio no compartimento)
const int GPIO_PADRAO[] = {
  16, 17, 18, 19, 21, 22, 23, 27,
  26, 27, 32, 33, 12, 13, 14, 15,
  16, 17, 18, 19, 21, 22, 23, 27,
  26, 27, 32, 33, 12, 13, 14, 15
};

// ============ INTERNOS ============

WebServer server(HTTP_PORT);
Preferences prefs;

int syncVersao = 0;
int maxPortas = 16;
unsigned long releAte = 0;
int releAtivo = -1;
int gpioAtivo = -1;

unsigned long ultimoHeartbeat = 0;
unsigned long ultimoSync = 0;
bool redePendente = false;
const unsigned long INTERVALO_HEARTBEAT = 30000;
const unsigned long INTERVALO_SYNC      = 60000;
const unsigned long DURACAO_RELE_PADRAO = 3000;

struct CompartimentoCache {
  int id;
  int numero;
  int rele;
  int gpio;
  char codigo[8];
  bool ocupado;
};

CompartimentoCache cache[MAX_PORTAS];
int totalCache = 0;

// ============ RELÉ (non-blocking) ============

int gpioDoRele(int rele, int gpioServidor) {
  if (gpioServidor > 0) return gpioServidor;
  if (rele >= 1 && rele <= MAX_PORTAS) return GPIO_PADRAO[rele - 1];
  return -1;
}

void iniciarRele(int gpio, unsigned long duracaoMs) {
  if (gpio < 0) return;
  pinMode(gpio, OUTPUT);
  digitalWrite(gpio, HIGH);
  gpioAtivo = gpio;
  releAte = millis() + duracaoMs;
  Serial.printf("Relé GPIO%d ON por %lums\n", gpio, duracaoMs);
}

void atualizarRele() {
  if (gpioAtivo >= 0 && millis() >= releAte) {
    digitalWrite(gpioAtivo, LOW);
    Serial.printf("Relé GPIO%d OFF\n", gpioAtivo);
    gpioAtivo = -1;
    releAtivo = -1;
  }
}

void acionarPorRele(int rele, unsigned long duracaoMs) {
  for (int i = 0; i < totalCache; i++) {
    if (cache[i].rele == rele) {
      int g = gpioDoRele(rele, cache[i].gpio);
      iniciarRele(g, duracaoMs);
      releAtivo = rele;
      return;
    }
  }
  int g = gpioDoRele(rele, -1);
  iniciarRele(g, duracaoMs);
  releAtivo = rele;
}

// ============ FILA DE EVENTOS OFFLINE ============

void enfileirarEvento(const char* tipo, const char* codigo, int compId) {
  prefs.begin("eventos", false);
  int qtd = prefs.getInt("qtd", 0);
  if (qtd >= 20) qtd = 19;

  char chave[16];
  StaticJsonDocument<256> doc;
  doc["uid"] = String(millis()) + "-" + String(qtd);
  doc["tipo"] = tipo;
  doc["codigo"] = codigo;
  doc["compartimento_id"] = compId;
  doc["ts"] = millis();

  snprintf(chave, sizeof(chave), "e%d", qtd);
  String json;
  serializeJson(doc, json);
  prefs.putString(chave, json);
  prefs.putInt("qtd", qtd + 1);
  prefs.end();
  Serial.println("Evento enfileirado: " + json);
}

bool enviarEventosPendentes() {
  if (WiFi.status() != WL_CONNECTED) return false;

  prefs.begin("eventos", false);
  int qtd = prefs.getInt("qtd", 0);
  if (qtd == 0) { prefs.end(); return true; }

  DynamicJsonDocument body(4096);
  JsonArray arr = body.createNestedArray("eventos");

  for (int i = 0; i < qtd; i++) {
    char chave[16];
    snprintf(chave, sizeof(chave), "e%d", i);
    String ev = prefs.getString(chave, "");
    if (ev.length() > 0) {
      StaticJsonDocument<256> one;
      deserializeJson(one, ev);
      arr.add(one);
    }
  }

  String payload;
  serializeJson(body, payload);
  prefs.end();

  HTTPClient http;
  String url = String(SERVIDOR_URL) + "/api/esp32/eventos";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-ESP32-Token", ESP32_TOKEN);
  int code = http.POST(payload);
  http.end();

  if (code == 200) {
    prefs.begin("eventos", false);
    prefs.putInt("qtd", 0);
    for (int i = 0; i < qtd; i++) {
      char chave[16];
      snprintf(chave, sizeof(chave), "e%d", i);
      prefs.remove(chave);
    }
    prefs.end();
    Serial.println("Eventos sincronizados com servidor.");
    return true;
  }

  Serial.printf("Falha upload eventos HTTP %d\n", code);
  return false;
}

// ============ SYNC SERVIDOR → ESP ============

bool aplicarSync(JsonObject sync) {
  syncVersao = sync["versao"] | syncVersao;
  maxPortas = sync["max_portas"] | 16;
  if (maxPortas < MIN_PORTAS) maxPortas = MIN_PORTAS;
  if (maxPortas > MAX_PORTAS) maxPortas = MAX_PORTAS;

  totalCache = 0;
  JsonArray comps = sync["compartimentos"];
  JsonArray codigos = sync["codigos_ativos"];

  for (JsonObject c : comps) {
    if (totalCache >= MAX_PORTAS) break;
    cache[totalCache].id = c["id"];
    cache[totalCache].numero = c["numero"];
    cache[totalCache].rele = c["rele"] | 0;
    cache[totalCache].gpio = c["gpio"] | 0;
    cache[totalCache].codigo[0] = '\0';
    cache[totalCache].ocupado = (strcmp(c["status"] | "livre", "ocupado") == 0);
    totalCache++;
  }

  for (JsonObject cod : codigos) {
    int compId = cod["compartimento_id"];
    const char* codigo = cod["codigo"];
    for (int i = 0; i < totalCache; i++) {
      if (cache[i].id == compId) {
        strncpy(cache[i].codigo, codigo, 7);
        cache[i].codigo[7] = '\0';
        cache[i].ocupado = true;
        break;
      }
    }
  }

  prefs.begin("sync", false);
  prefs.putInt("versao", syncVersao);
  prefs.putInt("portas", totalCache);
  prefs.end();

  Serial.printf("Sync OK v%d — %d compartimentos\n", syncVersao, totalCache);
  return true;
}

bool sincronizarComServidor() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String url = String(SERVIDOR_URL) + "/api/esp32/sync";
  http.begin(url);
  http.addHeader("X-ESP32-Token", ESP32_TOKEN);
  int code = http.GET();

  if (code != 200) {
    Serial.printf("Sync falhou HTTP %d\n", code);
    http.end();
    return false;
  }

  String body = http.getString();
  http.end();

  DynamicJsonDocument doc(8192);
  if (deserializeJson(doc, body)) return false;
  if (!doc["sucesso"]) return false;

  return aplicarSync(doc["sync"]);
}

bool enviarHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  String url = String(SERVIDOR_URL) + "/api/esp32/heartbeat";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-ESP32-Token", ESP32_TOKEN);

  StaticJsonDocument<256> doc;
  doc["ip"] = WiFi.localIP().toString();
  doc["mac"] = WiFi.macAddress();
  doc["sync_versao"] = syncVersao;

  String payload;
  serializeJson(doc, payload);
  int code = http.POST(payload);

  if (code != 200) {
    http.end();
    return false;
  }

  String resp = http.getString();
  http.end();

  StaticJsonDocument<512> res;
  deserializeJson(res, resp);

  if (res["precisa_sync"] | false) {
    sincronizarComServidor();
  }

  return true;
}

// ============ RETIRADA OFFLINE ============

int buscarPorCodigo(const char* codigo) {
  for (int i = 0; i < totalCache; i++) {
    if (cache[i].ocupado && strcmp(cache[i].codigo, codigo) == 0) {
      return i;
    }
  }
  return -1;
}

bool retirarPorCodigo(const char* codigo, bool online) {
  int idx = buscarPorCodigo(codigo);
  if (idx < 0) return false;

  int rele = cache[idx].rele;
  acionarPorRele(rele, DURACAO_RELE_PADRAO);

  cache[idx].ocupado = false;
  cache[idx].codigo[0] = '\0';

  if (online) {
    HTTPClient http;
    String url = String(SERVIDOR_URL) + "/api/esp32/validar-codigo";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-ESP32-Token", ESP32_TOKEN);
    String body = String("{\"codigo\":\"") + codigo + "\"}";
    http.POST(body);
    http.end();
  } else {
    enfileirarEvento("retirada", codigo, cache[idx].id);
  }

  return true;
}

// ============ ROTAS HTTP NA ESP (servidor chama + totem local) ============

bool tokenValido() {
  return server.hasArg("token") && server.arg("token") == ESP32_TOKEN;
}

void rotaStatus() {
  if (!tokenValido()) {
    server.send(403, "application/json", "{\"erro\":\"token invalido\"}");
    return;
  }
  String json = "{\"online\":true,\"sync_versao\":" + String(syncVersao) +
                ",\"portas\":" + String(totalCache) + "}";
  server.send(200, "application/json", json);
}

void rotaAbrir() {
  if (!tokenValido()) {
    server.send(403, "application/json", "{\"erro\":\"token invalido\"}");
    return;
  }
  String path = server.uri();
  int rele = path.substring(path.lastIndexOf('/') + 1).toInt();
  unsigned long dur = server.hasArg("duracao") ? server.arg("duracao").toInt() * 1000UL : DURACAO_RELE_PADRAO;
  acionarPorRele(rele, dur);
  server.send(200, "application/json", "{\"sucesso\":true,\"rele\":" + String(rele) + "}");
}

void rotaRetirarLocal() {
  if (!server.hasArg("plain") && server.args() == 0) {
    server.send(400, "application/json", "{\"sucesso\":false}");
    return;
  }
  String codigo = server.arg("codigo");
  if (codigo.length() == 0) {
    StaticJsonDocument<128> doc;
    deserializeJson(doc, server.arg("plain"));
    codigo = doc["codigo"] | "";
  }
  codigo.trim();
  bool online = (WiFi.status() == WL_CONNECTED);
  if (retirarPorCodigo(codigo.c_str(), online)) {
    server.send(200, "application/json", "{\"sucesso\":true,\"offline\":" + String(!online) + "}");
  } else {
    server.send(403, "application/json", "{\"sucesso\":false,\"mensagem\":\"codigo invalido\"}");
  }
}

void rotaPainel() {
  bool admin = server.hasArg("token") && server.arg("token") == ESP32_TOKEN;

  int n = totalCache;
  if (n > MAX_PORTAS) n = MAX_PORTAS;
  if (n < 0) n = 0;

  server.setContentLength(CONTENT_LENGTH_UNKNOWN);
  server.send(200, "text/html", "");

  server.sendContent(
    "<!DOCTYPE html><html><head><meta charset=utf-8>"
    "<meta name=viewport content=\"width=device-width,initial-scale=1\">"
    "<title>ELEVA LOCKER ESP</title>"
    "<style>"
    "body{font-family:Arial,sans-serif;margin:16px;background:#f0f4f8;text-align:center}"
    "h1{margin:0 0 8px;font-size:1.4rem}"
    ".sub{color:#666;font-size:.85rem;margin-bottom:16px}"
    ".grid{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:520px;margin:0 auto 20px}"
    ".p{background:#fff;border-radius:8px;padding:10px 14px;min-width:100px;box-shadow:0 1px 4px rgba(0,0,0,.1)}"
    ".n{font-size:1.3rem;font-weight:bold}"
    ".r{font-size:.7rem;color:#888}"
    ".ok{color:#155724;background:#d4edda;padding:3px 8px;border-radius:12px;font-size:.75rem}"
    ".busy{color:#856404;background:#fff3cd;padding:3px 8px;border-radius:12px;font-size:.75rem}"
    ".box{max-width:360px;margin:0 auto;background:#fff;padding:16px;border-radius:10px}"
    "input{width:90%;font-size:1.4rem;text-align:center;padding:8px}"
    "button{width:95%;margin-top:10px;padding:12px;font-size:1rem;background:#2563eb;color:#fff;border:0;border-radius:8px}"
    "a.btn{display:inline-block;margin-top:6px;padding:4px 10px;background:#16a34a;color:#fff;text-decoration:none;border-radius:6px;font-size:.7rem}"
    "</style></head><body>"
  );

  server.sendContent("<h1>ELEVA LOCKER ESP</h1>");

  char buf[128];
  snprintf(buf, sizeof(buf),
    "<p class=sub>Sync v%d | Portas: %d | WiFi: %s</p>",
    syncVersao, n,
    WiFi.status() == WL_CONNECTED ? "Online" : "OFFLINE");
  server.sendContent(buf);

  server.sendContent("<div class=grid>");
  for (int i = 0; i < n; i++) {
    snprintf(buf, sizeof(buf),
      "<div class=p><div class=n>#%d</div><div class=r>Relé %d</div>",
      cache[i].numero, cache[i].rele);
    server.sendContent(buf);
    if (cache[i].ocupado) {
      server.sendContent("<span class=busy>Ocupado</span>");
    } else {
      server.sendContent("<span class=ok>Livre</span>");
    }
    if (admin && cache[i].rele > 0) {
      snprintf(buf, sizeof(buf),
        "<br><a class=btn href='/abrir/%d?token=%s&duracao=3'>Abrir</a>",
        cache[i].rele, ESP32_TOKEN);
      server.sendContent(buf);
    }
    server.sendContent("</div>");
  }
  server.sendContent("</div>");

  server.sendContent(
    "<div class=box><form action=/retirar method=POST>"
    "<input name=codigo maxlength=6 placeholder='Código 6 dígitos' inputmode=numeric>"
    "<button type=submit>RETIRAR</button></form></div>"
    "</body></html>"
  );
  server.sendContent("");
}

// ============ SETUP / LOOP ============

void conectarWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi");
  int tent = 0;
  while (WiFi.status() != WL_CONNECTED && tent < 40) {
    delay(500);
    Serial.print(".");
    tent++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("IP: " + WiFi.localIP().toString());
  }
}

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < MAX_PORTAS; i++) {
    int g = GPIO_PADRAO[i];
    pinMode(g, OUTPUT);
    digitalWrite(g, LOW);
  }

  prefs.begin("sync", true);
  syncVersao = prefs.getInt("versao", 0);
  totalCache = prefs.getInt("portas", 0);
  prefs.end();

  conectarWiFi();

  if (WiFi.status() == WL_CONNECTED) {
    redePendente = true;
  }

  server.on("/status", HTTP_GET, rotaStatus);
  server.on("/", HTTP_GET, rotaPainel);
  server.on("/retirar", HTTP_POST, rotaRetirarLocal);
  server.onNotFound([]() {
    if (server.uri().startsWith("/abrir/")) {
      rotaAbrir();
    } else {
      server.send(404, "text/plain", "Not found");
    }
  });

  server.begin();
  Serial.println("ESP32 ELEVA LOCKER pronto.");
}

void loop() {
  server.handleClient();
  atualizarRele();

  unsigned long agora = millis();

  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long ultimaTentativa = 0;
    if (agora - ultimaTentativa > 10000) {
      conectarWiFi();
      ultimaTentativa = agora;
      if (WiFi.status() == WL_CONNECTED) redePendente = true;
    }
    return;
  }

  if (redePendente) {
    enviarHeartbeat();
    sincronizarComServidor();
    enviarEventosPendentes();
    redePendente = false;
    ultimoHeartbeat = agora;
    ultimoSync = agora;
  }

  if (agora - ultimoHeartbeat > INTERVALO_HEARTBEAT) {
    enviarHeartbeat();
    enviarEventosPendentes();
    ultimoHeartbeat = agora;
  }

  if (agora - ultimoSync > INTERVALO_SYNC) {
    sincronizarComServidor();
    ultimoSync = agora;
  }
}
