// LIGHT.h
// Autor: J. Slack 8/8/23
// class header file for house light control in operant chamber
#ifndef LIGHT_h
#define LIGHT_h

#include <Arduino.h>

class LIGHT{
public:
    LIGHT(int pin1);
    void setUp();
    void ON();
    void OFF();
    byte getLightState();
    //void ON_pw(int pwVal);
    //void OFF_pw();

private:
    int lightPin;
    byte lightState;
  
};

#endif
