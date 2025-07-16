// SPOUT.h
// Author: J. Slack 8/8/23
// class header file for water reward solenoid valve control in operant chamber 
#ifndef SPOUT_h
#define SPOUT_h

#include <Arduino.h>

class SPOUT {    
public:
    SPOUT(int pin1);
    void setUp(int delayVal);
    void setDelay(int portVal, int delayVal);
    void flushWater();
    void OFF();
    void deliverReward();
    void calibrateReward(int portVal, int testNum, int testDelay);
    int getRewardNum();
    void resetRewardNum();
    
private:
    int solPin; //solenoid valve pin
    byte solState; //state of solenoid
    int delayValue; //water reward time (msec)
    int rewardNum = 0; //number of delivered rewards
    
  
};

#endif
