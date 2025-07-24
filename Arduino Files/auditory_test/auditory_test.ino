
const long baudrate = 9600;
int readDelay = 10; //delay between reading matlab serial port data (msec)

const int toneH = 7; //3.5kHz tone (output)
const int toneL = 12; //1.8kHz tone (output)
unsigned long toneDuration = 1000; //duration of auditory stimulus (ms)

void setup() {
  pinMode(toneH,OUTPUT);
  pinMode(toneL,OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(baudrate);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available() > 0){
    int comByte = Serial.read();
    switch(comByte){

      case 'H':
        digitalWrite(toneH, HIGH);
        delay(toneDuration);
        digitalWrite(toneH, LOW);
        break;

      case 'L':
        digitalWrite(toneL, HIGH);
        delay(toneDuration);
        digitalWrite(toneL, LOW);
        break;

      case 'F':
        for (int i=0;i<=10;i++){
          digitalWrite(toneH, HIGH);
          delay(5);
          digitalWrite(toneH, LOW);
          delay(95);
        }
        break;

      case 'P':
        delay(readDelay);
        uint8_t p_select;
        p_select = Serial.read();
        delay(readDelay);
        switch(p_select){

          case '1':
            toneDuration = Serial.parseInt();
            Serial.print("Tone duration set: ");
            Serial.print(toneDuration);
            Serial.println("msec.");
            break;
        }
        
    }
  }
}
