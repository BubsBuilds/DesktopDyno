#include <ArduinoJson.h>

const byte intFallPin = 3;
const byte intRisePin = 2;
volatile long rDelta = 0;
volatile long fDelta = 0;
volatile long rCur = 0;
volatile long fCur = 0;
volatile long rLast = 0;
volatile long fLast = 0;
volatile int iR = 0;
volatile int iF = 0;
volatile int lVals1 = 9;
volatile int lVals2 = 18;
volatile long rVals1[10];
volatile long rVals2[10];
volatile long fVals1[10];
volatile long fVals2[10];
volatile int rSendFlag = 0;
volatile int fSendFlag = 0;
int logInc = 0;


void setup() {
  Serial.begin(250000);
  pinMode(intRisePin, INPUT);
  pinMode(intFallPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(intRisePin), encRise, RISING);
  attachInterrupt(digitalPinToInterrupt(intFallPin), encFall, FALLING);
}

void loop() {
  
  if (rSendFlag == 1){
    StaticJsonDocument<1000> response;
    response["id"] = "R";
    for (int i = 0; i < lVals1; i += 1) {
      //response["rKeys1"] = rKeys1[i];
      //response["rVals1"] = rVals1[i];
      response[String(logInc)] = rVals1[i];
      logInc += 1;
    }      
    serializeJson(response, Serial);
    Serial.println();
    rSendFlag = 0;
    //delay(5);
  }else if (rSendFlag == 2){
    StaticJsonDocument<1000> response;
    response["id"] = "R";
    for (int i = 0; i < lVals1; i += 1) {
      response[String(logInc)] = rVals2[i];
      logInc += 1;
    }      
    serializeJson(response, Serial);
    Serial.println();
    rSendFlag = 0;
    //delay(5);
  }
  if (fSendFlag == 1){
    StaticJsonDocument<1000> response;
    response["id"] = "F";
    for (int i = 0; i < lVals1; i += 1) {
      response[String(logInc)] = fVals1[i];
      logInc += 1;
    }      
    serializeJson(response, Serial);
    Serial.println();
    fSendFlag = 0;
    //delay(5);

  }else if (fSendFlag == 2){
    StaticJsonDocument<1000> response;
    response["id"] = "F";
    for (int i = 0; i < lVals1; i += 1) {
      response[String(logInc)] = fVals2[i];
      logInc += 1;
    }      
    serializeJson(response, Serial);
    Serial.println();
    fSendFlag = 0;
    //delay(5);
  }
}


void encRise() {
  rCur = micros();
  if (iR < lVals1){
    rVals1[iR] = rCur;
    iR += 1;
  }else if (iR == lVals1){
    rVals2[(iR - lVals1)] = rCur;
    rSendFlag = 1;
    iR += 1;
  }else if (iR < lVals2){
    rVals2[(iR-lVals1)] = rCur;
    iR += 1;
  }else if (iR == lVals2){
    rSendFlag = 2;
    iR = 0;
  }
}

void encFall() {
  fCur = micros();
  if (iF < lVals1){
    fVals1[iF] = fCur;
    iF += 1;
  }else if (iF == lVals1){
    fVals2[(iF-lVals1)] = fCur;
    fSendFlag = 1;
    iF += 1;
  }else if (iF < lVals2){
    fVals2[(iF-lVals1)] = fCur;
    iF += 1;
  }else if (iF == lVals2){
    fSendFlag = 2;
    iF = 0;
  }
}