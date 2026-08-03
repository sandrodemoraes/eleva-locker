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

  StaticJsonDocument<4096> body;
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

  StaticJsonDocument<8192> doc;
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
  bool admin = tokenValido();

  String html = "<!DOCTYPE html><html><head>";
  html += "<meta charset='utf-8'>";
  html += "<meta name='viewport' content='width=device-width,initial-scale=1'>";
  html += "<title>ELEVA LOCKER ESP</title>";
  html += "<style>";
  html += "body{font-family:Arial,sans-serif;margin:0;padding:16px;background:#f0f4f8;color:#1a1a2e}";
  html += "h1{text-align:center;margin:0 0 4px;font-size:1.5rem}";
  html += ".sub{text-align:center;color:#666;margin-bottom:16px;font-size:.9rem}";
  html += ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px;max-width:640px;margin:0 auto 20px}";
  html += ".porta{background:#fff;border-radius:10px;padding:12px;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.08)}";
  html += ".porta-num{font-size:1.4rem;font-weight:bold;margin-bottom:4px}";
  html += ".porta-rele{font-size:.75rem;color:#888}";
  html += ".badge{display:inline-block;padding:4px 10px;border-radius:20px;font-size:.8rem;font-weight:bold;margin-top:6px}";
  html += ".livre{background:#d4edda;color:#155724}";
  html += ".ocupado{background:#fff3cd;color:#856404}";
  html += ".retirar-box{max-width:400px;margin:0 auto;background:#fff;padding:20px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.1)}";
  html += "input[name=codigo]{width:100%;font-size:1.5rem;text-align:center;padding:10px;border:2px solid #ccc;border-radius:8px;box-sizing:border-box}";
  html += "button[type=submit]{width:100%;margin-top:12px;font-size:1.1rem;padding:14px;background:#2563eb;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:bold}";
  html += ".btn-abrir{display:inline-block;margin-top:8px;padding:6px 12px;background:#16a34a;color:#fff;text-decoration:none;border-radius:6px;font-size:.75rem}";
  html += "</style></head><body>";

  html += "<h1>ELEVA LOCKER ESP</h1>";
  html += "<p class='sub'>Sync v" + String(syncVersao) + " | Portas: " + String(totalCache);
  html += " | WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Online" : "OFFLINE") + "</p>";

  html += "<div class='grid'>";
  for (int i = 0; i < totalCache; i++) {
    html += "<div class='porta'>";
    html += "<div class='porta-num'>#" + String(cache[i].numero) + "</div>";
    html += "<div class='porta-rele'>Relé " + String(cache[i].rele) + "</div>";
    if (cache[i].ocupado) {
      html += "<span class='badge ocupado'>Ocupado</span>";
    } else {
      html += "<span class='badge livre'>Livre</span>";
    }
    if (admin && cache[i].rele > 0) {
      html += "<br><a class='btn-abrir' href='/abrir/" + String(cache[i].rele);
      html += "?token=" + String(ESP32_TOKEN) + "&duracao=3'>Abrir</a>";
    }
    html += "</div>";
  }
  html += "</div>";

  html += "<div class='retirar-box'>";
  html += "<form action='/retirar' method='POST'>";
  html += "<input name='codigo' maxlength='6' placeholder='Código 6 dígitos' inputmode='numeric' autocomplete='off'>";
  html += "<button type='submit'>RETIRAR</button>";
  html += "</form></div>";

  html += "</body></html>";
  server.send(200, "text/html", html);
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
    enviarHeartbeat();
    sincronizarComServidor();
    enviarEventosPendentes();
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
    }
    return;
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
