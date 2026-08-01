/*
 * TESTE MINIMO — grave isto primeiro para testar a ESP32.
 * Se aparecer "MINIMAL OK" no Serial, o hardware esta bom.
 */

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("\n=== TESTE MINIMO ===");
  Serial.println("MINIMAL OK");
  Serial.println("ESP32 funcionando. Pode gravar elevalocker_sync.ino");
}

void loop() {
  delay(5000);
  Serial.println("Ainda vivo...");
}
