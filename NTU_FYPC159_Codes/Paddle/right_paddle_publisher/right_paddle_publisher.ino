#include <WiFi.h>
#include <PubSubClient.h>
#include "HX711.h" // to use HX711 amplifier's methods 
const char* ssid = "";
const char* password = "";
const char* mqtt_server = "192.168.1.1"; //1.1 is baot raspi, .7 is laptop //"192.168.1.7";  

// declare pins and variables
const int DT_PIN =  26; // Data pin 26 for ESP32
const int SCK_PIN = 25; // CLK pin 25 for ESP32
const long CALIBRATION_FACTOR = 82182.6; // SET CALIBRATION FACTOR, *CHANGE HERE*

unsigned long startMillis;
int counter = 0;
//float i = -1; 
HX711 scale; // create scale object
WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0;

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883); // 1883 is default port set for most mqtt servers/applications

  Serial.begin(115200); // start serial
  scale.begin(DT_PIN, SCK_PIN); // initialise amplifier
  scale.set_scale(CALIBRATION_FACTOR); // set calibration factor
  scale.tare(); // reset the scale to 0

  startMillis = millis(); //get starting time 
}

void loop() {
  if (!client.connected()) {
    connect_mqttServer();
  }

  client.loop();
  //Serial.println(scale.get_units(1)); // get the average of 5 strain gauge data and send to client via bluetooth
  counter++; //add 1 to the counter

  if (millis() - startMillis >= 1000){ //print the number of outputs each second
    Serial.print("Number of outputs in the second: ");
    Serial.println(counter); //print number of outputs per second
    startMillis = millis(); //reset the start time
    counter = 0; //reset the counter
  }

  String merge = String(scale.get_units(1)) ;
  //i = i + 0.001;
  //merge =String(i);
  client.publish("esp32_right", merge.c_str());

}

void connect_mqttServer() {
  while (!client.connected()) {
    if (WiFi.status() != WL_CONNECTED) {
      setup_wifi();
    }

    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32_client1")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" trying again in 2 seconds");
      delay(2000);
    }
  }
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
