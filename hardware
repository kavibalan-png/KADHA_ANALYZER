#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>


const char* ssid = "iot@12345";
const char* password = "iot@12345";
const char* serverURL = "http://herb.local:5000/esp32/data";


#define PH_PIN   35
#define TDS_PIN  32

#define OPT_OUT  33
#define S0 18
#define S1 5
#define S2 26
#define S3 27

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);


void setup() {
  Serial.begin(115200);

  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(OPT_OUT, INPUT);

  digitalWrite(S0, HIGH);
  digitalWrite(S1, LOW);   

  Wire.begin(21, 22);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();

  WiFi.begin(ssid, password);
  showText("Connecting WiFi...");
  while (WiFi.status() != WL_CONNECTED) delay(500);
  showText("WiFi Connected");
}


float readVoltage(int pin) {
  return analogRead(pin) * 3.3 / 4095.0;
}

float readPH() {
  float v = readVoltage(PH_PIN);
  return 7 + ((2.5 - v) / 0.18);
}

float readTDS() {
  float v = readVoltage(TDS_PIN);
  return v * 500;
}

float readOptical() {
  digitalWrite(S2, LOW);
  digitalWrite(S3, LOW);
  delay(5);
  return pulseIn(OPT_OUT, LOW);
}

void showValues(float ph, float tds, float opt) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,0);

  display.println("HERBAL SENSOR NODE");
  display.println("-----------------");
  display.print("pH: "); display.println(ph,2);
  display.print("TDS: "); display.println(tds,1);
  display.print("Opt: "); display.println(opt,0);

  display.display();
}

void showText(String txt){
  display.clearDisplay();
  display.setCursor(0,25);
  display.println(txt);
  display.display();
}


void sendData(float ph, float tds, float opt){
  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"ph\":" + String(ph) + ",";
    json += "\"tds\":" + String(tds) + ",";
    json += "\"optical\":" + String(opt);
    json += "}";

    http.POST(json);
    http.end();
  }
}

void loop() {
  float ph = readPH();
  float tds = readTDS();
  float opt = readOptical();

  Serial.printf("pH: %.2f | TDS: %.1f | OPT: %.0f\n", ph, tds, opt);

  showValues(ph, tds, opt);
  sendData(ph, tds, opt);

  delay(3000);   
}
