// VIBRATION_MOTOR.h
#ifndef VIBRATION_MOTOR_h
#define VIBRATION_MOTOR_h

#include <Arduino.h>

class VIBRATION_MOTOR {
public: 
    VIBRATION_MOTOR(int pwmPin);
    //void setTrigPin(int trigPin);
    void setUp(int pwmVal, int delayVal);
    void setPWM(int pwmVal);
    void setDelay(int delayVal);
    void RUN();
    void ON();
    void OFF();
    unsigned long getRunTime();
    byte isRunning();

private:
    int _pwmPin; //pin for vibration motor control (must be PWM: 3,5,6,9,10,11)
    //int _trigPin = 0; //optional pin for sending TTL HIGH then LOW during RUN() command
    int _pwmVal; //value between 0 and 255 for pwm
    int _delayVal; //value for length of vibration (msec)
    unsigned long _startRun;
    unsigned long _runTime; //timer for timing time between a use of ON() and OFF()
    byte runningState;

};

#endif
