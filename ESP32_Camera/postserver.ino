#include "M5TimerCAM.h"
#include <WiFi.h>
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <PubSubClient.h>

// --- CONFIGURATION ---
#define MQTT_SERVER     "192.168.129.140"
#define MQTT_PORT       1883
#define MQTT_TOPIC      "nichoir/photo"
#define SEND_INTERVAL   5000  // Time between photos in ms

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

unsigned long lastCaptureTime = 0;

void reconnectMQTT() {
    // Loop until we're reconnected
    while (!mqttClient.connected()) {
        Serial.print("Connecting to MQTT...");
        // Create a random client ID
        String clientId = "TimerCAM-" + String(random(0xffff), HEX);
        
        if (mqttClient.connect(clientId.c_str())) {
            Serial.println("Connected!");
        } else {
            Serial.print("Failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 2 seconds");
            delay(2000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    
    // 1. Initialize Camera (Before WiFi to ensure hardware is ready)
    TimerCAM.begin();
    if (!TimerCAM.Camera.begin()) {
        Serial.println("Camera Init Fail");
        while(true); // Stop here if camera fails
    }
    Serial.println("Camera Init Success");

    // Camera Settings
    TimerCAM.Camera.sensor->set_pixformat(TimerCAM.Camera.sensor, PIXFORMAT_JPEG);
    // Note: UXGA (1600x1200) creates large packets. If MQTT fails, try FRAMESIZE_SVGA
    TimerCAM.Camera.sensor->set_framesize(TimerCAM.Camera.sensor, FRAMESIZE_VGA); 
    TimerCAM.Camera.sensor->set_vflip(TimerCAM.Camera.sensor, 1);
    TimerCAM.Camera.sensor->set_hmirror(TimerCAM.Camera.sensor, 0);

    // 2. WiFi Manager Setup
    WiFiManager wm;
    
    // Custom parameters (displayed in portal, logic to save them to flash not included here)
    WiFiManagerParameter custom_api_key("api", "API Key", "", 32);
    WiFiManagerParameter custom_mode("mode", "Device Mode", "", 16);
    wm.addParameter(&custom_api_key);
    wm.addParameter(&custom_mode);

    // Connect
    // Creates AP "ESP32_Config_AP" if connection fails
    if(!wm.autoConnect("ESP32_Config_AP", "12345678")) {
        Serial.println("Failed to connect and hit timeout");
        ESP.restart();
    }

    Serial.println("WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // 3. MQTT Setup
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
    // Keep MQTT connection alive
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    mqttClient.loop();

    // Non-blocking timer
    if (millis() - lastCaptureTime > SEND_INTERVAL) {
        lastCaptureTime = millis();

        if (TimerCAM.Camera.get()) {
            Serial.print("Photo captured. Size: ");
            Serial.print(TimerCAM.Camera.fb->len);
            Serial.println(" bytes");

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

            // Free camera memory
            TimerCAM.Camera.free();
        } else {
            Serial.println("Failed to capture image");
        }
    }
}