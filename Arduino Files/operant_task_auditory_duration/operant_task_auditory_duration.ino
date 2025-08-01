
#include <Arduino.h>
#include <stdint.h>
#include "LIGHT.h"
#include "DOOR.h"
#include "SPOUT.h"

#define COMMAND_BUFFER_SIZE 30
char commandBuffer[COMMAND_BUFFER_SIZE];

//contant and variable intializations
const long baudrate = 9600;
const int doorR = 4; //right door (output)
const int doorL = 5; //left door (output)
const int solR = 2; //right solenoid (output)
const int solL = 3; //left solenoid (output)
const int toneHF = 7; //3.5kHz tone (output)

const int lightPin = 6; //houselight (output)
const int senR = 9; //left sensor (input)
const int senL = 8; //right sensor (input)

DOOR right_door(doorR); //door class for right door
DOOR left_door(doorL); //door class for left door
SPOUT right_spout(solR); //water reward class for right spout
SPOUT left_spout(solL); //water reward class for left spout
LIGHT house_light(lightPin); //light class for house light

int senStateL = 0;  //initialize sensor states (high or low)
int senStateR = 0;
unsigned long startSession; //initialize zero point for session
unsigned long startWait = 0.0;  //initialize zero point for trial
unsigned long responseT;
unsigned long runTime =  3600000; //length of session (msec)
unsigned long responseTime = 10000; //unforced trial response time (msec)
unsigned int unresponsive = 0; //initialize check for non-response trial
int delayL = 28;//30;//15; //left water reward time (msec)
int delayR = 32;//27;//13; // right water reward time (msec) 
int readDelay = 10; //delay between reading matlab serial port data (msec)

unsigned long toneDurationL = 500; //duration of auditory stimulus for left port (ms)
unsigned long toneDurationR = 100; //duration of auditory stimulus for right port (ms)

unsigned int b = 0; //tell if loop was broken

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
int n = 1;
float P = 0.0;
int A = 0; //trial type for saving data (1,2)
int B = 0; //left (1), right (2) or unresponsive (5) beam break;
int M = 0; //forced (1) or unforced (0) trial


int trialType[4] = {1,2,1,2}; //left port (1) or right port (2) trial
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
  
  Serial.begin(baudrate);
  randomSeed(analogRead(0));
  //delay(500);
  Serial.flush();
  Serial.print("Connected,");
  //Serial.println("Waiting for input...");
  //delay(200);
  handleCommands();
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
  //for(int i = 0;i<=3;i++){
  //  Serial.println(trialType[i]);
  //  delay(100);
  //}
  //Serial.println(entryT);
  //Serial.println(setTrial);
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
      house_light.ON();
      stim(A);
      left_door.OPEN();
    }
    else{
     Serial.println("Left Port Trial");
     house_light.ON();
     stim(A);
     
     right_door.OPEN();
     delay(5);
     left_door.OPEN();
    }
  }
  else if(setTrial == 2){
    A = 2;
    if(E == maxE && fcheck == 1){
      Serial.println("Forced Right Trial");
      house_light.ON();
      stim(A);
      right_door.OPEN();
    }
    else{
      Serial.println("Right Port Trial");
      house_light.ON();
      stim(A);
      right_door.OPEN();
      delay(5);
      left_door.OPEN();
    }
  }
  
//------------------------WAIT FOR SENSOR INPUT--------------
  startWait = millis();
  Serial.println("Wait for Response");

//--------------------------FORCED TRIAL---------------------
  if(E == maxE && fcheck == 1){
    F++;
    if(setTrial == 1){


      while(digitalRead(senL) == HIGH && b == 0){
          if(Serial.available() > 0){
            manualControl();
          }
        if(millis()-startSession > runTime){
          b = 1;
          break;
        };
      }
      responseT = millis();
      if(b == 1){
        T = L + R;
        N = L + R + U;
        P = C/(T-F);
        left_door.CLOSE();//digitalWrite(doorL,HIGH);
        house_light.OFF();//digitalWrite(light,HIGH);
        endSession();
      }
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(setTrial);
      Serial.println(",5");
      left_spout.deliverReward(); //deliverReward(solL);
      //shortTone();
      L++;
      B = 1;
      E = 0;
      delay(500);
      delay(5500);
      left_door.CLOSE();//digitalWrite(doorL,HIGH);     //close door
    }
    else if(setTrial == 2){
    
      while(digitalRead(senR) == HIGH && b == 0){
          if(Serial.available() > 0){
            manualControl();
          }
        if(millis()-startSession > runTime){
          b = 1;
          break;
        }
      }
      responseT = millis();
      if(b == 1){
        T = L + R;
        N = L + R + U;
        P = C/(T-F);
        right_door.CLOSE();//digitalWrite(doorR,HIGH);
        house_light.OFF();//digitalWrite(light,HIGH);
        endSession();
      }
      Serial.print("Response,");
      Serial.print(responseT-startWait);
      Serial.print(",");
      Serial.print(setTrial);
      Serial.println(",5");
      right_spout.deliverReward();//deliverReward(solR);
      //shortTone();
      R++;
      B = 2;
      E = 0;
      delay(500);
      delay(5500);
      right_door.CLOSE();//digitalWrite(doorR,HIGH);     //close door  
    }
  }
  
//--------------------------UNFORCED TRIAL------------------------
  else{

    while(digitalRead(senL) == HIGH && digitalRead(senR) == HIGH && millis()-startWait <= responseTime){
      
    }
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
        //shortTone();
        L++;
        C++;
        Serial.println(",1");
        E = 0;
        delay(4000);
      }
      else{
        //longTone();
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
        //longTone();
        R++;
        I++;
        if(fcheck == 1){
          E++;
        }
        Serial.println(",0");
      }
      else{
        right_spout.deliverReward();//deliverReward(solR);
        //shortTone();
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
      //longTone();
      unresponsive = 0;
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
    if(entryT > 3){
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
      if(entryT > 3){
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
    playTone(toneDurationL);
  }
  else if(dcheck == 1 && acheck == 1){ //discrimination
    if(stimType == 1){ //left port stim
      playTone(toneDurationL);
    }
    else if(stimType == 2){ //right port stim
      playTone(toneDurationR);
    }
  }
  delay(1000);
  
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
  //endTone();
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
                  left_door.CLOSE();
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
            case 'B': {
              delay(readDelay);
              uint8_t bCom = Serial.read();
              switch (bCom){
                case '0':
                  Serial.println("Playing left port tone...");
                  playTone(toneDurationL);
                  Serial.println("Tone complete.");
                  break;

                case '1':
                  Serial.println("Playing right port tone...");
                  playTone(toneDurationR);
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
                  Serial.println((acheck == 1) ? "Auditory Experiment" : "Initial Training");
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

                case '7': //set tone (auditory) stimulus duration in msec for left port (ex: "P7500")
                  toneDurationL = Serial.parseInt();
                  Serial.print("tone_duration,");
                  Serial.print(toneDurationL);
                  Serial.println("msec.");
                  break;

                case '8': //set tone (auditory) stimulus duration in msec for left port (ex: "P8100")
                  toneDurationR = Serial.parseInt();
                  Serial.print("tone_durationR,");
                  Serial.print(toneDurationR);
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
                  if(acheck == 1){
                    //Serial.println("Alternating ports is enabled.");
                    Serial.print("GET,session_type,");
                    Serial.println("Initial Training");
                  }
                  else if(acheck == 2){
                    //Serial.println("Alternating ports is disabled.");
                    Serial.print("GET,session_type,");
                    Serial.println("Auditory Experiment");
                  }
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

                case '7': //left port tone duration
                  Serial.print("GET,tone_durationL,");
                  Serial.println(toneDurationL);
                  break;

                case '8': //right port tone duration
                  Serial.print("GET,tone_durationR,");
                  Serial.println(toneDurationR);
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

void handleCommands(){
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
  
}
