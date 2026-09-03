#ifndef INITIATION_SENSOR_h
#define INITIATION_SENSOR_h

#include <Arduino.h>

class INITIATION_SENSOR {    
public:
    INITIATION_SENSOR(int pin1);
    //void setUp(int delayVal);
    //void setDelay(int portVal, int delayVal);
    //void flushWater();
    //void OFF();
    //void deliverReward();
    //void calibrateReward(int portVal, int testNum, int testDelay);
    //int getRewardNum();
    //void resetRewardNum();
    
private:
    int solPin; //solenoid valve pin
    byte solState; //state of solenoid
    int delayValue; //water reward time (msec)
    int rewardNum = 0; //number of delivered rewards
    
  
};

#endif