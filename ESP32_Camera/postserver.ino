#include <WiFiManager.h>
#include <PubSubClient.h>
#include "M5TimerCAM.h"

// Note : SSID et PASS sont gérés par WiFiManager, pas besoin de les définir ici sauf si tu veux forcer une connexion code.

#define MQTT_SERVER      "192.168.2.41"
#define MQTT_PORT        1883
#define MQTT_TOPIC_PHOTO "nichoir/photo"
#define MQTT_TOPIC_BATT  "nichoir/battery" // CORRIGÉ : Topic distinct

#define CAM_EXT_WAKEUP_PIN 4
#define WAKEUP_INTERVAL_SEC 10 // Attention: 10 secondes pour le test. Mettre 86400 pour 24h.

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void reconnectMQTT() {
  // On essaye 3 fois max pour ne pas vider la batterie si le serveur est down
  int attempts = 0;
  while (!mqttClient.connected() && attempts < 3) {
    if (mqttClient.connect("TimerCAMClient")) {
      Serial.println("MQTT connecté");
    } else {
      delay(1000);
      attempts++;
    }
  }
}

void sendPhotoMQTT() {
  if (TimerCAM.Camera.get()) {
    Serial.println("Photo capturée, envoi MQTT...");

    // Récupérer le niveau de batterie
    float level = TimerCAM.Power.getBatteryLevel();
    level = 30.0;
    char batteryInfo[32];
    // On ajoute un marqueur ### pour séparer l'image du texte à la réception
    snprintf(batteryInfo, sizeof(batteryInfo), "###%.2f", level);

    // Taille totale = image + "###" + info batterie
    size_t totalSize = TimerCAM.Camera.fb->len + strlen(batteryInfo);

    // Augmenter la taille du buffer MQTT si nécessaire (par défaut c'est souvent 256 octets, trop petit pour une image)
    // Note: beginPublish gère le streaming, donc le buffer size est moins critique, mais attention aux limites.
    if (mqttClient.beginPublish(MQTT_TOPIC_PHOTO, totalSize, false)) {
      
      // 1. Envoyer l'image
      mqttClient.write(TimerCAM.Camera.fb->buf, TimerCAM.Camera.fb->len);
      
      // 2. Envoyer les infos batterie à la suite
      mqttClient.write((const uint8_t*)batteryInfo, strlen(batteryInfo));

      if (mqttClient.endPublish()) {
        Serial.printf("Image + batterie envoyées (%.2f V)\n", level);
      } else {
        Serial.println("Erreur lors de la fin de l'envoi MQTT...");
      }
    } else {
      Serial.println("Erreur au début de l'envoi MQTT. Vérifiez la connexion.");
    }

    // Libérer la mémoire APRES l'envoi
    TimerCAM.Camera.free();
  } else {
    Serial.println("Echec capture photo");
  }
}

void sendBatteryMQTT() {
  float level = TimerCAM.Power.getBatteryLevel();
  level = 66.4;
  char payload[32];
  snprintf(payload, sizeof(payload), "%.2f", level); // Juste le chiffre, plus facile à tracer dans Home Assistant
  
  // CORRIGÉ : On envoie le char array 'payload', pas le float 'level'
  mqttClient.publish(MQTT_TOPIC_BATT, payload); 
  Serial.printf("Batterie envoyée : %s %\n", payload);
}

void setup() {
  Serial.begin(115200);
  TimerCAM.begin(true);

  // --- Connexion WiFi ---
  WiFiManager wm;
  
  // Custom parameters
  WiFiManagerParameter custom_api_key("api", "API Key", "", 32);
  WiFiManagerParameter custom_mode("mode", "Device Mode", "", 16);
  wm.addParameter(&custom_api_key);
  wm.addParameter(&custom_mode);

  // AJOUT IMPORTANT : Timeout. Si pas de wifi après 30 sec, on ne bloque pas indéfiniment (vide la batterie)
  wm.setConfigPortalTimeout(180); // 3 minutes pour configurer si besoin
  wm.setConnectTimeout(30);       // 30 secondes pour essayer de se connecter au WiFi connu

  // Connexion
  if(!wm.autoConnect("ESP32_Nichoir_AP", "12345678")) {
      Serial.println("Echec connexion WiFi ou Timeout -> Dodo");
      // Si échec wifi, on retourne dormir pour réessayer plus tard
      // (Code de mise en veille à la fin du setup)
  } else {
      Serial.println("WiFi OK");
      
      mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
      // Il faut augmenter la taille du buffer pour envoyer de gros paquets (images) si on n'utilise pas le streaming pur
      mqttClient.setBufferSize(2048); 
      
      reconnectMQTT();

      // --- Initialisation caméra ---
      TimerCAM.Camera.begin();
      // UXGA est très grand pour du MQTT, attention à la lenteur. SVGA ou VGA est souvent mieux pour l'IoT.
      TimerCAM.Camera.sensor->set_pixformat(TimerCAM.Camera.sensor, PIXFORMAT_JPEG);
      TimerCAM.Camera.sensor->set_framesize(TimerCAM.Camera.sensor, FRAMESIZE_VGA);
      TimerCAM.Camera.sensor->set_vflip(TimerCAM.Camera.sensor, 1);
      TimerCAM.Camera.sensor->set_hmirror(TimerCAM.Camera.sensor, 0); 

      // --- Détection du type de réveil ---
      esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();

      if (mqttClient.connected()) {
        if (wakeup_reason == ESP_SLEEP_WAKEUP_EXT0 || wakeup_reason == ESP_SLEEP_WAKEUP_TIMER) {
          Serial.println("Réveil par signal externe (PIR?)");
          sendPhotoMQTT();
        } else if (wakeup_reason == ESP_SLEEP_WAKEUP_TIMER) {
          Serial.println("Réveil par timer (Status)");
          sendBatteryMQTT();
        } else {
          Serial.println("Premier démarrage ou Reset");
          sendBatteryMQTT(); // Envoie au moins la batterie pour dire "Je suis là"
        }
        // Petit délai pour être sûr que le message MQTT parte
        delay(500); 
      }
      
      TimerCAM.Camera.deinit();
  }

  // --- Préparer le deep sleep ---
  // Maintien de l'alimentation (Spécifique M5TimerCAM)
  gpio_hold_en((gpio_num_t)POWER_HOLD_PIN);
  gpio_deep_sleep_hold_en();

  // Configuration du réveil
  esp_sleep_enable_ext0_wakeup((gpio_num_t)CAM_EXT_WAKEUP_PIN, 1); // HIGH = réveil
  esp_sleep_enable_timer_wakeup(WAKEUP_INTERVAL_SEC * 1000000ULL); 

  Serial.println("Mise en veille...");
  Serial.flush(); // Attendre que le Serial ait fini d'écrire
  esp_deep_sleep_start();
}

void loop() {
  // Vide
}