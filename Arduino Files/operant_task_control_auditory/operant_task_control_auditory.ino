
#include <Arduino.h>
#include <stdint.h>
#include "LIGHT.h"
#include "DOOR.h"
#include "SPOUT.h"

//contant and variable intializations
const long baudrate = 9600;
const int doorR = 4; //right door (output)
const int doorL = 5; //left door (output)
const int solR = 2; //right solenoid (output)
const int solL = 3; //left solenoid (output)
const int toneHF = 7; //3.5kHz tone (output)
const int toneLF = 12; //1.8kHz tone (output)
int toneL = toneHF; //tone played on left port trials (default to high frequency tone)
int toneR = toneLF; //tone played on right port trials (default to low frequencty tone), will only be used when discrimination experiment is selected

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
unsigned long toneDuration = 500; //duration of auditory stimulus (ms)
int delayL = 29;//30;//15; //left water reward time (msec)
int delayR = 32;//27;//13; // right water reward time (msec) 
int readDelay = 10; //delay between reading matlab serial port data (msec)

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
  delay(500);
  Serial.flush();
  Serial.print("Connected,");
  //Serial.println("Waiting for input...");
  delay(200);
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
     left_door.OPEN();
     //delay(10);
     right_door.OPEN();
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
      left_door.OPEN();
      //delay(10);
      right_door.OPEN();
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
    P = 0;
  }
  else{
    P =(float)C/((float)T-(float)F);
    Serial.print("Percent,");
    Serial.println(P); 
  }
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


void shuffleArray(int * array, int arrSize)
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
  pinMode(toneLF,OUTPUT);
  //pinMode(light,OUTPUT);
  //digitalWrite(doorR,LOW);
  //digitalWrite(doorL,LOW);
  digitalWrite(solL,LOW);
  digitalWrite(solR,LOW);
  digitalWrite(toneHF,LOW);
  digitalWrite(toneLF, LOW);
  //digitalWrite(light,LOW);
  delay(1000);
}

void stim(int stimType){
  delay(1000);
  Serial.print("Stim,");
  Serial.println(stimType);
  if(dcheck == 0){ // detection
    playTone(toneL);
  }
  else if(dcheck == 1){ //discrimination
    if(stimType == 1){ //left port stim
      playTone(toneL);
    }
    else if(stimType == 2){ //right port stim
      playTone(toneR);
    }
  }
  delay(1000);
  
}

void playTone(int tonePin){
  digitalWrite(tonePin, HIGH);
  delay(toneDuration);
  digitalWrite(tonePin, LOW);
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
            
            case 'b': //begin session (exit setup loop)
              left_door.CLOSE();
              right_door.CLOSE();
              left_spout.OFF();
              right_spout.OFF();
              house_light.OFF();
              Serial.println("Begin");
              serial_flush_buffer();
              ch = 1;
              break;  
                            
            case 'L':  //manual left port flush
              Serial.print("Left Port: ");
              if(left_door.getDoorState() == LOW){
                left_door.OPEN();
                delay(500);
              }
              left_spout.flushWater();
              break;
            
            case 'R':  //manual right port flush
              Serial.print("Right Port: ");
              if(right_door.getDoorState() == LOW){
                right_door.OPEN();
                delay(500); 
              }
              right_spout.flushWater();           
              break;

            case 'l': //deliver reward from left spout
              if(left_door.getDoorState() == LOW){
                left_door.OPEN();
                delay(500);
              }
              left_spout.deliverReward();
              break;

            case 'r': //deliver reward from right spout
              if(right_door.getDoorState() == LOW){
                right_door.OPEN();
                delay(500);
              }
              right_spout.deliverReward();
              break;

            case 'D':
              if(left_door.getDoorState() == LOW){
                left_door.OPEN();
                Serial.println("Left Door Opened.");
              }
              else{
                left_door.CLOSE();
                Serial.println("Left Door Closed.");
              }
              break;

            case 'd':
              if(right_door.getDoorState() == LOW){
                right_door.OPEN();
                Serial.println("Right Door Opened.");
              }
              else{
                right_door.CLOSE();
                Serial.println("Right Door Closed.");
              }
              break;

            case 'H':
              if(house_light.getLightState() == LOW){
                house_light.ON();
                Serial.println("House Light On");
              }
              else{
                house_light.OFF();
                Serial.println("House Light Off");
              }
              break;

            case 'B':
              delay(readDelay);
              int bCom;
              bCom = Serial.parseInt();
              if(bCom == 0){
                longTone();
                Serial.println("Playing long tone");
              }
              else if(bCom == 1){
                shortTone();
                Serial.println("Playing short tone");
              }
              break;
                           
            case 'J': //test sensors for reward delivery
              while(1){
                serial_flush_buffer();
                right_door.OPEN();
                left_door.OPEN();
                Serial.println("Testing Ports...");
                delay(250);
                while(1){
                  if(digitalRead(senL) == LOW){
                    Serial.println("Left port poke.");
                    left_spout.deliverReward();
                    break;
                  }
                  else if(digitalRead(senR) == LOW){
                    Serial.println("Right port poke.");
                    right_spout.deliverReward();
                    break;
                  }
                  if(Serial.available()){
                    fbyte = Serial.read();
                    break;
                  }
                }
                if(fbyte == 'K'){
                  Serial.println("End port test.");
                  break;
                }
                delay(1000);
              }
              right_door.CLOSE();
              left_door.CLOSE();
              break;

            case 'T': //manual control of tone stimulus (high frequency tone: "T0", low frequency tone: "T1")
              delay(readDelay);
              int tCom;
              tCom = Serial.parseInt();
              if(tCom == 0){
                playTone(toneHF);
                Serial.println("Playing high frequency tone.");
              }
              else if(tCom == 1){
                playTone(toneLF);
                Serial.println("Playing low frequency tone.");
              }
              break;
              

            case 'P': //sets various parameters
              delay(readDelay);
              uint8_t p_select;
              p_select = Serial.read();
              //Serial.print("Here ");
              //Serial.println(p_select);
              delay(readDelay);
              switch(p_select){

                case '1': //change session length (ex: "P155" sets session length to 55min)
                  runTime = Serial.parseInt() * 60000;
                  Serial.print("Session time set: ");
                  Serial.print(runTime/60000);
                  Serial.println("min.");
                  break;

                case '2': //change response time (ex: "P215" sets response time to 15sec)
                  responseTime = Serial.parseInt() * 1000;
                  Serial.print("Response time set: ");
                  Serial.print(responseTime/1000);
                  Serial.println("sec.");
                  break;

                case '3': //change consecutive error (ex: "P32" changes consecutive error to 2)
                  maxE = Serial.parseInt();
                  Serial.print("Consecutive error set: ");
                  Serial.println(maxE);
                  break;

                case '4': //enable or disable alternating ports (disable: "P41", enable: "P42")
                  acheck = Serial.parseInt();
                  if(acheck == 1){
                    Serial.println("Alternating ports disabled.");
                  }
                  else if(acheck == 2){
                    Serial.println("Alternating ports enabled.");
                  }
                  break;

                case '5': //enable or disable forced trials (disable: "P50", enable: "P51")
                  fcheck = Serial.parseInt();
                  if(fcheck == 0){
                    Serial.println("Forced trials disabled.");
                  }
                  else if(fcheck == 1){
                    Serial.println("Forced trials enabled.");
                  }
                  break;

                case '6': //set tone (auditory) stimulus duration in msec (ex: "P6200")
                  toneDuration = Serial.parseInt();
                  Serial.print("Tone duration set: ");
                  Serial.print(toneDuration);
                  Serial.println("msec.");
                  break;
                  
                case '7': //set detection ("P70") or discrimination ("P71")
                  dcheck = Serial.parseInt();
                  if(dcheck == 0){
                    Serial.println("Detection experiment selected");
                  }
                  else if(dcheck == 1){
                    Serial.println("Discrimination experiment selected");
                  }
                  break;
                  
              }
              break;
              

            case 'G': //get various parameters and session data
              delay(readDelay);
              uint8_t g_select;
              g_select = Serial.read();
              switch(g_select){

                case '1': //get session length ("G1")
                  Serial.print("Session length is set to: ");
                  Serial.print(runTime / 60000);
                  Serial.println("min.");
                  break;

                case '2': //get response time ("G2")
                  Serial.print("Response time is set to: ");
                  Serial.print(responseTime / 1000);
                  Serial.println("sec.");
                  break;

                case '3': //get max consecutive error ("G3")
                  Serial.print("Consecutive error is set to: ");
                  Serial.println(maxE);
                  break;

                case '4': //get alternating ports setting ("G4")
                  if(acheck == 1){
                    Serial.println("Alternating ports is enabled.");
                  }
                  else if(acheck == 2){
                    Serial.println("Alternating ports is disabled.");
                  }
                  break;

                case '5': //get force trials setting ("G5")
                  if(acheck == 0){
                    Serial.println("Forced trials are disabled.");
                  }
                  else if(acheck == 1){
                    Serial.println("Forced trials are enabled.");
                  }
                  break;
                
              }
              break;
              
            case 'p':
              //pt0 = millis();
              Serial.println("Paused");
              break;
          
            case 'u':
              ch = 1;
              Serial.println("Unpaused");
              serial_flush_buffer();
              break;

            case 'Q': 
              endSession();
              break;
            }
          }
        }
}
