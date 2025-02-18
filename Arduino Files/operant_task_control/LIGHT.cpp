//LIGHT.cpp
// Autor: J. Slack 8/8/23
// cpp file for house light control in operant chamber
#include <Arduino.h>
#include "LIGHT.h"

LIGHT::LIGHT(int pin1){
  lightPin = pin1;
  lightState = LOW;
}

void LIGHT::setUp(){
  pinMode(lightPin,OUTPUT);
  digitalWrite(lightPin,lightState);
}

void LIGHT::ON(){
  if(lightState == LOW){
    digitalWrite(lightPin,HIGH);
    lightState = HIGH;
    //Serial.println("House Light On");  
  }  
}

void LIGHT::OFF(){
  if(lightState == HIGH){
    digitalWrite(lightPin,LOW);
    lightState = LOW;
    //Serial.println("House Light Off");
  }
}

byte LIGHT::getLightState(){
  return lightState;
}
