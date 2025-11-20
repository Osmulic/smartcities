#include <PubSubClient.h>
 
#include "M5TimerCAM.h"
#include <WiFi.h>
#include <PubSubClient.h>
 
#define WIFI_SSID     "ssid"
#define WIFI_PASS     "password"
 
// --- MQTT ---
#define MQTT_SERVER  "ip_address"
#define MQTT_PORT    1883
#define MQTT_TOPIC   "nichoir/photo"
 
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
 
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqttClient.connect("TimerCAMClient")) {
      Serial.println("Connected!");
    } else {
      Serial.print("Failed, rc=");
      Serial.println(mqttClient.state());
      delay(2000);
    }
  }
}
 
void setup() {
    Serial.begin(115200);
   
    TimerCAM.begin();
 
    if (!TimerCAM.Camera.begin()) {
        Serial.println("Camera Init Fail");
        return;
    }
    Serial.println("Camera Init Success");
 
    TimerCAM.Camera.sensor->set_pixformat(TimerCAM.Camera.sensor, PIXFORMAT_JPEG);
    TimerCAM.Camera.sensor->set_framesize(TimerCAM.Camera.sensor, FRAMESIZE_UXGA);
    TimerCAM.Camera.sensor->set_vflip(TimerCAM.Camera.sensor, 1);
 
    // --- WIFI ---
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println(" Connected!");
 
    // --- MQTT ---
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    reconnectMQTT();
}
 
void loop() {
    if (!mqttClient.connected()) reconnectMQTT();
    mqttClient.loop();

    if (TimerCAM.Camera.get()) {
        Serial.println("Photo capturée, envoi MQTT...");
        Serial.println(TimerCAM.Camera.fb->len);

        // Commencer la publication
        if (mqttClient.beginPublish(MQTT_TOPIC, TimerCAM.Camera.fb->len, false)) {
            // Écrire les données de l'image
            mqttClient.write(TimerCAM.Camera.fb->buf, TimerCAM.Camera.fb->len);
            // Terminer la publication
            if (mqttClient.endPublish()) {
                Serial.println("Image envoyée via MQTT !");
            } else {
                Serial.println("Erreur lors de la fin de l'envoi MQTT...");
            }
        } else {
            Serial.println("Erreur lors du début de l'envoi MQTT...");
        }

        TimerCAM.Camera.free();
        delay(5000);
    }
}
