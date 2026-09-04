// VIBRATION_MOTOR.cpp
#include <Arduino.h>
#include "VIBRATION_MOTOR.h"

VIBRATION_MOTOR::VIBRATION_MOTOR(int pwmPin){ 
    _pwmPin = pwmPin;
}

//void VIBRATION_MOTOR::setTrigPin(int trigPin){
//  _trigPin = trigPin;
//  pinMode(_trigPin, OUTPUT);
//  digitalWrite(_trigPin, LOW);
//  
//}
void VIBRATION_MOTOR::setUp(int pwmVal, int delayVal){
  _pwmVal = pwmVal;
  _delayVal = delayVal;
  pinMode(_pwmPin,OUTPUT);
  analogWrite(_pwmPin,0);
}

void VIBRATION_MOTOR::setPWM(int pwmVal){
  _pwmVal = pwmVal;
  //Serial.print("PWM level set: ");
  //Serial.println(_pwmVal);
}

void VIBRATION_MOTOR::setDelay(int delayVal){
  _delayVal = delayVal;
  //Serial.print("Delay set: ");
  //Serial.print(_delayVal);
  //Serial.println("msec");
}

void VIBRATION_MOTOR::RUN(){
//  if(_trigPin == 0){ //if trig pin isn't used
    Serial.println("Vibration starting...");
    analogWrite(_pwmPin,_pwmVal);
    delay(_delayVal);
    analogWrite(_pwmPin,0);
    Serial.println("Vibration stopped");
//  }
//  else{
//    Serial.println("Vibration starting...");
//    digitalWrite(_trigPin, HIGH);
//    analogWrite(_pwmPin,_pwmVal);
//    delay(_delayVal);
//    analogWrite(_pwmPin,0);
//    digitalWrite(_trigPin, LOW);
//    Serial.println("Vibration stopped");
//  }
}

void VIBRATION_MOTOR::ON(){
  Serial.println("Vibration on");
  runningState = 1;
  _startRun = millis();
  analogWrite(_pwmPin,_pwmVal);
}

void VIBRATION_MOTOR::OFF(){
  Serial.println("Vibration off");
  analogWrite(_pwmPin,0);
  _runTime = millis() - _startRun;
  runningState = 0;
}

int VIBRATION_MOTOR::getRunTime(){
  _runTime = millis() - _startRun;
  return _runTime;
}

byte VIBRATION_MOTOR::isRunning(){
  return runningState;
}