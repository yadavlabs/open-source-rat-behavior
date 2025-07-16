//DOOR.cpp
// Author: J. Slack 8/8/23
// cpp file for door control in operant chamber
#include <Arduino.h>
#include "DOOR.h"

DOOR::DOOR(int pin1){//, String loc1){
  doorPin = pin1;
  //doorLoc = loc1;
  doorState = LOW;
}

void DOOR::setUp(){
  pinMode(doorPin,OUTPUT);
  digitalWrite(doorPin,doorState);
}

void DOOR::OPEN(){
  if(doorState == LOW){
    digitalWrite(doorPin,HIGH);
    doorState = HIGH;
    //Serial.println(String("House Light On");  
  }  
}

void DOOR::CLOSE(){
  if(doorState == HIGH){
    digitalWrite(doorPin,LOW);
    doorState = LOW;
    //Serial.println("House Light Off");
  }
}

byte DOOR::getDoorState(){
  return doorState;
}
