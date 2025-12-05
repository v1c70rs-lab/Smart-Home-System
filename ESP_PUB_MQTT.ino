#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <BH1750.h>

const char* ssid = "H369A7296C8_2.4GHz";
const char* password = "xxxxxx";

IPAddress ip(192, 168, 2 , 46);
IPAddress gateway(192, 168, 2, 254);
IPAddress subnet(255, 255, 255, 0);

const char* MQTT_HOST = "192.168.2.19";
const int MQTT_PORT = 1883;

WiFiClient client;
PubSubClient mqttClient(client);
BH1750 lightMeter;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  Wire.begin(0,2);
  lightMeter.begin();
  connectWiFi();  //client verbinden met WiFi
  connectMQTT();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (!mqttClient.connected()) {
    connectMQTT();
  }

  int lux = lightMeter.readLightLevel();
  String message = String(lux);
  mqttClient.publish("home/lightsensor", message.c_str());
  delay(1000);
}

// Functie voor het verbinden met de WiFi
void connectWiFi() {
  WiFi.config(ip, gateway, subnet);
  Serial.println();
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000); 
    Serial.print(".");
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println(" :Connected!");
      Serial.println();
    }
  }
  
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("IP gateway: ");
  Serial.println(WiFi.gatewayIP());
  Serial.print("IP subnet: ");
  Serial.println(WiFi.subnetMask());
  Serial.println();
}

void connectMQTT() {
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  Serial.print("Connecting to MQTT-broker");

  while (!mqttClient.connected()) {
    if (mqttClient.connect("IkWilKaas")) {
      Serial.println(" :Connected!");
      mqttClient.publish("test", "hello");
    }
    else {
      Serial.print("failed, rc=");
      Serial.println(mqttClient.state());
      delay(1000);
    }
  }
}
