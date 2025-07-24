// SPOUT.cpp
// Author: J. Slack 8/8/23
// cpp file for water reward solenoid valve control in operant chamber 
#include <Arduino.h>
#include "SPOUT.h"

SPOUT::SPOUT(int pin1){
  solPin = pin1;
  solState = LOW;
}

void SPOUT::setUp(int delayVal){
  delayValue = delayVal;
  pinMode(solPin, OUTPUT);
  digitalWrite(solPin, solState);
}

void SPOUT::setDelay(int portVal, int delayVal){
  delayValue = delayVal;
  if(portVal == 1){
    Serial.print("Left ");
  }
  else{
    Serial.print("Right ");
  }
  Serial.print("port delay value set: ");
  Serial.print(delayValue);
  Serial.println("msec");
}

void SPOUT::flushWater(){
  switch(solState){
    case LOW:
      solState = HIGH;
      digitalWrite(solPin, solState);
      Serial.println("Flusing Water...");
      break;

    case HIGH:
      solState = LOW;
      digitalWrite(solPin, solState);
      Serial.println("Water Flushed.");
      break;
  }

}

void SPOUT::OFF(){
  if(solState == HIGH){
    solState = LOW;
    digitalWrite(solPin, solState);
  }
}

void SPOUT::deliverReward(){
  solState = HIGH;
  digitalWrite(solPin, solState);
  delay(delayValue);
  solState = LOW;
  digitalWrite(solPin, solState);
  rewardNum++;
}

void SPOUT::calibrateReward(int portVal, int testNum, int testDelay){
  Serial.println("Calibrating Water Selected");
  if(portVal ==1){
    Serial.println("---Testing left port----");
  }
  else{
    Serial.println("---Testing right port---");
  }
  Serial.print(testNum);
  Serial.print(" Rewards at ");
  Serial.print(testDelay);
  Serial.println("msec");
  Serial.println("Calibrating...");
  for(int i = 0;i<testNum;i++){
    digitalWrite(solPin,HIGH);
    delay(testDelay);
    digitalWrite(solPin,LOW);
    delay(100);
  }
  Serial.println("Calibration Complete");
  Serial.println("--------------------");
}

int SPOUT::getRewardNum(){
  return rewardNum;
}

void SPOUT::resetRewardNum(){
  rewardNum = 0;
}
