
#include <Arduino.h>
#include <stdint.h>
#include "LIGHT.h"
#include "DOOR.h"
#include "SPOUT.h"
#include "VIBRATION_MOTOR.h"

//#define COMMAND_BUFFER_SIZE 30
//char commandBuffer[COMMAND_BUFFER_SIZE];

//contant and variable intializations
const long baudrate = 9600;
const int doorR = 4; //right door (output)
const int doorL = 5; //left door (output)
const int solR = 2; //right solenoid (output)
const int solL = 3; //left solenoid (output)
const int toneHF = 7; //3.5kHz tone (output)

const int lightPin = 6; //houselight (output)
const int senR = 9; //right sensor (input)
const int senL = 8; //left sensor (input)
const int senI = 12; //sensor for trial-initation port (input) -> may need to change pin

const int vbmPin = 10; //vibration motor pin (output, must be pwm)

DOOR right_door(doorR); //door class for right door
DOOR left_door(doorL); //door class for left door
SPOUT right_spout(solR); //water reward class for right spout
SPOUT left_spout(solL); //water reward class for left spout
LIGHT house_light(lightPin); //light class for house light

VIBRATION_MOTOR vibration_stimulus(vbmPin);

int senStateL = 0;  //initialize sensor states (high or low)
int senStateR = 0;
int senStateI = 0; 
unsigned long startSession; //initialize zero point for session
unsigned long startWait = 0.0;  //initialize zero point for trial response
unsigned long responseT;
unsigned long runTime =  3600000; //length of session (msec)
unsigned long responseTime = 10000; //unforced trial response time (msec)
unsigned int initiationTime = 10000; //time allowed for rat to initiate trial by nose-poking trial-initialization port (msec)
unsigned int initiationHoldTime = 500; //length of time rat must nose-poke to initiate trial (msec)
unsigned int startStimDelay = 300; //delay to deliver stimulus once initiation nose-poke is made (msec)
int stimStartCheck = 0; //flag to indicate whether stimulus was started
unsigned long initiateWait = 0.0 //initialize zero point for trial initiation
unsigned long initiateHoldWait = 0.0 //initialize zero point for holding nose-poke for trial initiation
unsigned long initiateT;
//unsigned int unresponsive = 0; //initialize check for non-response trial
int delayL = 21;//29;//28;//30;//15; //left water reward time (msec)
int delayR = 23;//27;//13; // right water reward time (msec) 
int readDelay = 10; //delay between reading matlab serial port data (msec)

int vibrationLevelL = 150; // value between 0 and 255 for level of vibration (left port, for discrimination)
int vibrationLevelR = 100; // value between 0 and 255 for level of vibration (right port, for discrimination)

int vibrationLength = 2000; // length of vibration stimulus (msec)

unsigned int b = 0; //tell if loop was broken
unsigned int holdSuccess = 0 //flag for rat making trial-initiation nose-poke for initiateHoldTime msec

int maxE = 1; //consecutive error
int fcheck = 1; //setting for forced and repeated trials (1 for forced and repeat, 0 for no forced or repeat)
int acheck = 1; //setting for alternating port session (1 for port randomizing, 2 for initial training/alternating ports)
int dcheck = 0; //setting for auditory detection (0) or discrimination (1)
//event counters
int U = 0; //number of non-responses
int R = 0; //number of right port responses
int L = 0; //number of left port responses
int T = 0; //total responses (L+R)
int N = 0; //total trials (L+R+U)
int C = 0; //correct responses
int I = 0; //incorrect responses
int E = 0; //consequtive incorrect responses
int F = 0; //forced trial 
int n = 1; // trial number
float P = 0.0;
int A = 0; //trial type for saving data (1,2)
int B = 0; //left (1), right (2) or unresponsive (5) beam break;
int M = 0; //forced (1) or unforced (0) trial


int trialType[6] = {1,2,1,2,1,2};//{1,2,1,2,1,1};//{1,1,1,1,2,1};// //left port (1) or right port (2) trial
const int nT = sizeof(trialType)/sizeof(trialType[0]);
int entryT = 0; //trialType index
int setTrial; //variable for chosen trial from trialType[entryT]

//------------------------------MAIN------------------------------
void setup() {
  setPINS();
  house_light.setUp();
  right_door.setUp();
  left_door.setUp();
  right_spout.setUp(delayR);
  left_spout.setUp(delayL);
  vibration_stimulus.setUp(vibrationLevelL, vibrationLength);
  
  Serial.begin(baudrate);
  randomSeed(analogRead(0));

  Serial.flush();
  Serial.print("Connected,");
  manualControl();
  startSession = millis();
  Serial.print("Start,");
  Serial.println(startSession);
  delay(100);
    
  serial_flush_buffer();
  if(acheck == 1){  
    shuffleArray(trialType,nT);
  }
  setTrial = trialType[entryT];
}

void loop() {
  
//-------------------------TRIAL BEGINS---------------------------

  Serial.print("Trial,");
  Serial.print(millis()-startSession);
  Serial.print(",");
  Serial.println(n);
  delay(100);
  Serial.print("Type,");
  Serial.print(setTrial);
  if (E == maxE && fcheck == 1){
    Serial.println(",1");
  }
  else{
    Serial.println(",0");
  }
  delay(500);

  if(setTrial == 1){
    A = 1;
    if(E == maxE && fcheck == 1){
      Serial.println("Forced Left Trial");
      //stim(A);
      //left_door.OPEN();
    }
    else{
     Serial.println("Left Port Trial");
     //house_light.ON();
     //stim(A);
     
     right_door.OPEN();
     //delay(5);
     //left_door.OPEN();
    }
  }
  else if(setTrial == 2){
    A = 2;
    if(E == maxE && fcheck == 1){
      Serial.println("Forced Right Trial");
      //house_light.ON();
      //stim(A);
      //right_door.OPEN();
    }
    else{
      Serial.println("Right Port Trial");
      //house_light.ON();
      //stim(A);
      //right_door.OPEN();
      //delay(5);
      //left_door.OPEN();
    }
  }

  //---------------Trial Initiation-----------------------------------//
  house_light.ON();
  initiateWait = millis();
  while(digitalRead(senI) == HIGH && millis()-initiateWait <= initiationTime) { //timer for initiating trial

  }
  
  senStateI = digitalRead(senI);
  initiateT = millis();

  if (senStateI == LOW){ //rat poked trial-initiation port
    initiateHoldWait = millis();
    holdSuccess = 1;
    stimStartCheck = 0;
    while (millis() - initiateHoldWait <= initiationHoldTime){ // time holding nose-poke
      if (difigtalRead(senStateI) == HIGH) { // rat removed nose
        holdSuccess = 0;
        break;
      }
      if (millis() - initiateHoldWait >= stimStartTime && stimStartCheck == 0){
        Serial.print("Stim,");
        Serial.println(setTrial);
        if(dcheck == 0 && acheck == 1){ // detection
          if(stimType == 1){
            vibration_stimulus.ON();//playTone(toneDurationL);
          }
        }
        else if(dcheck == 1 && acheck == 1){ //discrimination
          if(stimType == 1){ //left port stim
          // playTone(toneDurationL);
          }
          else if(stimType == 2){ //right port stim
            //playTone(toneDurationR);
          }
        }
        stimStartCheck = 1;

        //stim(setTrial);
      }

    }


    if (holdSuccess){ //successfully poke long enough to initiate trial
      opendoors
      //while (vibration_motor.getRunTime() <= vibrationLength){

      //}
      //vibration_motor.OFF();
    }
    else{ //trial initialization failure (rat didn't nose-poke long enough)
      if (vibration_stimulus.isRunning()){
        vibration_stimulus.OFF();
      }
    }
  }
  else { // trial initialization timeout

  }

 
  
  
//------------------------WAIT FOR SENSOR INPUT--------------
  startWait = millis();
  Serial.println("Wait for Response");

//--------------------------FORCED TRIAL---------------------
  if(E == maxE && fcheck == 1){
    F++;
    if(setTrial == 1){


      while(digitalRead(senL) == HIGH && b == 0){
        handleVibrationStimulus();
          if(Serial.available() > 0){
            manualControl();
          }
        if(millis()-startSession > runTime){
          b = 1;
          break;
        };
      }
      stopVibrationSafe();
      responseT = millis();
      if(b == 1){
        T = L + R;
        N = L + R + U;
        P = C/(T-F);
        left_door.CLOSE();
        house_light.OFF();
        endSession();
      }
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(setTrial);
      Serial.println(",5");
      left_spout.deliverReward();
      shortTone();
      L++;
      B = 1;
      E = 0;
      delay(500);
      delay(5500);
      left_door.CLOSE();    //close door
    }
    else if(setTrial == 2){
    
      while(digitalRead(senR) == HIGH && b == 0){
        handleVibrationStimulus();
          if(Serial.available() > 0){
            manualControl();
          }
        if(millis()-startSession > runTime){
          b = 1;
          break;
        }
      }
      stopVibrationSafe();
      responseT = millis();
      if(b == 1){
        T = L + R;
        N = L + R + U;
        P = C/(T-F);
        right_door.CLOSE();
        house_light.OFF();
        endSession();
      }
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(setTrial);
      Serial.println(",5");
      right_spout.deliverReward();
      shortTone();
      R++;
      B = 2;
      E = 0;
      delay(500);
      delay(5500);
      right_door.CLOSE();     //close door  
    }
  }
  
//--------------------------UNFORCED TRIAL------------------------
  else{

    while(digitalRead(senL) == HIGH && digitalRead(senR) == HIGH && millis()-startWait <= responseTime){
      handleVibrationStimulus();
    }
    stopVibrationSafe();
    responseT = millis();
    senStateL = digitalRead(senL);
    senStateR = digitalRead(senR);
    
    if(senStateL == LOW){
      B = 1;
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(B);
      if(setTrial == 1){
        left_spout.deliverReward();//deliverReward(solL);
        shortTone();
        L++;
        C++;
        Serial.println(",1");
        E = 0;
        delay(4000);
      }
      else{
        longTone();
        L++;
        I++;
        if(fcheck == 1){
          E++;
        }
        Serial.println(",0");
      }
    }
    else if(senStateR == LOW){
      B = 2;
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(B);

      if(setTrial == 1){
        longTone();
        R++;
        I++;
        if(fcheck == 1){
          E++;
        }
        Serial.println(",0");
      }
      else{
        right_spout.deliverReward();//deliverReward(solR);
        shortTone();
        R++;
        C++;
        Serial.println(",1");
        E = 0;
        delay(4000);
      }
    }
  else{
      B = 5;
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(B);
      Serial.println(",5");
      longTone();
      //unresponsive = 0;
      U++;
      if(fcheck == 1){
        E++;
      }
    }
    delay(1000);
    left_door.CLOSE();//digitalWrite(doorR,HIGH);
    right_door.CLOSE();//digitalWrite(doorL,HIGH);
  }


// next trial chosen  
  /*if(E == 0 || fcheck == 0){ //consecutive error is zero or forced trial off, continue through array
    entryT++;
    if(entryT > 3){         //reshuffle array if all values have been used
      if(acheck == 1){
        shuffleArray(trialType,nT);
      }
      entryT = 0;
      setTrial = trialType[entryT];
    }
    else{
      setTrial = trialType[entryT];
    }
  }
  else{  //repeat same trial on errors
    setTrial = setTrial;
  }*/
  if(fcheck == 0){ //forced trial off
    entryT++;
    if(entryT > 5){
      if(acheck == 1){
        shuffleArray(trialType,nT);
      }
      //Serial.println("Reshuffle");
      //for(int i = 0; i <= 3;i++){
        //Serial.println(trialType[i]);
      //}
      entryT = 0;
    }
    setTrial = trialType[entryT];
    //Serial.println(entryT);
    //Serial.println(setTrial);
  }
  else if(fcheck == 1){ //forced trial on
    //Serial.print("E = ");
    //Serial.println(E);
    if(E == 0){
      
      entryT++;
      if(entryT > 5){
        if(acheck == 1){ //alternating ports off, shuffle array, else start at beginning
          shuffleArray(trialType,nT);
        }
        //Serial.println("Reshuffle");
        entryT = 0;
      }
    }
    setTrial = trialType[entryT];
  }  
  
//adds trial counters
  T = L + R;
  N = L + R + U;
  if(T-F == 0){
    P = 0.0;
  }
  else{
    P =(float)C/((float)T-(float)F);
     
  }
  Serial.print("Percent,");
  Serial.println(P);
/*  if(P > 0.65 && P <= 0.80){
    maxE = 2;
  }
  if(P > 0.80){
    maxE = 3; 
  }*/
  n++;

  delay(500);
  house_light.OFF(); //digitalWrite(light,HIGH);                 //houselight off
  if(millis()-startSession > runTime){
    endSession();
  }
  //pauseCheck();
  if(Serial.available() > 0){
    manualControl();
  }
  delay(1000);
}


//-----------------functions-----------------------------
//intializes pin modes and states


/*void shuffleArray(int * array, int arrSize)
{
  randomSeed(analogRead(0));
  int last = 0;
  int temp = array[last];
  for (int i=0; i<arrSize; i++)
  {
    int index = random(arrSize);
    array[last] = array[index];
    last = index;
  }
  array[last] = temp;
}*/

void shuffleArray(int * array, int arrSize){ 

  randomSeed(analogRead(0));
  int last = 0;
  int temp = array[last];
  int prevarr[arrSize];
  for (int i=0; i<arrSize; i++){
    prevarr[i] = array[i];
  }
  Serial.print("Prev arr: ");
  for (int i=0; i<arrSize; i++){
    Serial.print(prevarr[i]);
  }
  bool flag = true;
  while(flag==true){
    for (int i=0; i<arrSize; i++)
    {
      int index = random(arrSize);
      // Serial.print(index);
      array[last] = array[index];
      last = index;
    }
    Serial.println();
    array[last] = temp;
    // flag=false;
    
    for (int i=0;i<arrSize; i++)
    { 
      if(prevarr[i]!=array[i]){
      flag= false;
      Serial.print("Final arr: ");
      for (int i=0; i<arrSize; i++)
        {  Serial.print(array[i]);
        }
       
      break;
      }
      Serial.println();
    } 

  }
 Serial.println();
}

int flushWater(int s){
  int i = 0;
  pinMode(s,OUTPUT);
  digitalWrite(s,HIGH);
  while(i < 1){
  digitalWrite(s,LOW);
  delay(2000);
  digitalWrite(s,HIGH);
  delay(500);
  i++;
  }
  return(i);
}


void setPINS(){
  //pinMode(doorR,OUTPUT);
  //pinMode(doorL,OUTPUT);
  //pinMode(solL,OUTPUT);
  //pinMode(solR,OUTPUT);
  pinMode(senL,INPUT_PULLUP);
  pinMode(senR,INPUT_PULLUP);
  pinMode(toneHF,OUTPUT);
  //pinMode(light,OUTPUT);
  //digitalWrite(doorR,LOW);
  //digitalWrite(doorL,LOW);
  digitalWrite(solL,LOW);
  digitalWrite(solR,LOW);
  digitalWrite(toneHF,LOW);
  //digitalWrite(light,LOW);
  delay(1000);
}

void stim(int stimType){
  delay(1000);
  Serial.print("Stim,");
  Serial.println(stimType);
  if(dcheck == 0 && acheck == 1){ // detection
    if(stimType == 1){
      vibration_stimulus.RUN();//playTone(toneDurationL);
    }
    else {
      delay(2000);
    }
  }
  else if(dcheck == 1 && acheck == 1){ //discrimination
    if(stimType == 1){ //left port stim
     // playTone(toneDurationL);
    }
    else if(stimType == 2){ //right port stim
      //playTone(toneDurationR);
    }
  }
  delay(500);
  
}

void playTone(int toneDuration){
  digitalWrite(toneHF, HIGH);
  delay(toneDuration);
  digitalWrite(toneHF, LOW);
  if(toneDuration < 2000){ // this makese the time block where stimulus occurs to take 2seconds in total if the stimulus duration is less than 2 seconds
    delay(2000-toneDuration);
  }
}

//short tone
void shortTone(){
  digitalWrite(toneHF,HIGH);
  delay(100);
  digitalWrite(toneHF,LOW);
}

//long tone
void longTone(){
  digitalWrite(toneHF,HIGH);
  delay(1000);
  digitalWrite(toneHF,LOW);
}

void endTone(){
  for (int p = 1; p < 4; p++){
    digitalWrite(toneHF,HIGH);
    delay(100);
    digitalWrite(toneHF,LOW);
    delay(500);
  }
}

//when called (i.e. when session time reaches runTime), 
//initiates empty endless while loop  
void endSession(){
  unsigned long msec = millis() - startSession;
  //unsigned long sec = msec / 1000;
  //unsigned long mins = sec / 60;
  endTone();
  Serial.print("End,");
  Serial.println(msec);
  manualControl();

}

void serial_flush_buffer(){
  while(Serial.available()){
    Serial.read(); 
  }
}

void manualControl(){
  int ch = 0;
  //volatile unsigned long pt0;
  Serial.println("Wait");
      while(ch == 0){
        if(Serial.available() > 0){
          int fbyte = Serial.read();
          switch(fbyte){
            
            case 'b': { //begin session (exit setup loop)
              left_door.CLOSE();
              right_door.CLOSE();
              left_spout.OFF();
              right_spout.OFF();
              house_light.OFF();
              Serial.println("Begin");
              serial_flush_buffer();
              ch = 1;
              break;  
            }         
            case 'L': { //manual left port flush
              
              if(left_door.getDoorState() == LOW){
                Serial.println("Left door not opened.");
                //left_door.OPEN();
                //delay(500);
              }
              else {
                Serial.print("Left Port: ");
                delay(readDelay);
                uint8_t state = Serial.read();
                switch (state) {
                  case '1':
                    left_spout.flushWater();
                    break;

                  case '0':
                    left_spout.OFF();
                    Serial.println("Water flushed.");
                    break;
                }
                
                
              }
              break;
            }
            case 'R': { //manual right port flush
              //Serial.print("Right Port: ");
              if(right_door.getDoorState() == LOW){
                Serial.println("Right door not opened.");
                //right_door.OPEN();
                //delay(500); 
              }
              else {
                Serial.println("Right port: ");
                delay(readDelay);
                uint8_t state = Serial.read();
                switch (state) {
                  case '1': 
                    right_spout.flushWater();
                    break;

                  case '0':
                    right_spout.OFF();
                    Serial.println("Water flushed.");
                    break;
                }
                
              }
                         
              break;
            }
            case 'l': { //deliver reward from left spout
              if(left_door.getDoorState() == LOW){
                left_door.OPEN();
                delay(500);
              }
              left_spout.deliverReward();
              break;
            }
            case 'r': { //deliver reward from right spout
              if(right_door.getDoorState() == LOW){
                right_door.OPEN();
                delay(500);
              }
              right_spout.deliverReward();
              break;
            }
            case 'D': {
              delay(readDelay);
              uint8_t state = Serial.read();
              //state = Serial.read();
              //Serial.println(state);
              switch (state) {
                case '1': {
                  if(left_door.getDoorState() == LOW){
                    left_door.OPEN();
                    Serial.println("Left Door Opened.");
                  }
                  break;
                }
                case '0': {
                  left_door.CLOSE();
                  Serial.println("Left Door Closed.");
                  break;
                }
              
              /*if(left_door.getDoorState() == LOW){
                left_door.OPEN();
                Serial.println("Left Door Opened.");
              }
              else{
                left_door.CLOSE();
                Serial.println("Left Door Closed.");
              }*/
              
              }
              break;
            }
            case 'd': {
              delay(readDelay);
              uint8_t state = Serial.read();
              switch (state) {
                case '1': {
                  if(right_door.getDoorState() == LOW){
                    right_door.OPEN();
                    Serial.println("Right Door Opened.");
                  }
                  break;
                }
                case '0': {
                  right_door.CLOSE();
                  Serial.println("Right Door Closed.");
                  break;
                }
              }
              break;
              /*if(right_door.getDoorState() == LOW){
                right_door.OPEN();
                Serial.println("Right Door Opened.");
              }
              else{
                right_door.CLOSE();
                Serial.println("Right Door Closed.");
              }
              break;*/
            }
            case 'H': { //House light
              delay(readDelay);
              uint8_t state = Serial.read();
              switch (state) {
                case '1':
                  house_light.ON();
                  Serial.println("House Light On.");
                  break;
                
                case '0':
                  house_light.OFF();
                  Serial.println("House Light Off.");
                  break;
              }
              break;
            }

            case 'S': { // test vibration stimulus at currently set parameters
              //Serial.println("Delivering stimulus...");
              vibration_stimulus.RUN();
              //Serial.println("Stimulus delivered.");
              break;

              
            }
            case 'B': {
              delay(readDelay);
              uint8_t bCom = Serial.read();
              switch (bCom){
                case '0':
                  Serial.println("Playing left port tone...");
                  //playTone(toneDurationL);
                  shortTone();
                  Serial.println("Tone complete.");
                  break;

                case '1':
                  Serial.println("Playing right port tone...");
                  //playTone(toneDurationR);
                  longTone();
                  Serial.println("Tone complete.");
                  break;
              }
              break;
            }    
            case 'J': {//test sensors for reward delivery
              bool test_sensor_flag = true;
              serial_flush_buffer();
              right_door.OPEN();
              left_door.OPEN();
              Serial.println("Testing Ports...");
              delay(250);
              while(test_sensor_flag){
                if (digitalRead(senL) == LOW){
                  Serial.println("Left port poke.");
                  left_spout.deliverReward();
                  delay(1000);
                }
                else if (digitalRead(senR) == LOW){
                  Serial.println("Right port poke.");
                  right_spout.deliverReward();
                  delay(1000);
                }
                if (Serial.available() > 0) {
                  byte jbyte = Serial.read();
                  switch (jbyte) {
                    case 'K':
                      test_sensor_flag = false;
                      break;

                    case 'D':
                      if (left_door.getDoorState() == LOW) {
                        left_door.OPEN();
                      }
                      else {
                        left_door.CLOSE();
                      }
                      break;
                    
                    case 'd':
                      if (right_door.getDoorState() == LOW) {
                        right_door.OPEN();
                      }
                      else {
                        right_door.CLOSE();
                      }
                      break;

                    case 'L':
                      left_spout.deliverReward();
                      Serial.println("Left port reward deliverd.");
                      serial_flush_buffer();
                      break;

                    case 'R':
                      right_spout.deliverReward();
                      Serial.println("Right port reward deliverd.");
                      serial_flush_buffer();
                      break;
                    
                    default:
                      serial_flush_buffer();
                      break;
                  }
                }
              }
              Serial.println("End port test.");
              break;
            }
            case 'C': {
              delay(readDelay);
              int portVal;
              int testNum;
              int testDelay;
              portVal = Serial.parseInt();
              delay(readDelay);
              testNum = Serial.parseInt();
              delay(readDelay);
              testDelay = Serial.parseInt();

              if(portVal == 1){
                left_spout.calibrateReward(portVal, testNum, testDelay);
              }
              else{
                right_spout.calibrateReward(portVal, testNum, testDelay);
              }
              break;
            }
            case 'P': {//sets various parameters
              delay(readDelay);
              uint8_t p_select;
              p_select = Serial.read();
              //Serial.print("Here ");
              //Serial.println(p_select);
              delay(readDelay);
              Serial.print("SET,");
              switch(p_select){

                case '1': //change session length (ex: "P155" sets session length to 55min)
                  runTime = Serial.parseInt() * 60000;
                  Serial.print("session_length,");
                  Serial.print(runTime/60000);
                  Serial.println("min");
                  break;

                case '2': //change response time (ex: "P215" sets response time to 15sec)
                  responseTime = Serial.parseInt() * 1000;
                  Serial.print("response_time,");
                  Serial.print(responseTime/1000);
                  Serial.println("sec");
                  break;

                case '3': //change consecutive error (ex: "P32" changes consecutive error to 2)
                  maxE = Serial.parseInt();
                  Serial.print("consecutive_error,");
                  Serial.println(maxE);
                  break;

                case '4': //enable or disable alternating ports (disable: "P41", enable: "P42")

                  acheck = Serial.parseInt();
                  acheck = constrain(acheck, 1, 2);
                  Serial.print("session_type,");
                  //Serial.print(acheck);
                  //Serial.print(",");
                  //if (acheck == 1) {
                  //  Serial.println("Auditory Experiment");
                  //}
                  //else if (acheck == 2) {
                  
                  //}
                  Serial.println((acheck == 1) ? "Vibration Experiment" : "Initial Training");
                  //if(acheck == 1){
                  //  Serial.println("Alternating ports disabled.");
                  //}
                  //else if(acheck == 2){
                  //  Serial.println("Alternating ports enabled.");
                  //}
                  break;

                case '5': //enable or disable forced trials (disable: "P50", enable: "P51")
                  fcheck = Serial.parseInt();
                  fcheck = constrain(fcheck, 0, 1);
                  Serial.print("forced_trials,");
                  //Serial.print(fcheck);
                  //Serial.print(",");
                  Serial.println(fcheck ? "Enabled" : "Disabled");
                  //if(fcheck == 0){
                  //  Serial.println("Forced trials disabled.");
                  //}
                  //else if(fcheck == 1){
                  //  Serial.println("Forced trials enabled.");
                  //}
                  break;

                case '6': //set detection ("P60") or discrimination ("P61")
                  dcheck = Serial.parseInt();
                  dcheck = constrain(dcheck, 0, 1);
                  Serial.print("experiment_type,");
                  Serial.println(dcheck ? "Discrimination" : "Detection");
                  //if(dcheck == 0){
                  //  Serial.println("Detection experiment selected");
                  //}
                  //else if(dcheck == 1){
                  //  Serial.println("Discrimination experiment selected");
                  //}
                  break;

                case '7': //set vibration level of stimulus for left port (ex: "P7200")
                  vibrationLevelL = Serial.parseInt();
                  //Serial.print("Left port ");
                  vibration_stimulus.setPWM(vibrationLevelL);
                  Serial.print("vibration_level,");
                  Serial.println(vibrationLevelL);
                  //Serial.println("msec.");
                  break;

                case '8': //set vibration level of stimulus for right port (ex: "P8100")
                  vibrationLevelR = Serial.parseInt();
                  //Serial.print("Right port ");
                  vibration_stimulus.setPWM(vibrationLevelR);
                  Serial.print("vibration_levelR,");
                  Serial.println(vibrationLevelR);
                  //Serial.println("msec.");
                  break;

               case '9': //set vibration length of stimulus
                  vibrationLength = Serial.parseInt();
                  Serial.print("vibration_length,");
                  vibration_stimulus.setDelay(vibrationLength);
                  Serial.print(vibrationLength);
                  Serial.println("msec.");
                  break;
                  
                
                  
              }
              break;
              
            }
            case 'G': {//get various parameters and session data
              delay(readDelay);
              uint8_t g_select;
              g_select = Serial.read();
              switch(g_select){

                case '1': //get session length ("G1")
                  Serial.print("GET,session_length,");
                  Serial.println(runTime / 60000);
                  
                  //Serial.println("min.");
                  break;

                case '2': //get response time ("G2")
                  Serial.print("GET,response_time,");
                  Serial.println(responseTime / 1000);
                  //Serial.println("sec.");
                  break;

                case '3': //get max consecutive error ("G3")
                  Serial.print("GET,consecutive_error,");
                  Serial.println(maxE);
                  break;

                case '4': //get alternating ports setting ("G4")
                  Serial.print("GET,session_type,");
                  Serial.println((acheck == 1) ? "Vibration Experiment" : "Initial Training");
                  //if(acheck == 1){
                    //Serial.println("Alternating ports is enabled.");
                    
                  //  Serial.println("Initial Training");
                  //}
                  //else if(acheck == 2){
                    //Serial.println("Alternating ports is disabled.");
                  //  Serial.print("GET,session_type,");
                  //  Serial.println("Auditory Experiment");
                  //}
                  break;

                case '5': //get force trials setting ("G5")
                  Serial.print("GET,forced_trials,");
                  if(fcheck == 0){
                    Serial.println("No");
                    //Serial.println("Forced trials are disabled.");
                  }
                  else if(fcheck == 1){
                    Serial.println("Yes");
                    //Serial.println("Forced trials are enabled.");
                  }
                  break;

                case '6': //get experiment type: auditory detection (0) or discrimination (1)
                  Serial.print("GET,experiment_type,");
                  Serial.println(dcheck ? "Discrimination" : "Detection");
                  break;

                case '7': //left port vibration level
                  Serial.print("GET,vibration_levelL,");
                  Serial.println(vibrationLevelL);
                  break;

                case '8': //right port vibration level
                  Serial.print("GET,vibration_levelR,");
                  Serial.println(vibrationLevelR);
                  break;

                case '9': // vibration length
                  Serial.print("GET,vibration_length,");
                  Serial.println(vibrationLength);
                  break;
              }
              break;
            }
            case 'p': {
              //pt0 = millis();
              Serial.println("Paused");
              break;
            }
            case 'u': {
              ch = 1;
              Serial.println("Unpaused");
              serial_flush_buffer();
              break;
            }
            case 'Q': { 
              endSession();
              break;
            }

            default: {
              Serial.println(fbyte);
              break;
            }
      }
    }
  }
}

void handleVibrationStimulus(){
  if (vibration_stimulus.isRunning()){
    if (vibration_motor.getRunTime() >= vibrationLength){
      vibration_motor.OFF();
    }
  }
}

void stopVibrationSafe(){
  if (vibrtaion_stimulus.isRunning()){
    vibration_motor.OFF();
  }
}

/*void handleCommands(){
  int ch = 1;
  while (ch) {
    if (Serial.available()) {
      String inString = Serial.readStringUntil('\r\n');
      //Serial.println(sizeof(inString)/sizeof(inString[0]));
      Serial.println(commandBuffer);
      inString.toCharArray(commandBuffer, COMMAND_BUFFER_SIZE);
      commandBuffer[inString.length()] = 0;
      Serial.println(commandBuffer);
      //Serial.println(inString);
      //Serial.println(commandBuffer);
      //sizeof(trialType)/sizeof(trialType[0]);
      //Serial.println(inString[0]);
      //Serial.println(inString[1]);
      //Serial.println(sizeof(inString)/sizeof(inString[0]));
    }
  }
  
}*/
