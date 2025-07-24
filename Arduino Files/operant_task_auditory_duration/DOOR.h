// DOOR.h
// Author: J. Slack 8/8/23
// class header file for door control in operant chamber
#ifndef DOOR_h
#define DOOR_h

#include <Arduino.h>

class DOOR{
public:
    DOOR(int pin1);//, String loc1);
    void setUp();
    void OPEN();
    void CLOSE();
    byte getDoorState();
    //void ON_pw(int pwVal);
    //void OFF_pw();

private:
    int doorPin; //digOut pin on board
    //String doorLoc; //location of door (either "Left" for left or "Right" for right)
    byte doorState; //HIGH (open) or LOW (closed)
  
};

#endif
