#include <Arduino.h>
#include <Servo.h>

// Blynk app info
#define BLYNK_TEMPLATE_ID           "TMPL2CKx0CwnM"
#define BLYNK_TEMPLATE_NAME         "Quickstart Template"
#define BLYNK_AUTH_TOKEN            "OcGax-kct3Ktmzq3aTYigvyxSfFhxScR"
#define BLYNK_PRINT Serial
#define ESP8266_BAUD 115200

#include <SoftwareSerial.h>
#include <ESP8266_Lib.h>
#include <BlynkSimpleShieldEsp8266.h>

// wifi info
char ssid[] = "Ampharos";
char pass[] = "18015EAA86";

SoftwareSerial EspSerial(6, 7); // RX, TX
ESP8266 wifi(&EspSerial);
BlynkTimer timer;

// servo positions
#define LOW_LIM 10
#define UPP_LIM 180
#define TILT_LEFT 135
#define TILT_RIGHT 45
#define MIDDLE 93

// for ultrasonics
#define SPEED_OF_SOUND  0.0343 // cm/us
#define TRASH_DIST 25
#define RECYCLE_DIST 16.6
#define DEVIATION_TOL 3

//create servo object
Servo platformServo;

// ultrasonic range sensor signal pins
const int trig_recycle = 3;
const int echo_recycle = 2;
const int trig_trash = 5;
const int echo_trash = 4;

// FUNCTION DECLARATIONS:
void rotateServo(int target);
int getObjectID();
float measureRecycle();
float measureTrash();
// python does its own initialization in the background and gets the next image based on serial input from arduino 

void setup() {
  Serial.begin(115200);

  // begin ESP8266-01 comms
  EspSerial.begin(ESP8266_BAUD);
  delay(10);
  Blynk.begin(BLYNK_AUTH_TOKEN, wifi, ssid, pass, "blynk.cloud", 80);

  // initialize platform to middle position
  rotateServo(MIDDLE);

  // set pin I/O for ultrasonics
  pinMode(trig_recycle, OUTPUT);
  pinMode(trig_trash, OUTPUT);
  pinMode(echo_recycle, INPUT);
  pinMode(echo_trash, INPUT);
}

//0 is bg, 1 is trash, 2 is recycling
void loop() {
  // wait until an object is placed and detected -- call Python to do this
    int objectID = getObjectID();
    Serial.println(objectID);
    switch(objectID){
      case 0:
        break;
      case 1: // trash
        { 
          float trashSensor = measureTrash();
          if(trashSensor < (TRASH_DIST - DEVIATION_TOL)){
            Serial.println("TRASH FULL");
            Blynk.logEvent("trash_bin_full");
          }
          else {
            rotateServo(TILT_RIGHT);
            delay(1500);   // settling time
            rotateServo(MIDDLE);
            delay(500);   // settling time
            trashSensor = measureTrash();
            if(trashSensor < (TRASH_DIST - DEVIATION_TOL)){
              Serial.println("TRASH FULL");
              Blynk.logEvent("trash_bin_full");
            }
          }
        }
        break;
      case 2: // recycle
        {
          float recycleSensor = measureRecycle();
          if(recycleSensor < (RECYCLE_DIST - DEVIATION_TOL)){
            Serial.println("RECYCLE FULL");
            Blynk.logEvent("recycle_bin_full");
          }
          else {
            rotateServo(TILT_LEFT);
            delay(1500);   // settling time
            rotateServo(MIDDLE);
            delay(500);   // settling time
            recycleSensor = measureRecycle();
            if(recycleSensor < (RECYCLE_DIST - DEVIATION_TOL)){
              Serial.println("RECYCLE FULL");
              Blynk.logEvent("recycle_bin_full");
            }
          }
        }
        break;
      default:
        // should never be reached
        break;
    }
  delay(1000);
}


// function to slow down servo motion by commanding in increments with delays 
void rotateServo(int target) {
  // (re)initialize servo to pwm pin 9 bc this gets detached to stop motor hum
  platformServo.attach(9);
  // read starting servo position
  int pos = platformServo.read();

  // increment servo pos
  if (target > pos) {
    while (pos < target) {
      pos = pos + 1;
      platformServo.write(pos);
      pos = platformServo.read();
      delay(8);      // 8ms delay
    }
  }
  // decrement servo pos
  else if (target < pos) {
    while (pos > target) {
      pos = pos - 1;
      platformServo.write(pos);
      pos = platformServo.read();
      delay(8);      // 8ms delay
    }
  }
  // needed to hold the final position for a few ms before detaching
  platformServo.write(pos);
  delay(300);
  platformServo.detach();
  return;
}

// prompt Python script to take a picture and identify the object
int getObjectID(){
  // send a string to trigger Python function
  Serial.println("IDENTIFY OBJECT");

  // wait for Python to respond with the object name
	while (!Serial.available()) {
    Blynk.run(); // handshake with Blynk while waiting
  }
	return Serial.readString().toInt();
}

float measureRecycle() {
  // set trig low for 2 us to ensure starting in low
  digitalWrite(trig_recycle, LOW);
  delayMicroseconds(2);

  // set trigger high for 10 us, then low
  digitalWrite(trig_recycle, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_recycle, LOW);

  // time how long it takes for echo to switch from high to low
  float recycle_duration = pulseIn(echo_recycle, HIGH);

  // divide by 2 for there and back
  float recycle_distance = (recycle_duration*SPEED_OF_SOUND)/2;  

  Serial.print("Recycle Dist: ");
  Serial.println(recycle_distance);

  return recycle_distance;
}

float measureTrash() {
  // set trig low for 2 us to ensure starting in low
  digitalWrite(trig_trash, LOW);
  delayMicroseconds(2);

  // set trigger high for 10 us, then low
  digitalWrite(trig_trash, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_trash, LOW);

  // time how long it takes for echo to switch from high to low
  float trash_duration = pulseIn(echo_trash, HIGH);

  // divide by 2 for there and back
  float trash_distance = (trash_duration*SPEED_OF_SOUND)/2;  

  Serial.print("Trash Dist: ");
  Serial.println(trash_distance);

  return trash_distance;
}