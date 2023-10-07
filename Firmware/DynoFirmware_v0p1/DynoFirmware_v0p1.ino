//#include <ArduinoJson.h>

const byte switchPin = 10;
const byte intFallPin = 3;
const byte intRisePin = 2;
const byte rOutPin = 5;
const byte fOutPin = 6;
volatile byte state = LOW;
volatile long rDelta = 0;
volatile long fDelta = 0;
volatile long rCur = 0;
volatile long fCur = 0;
volatile long rLast = 0;
volatile long fLast = 0;
volatile long iR = 0;
volatile long iF = 0;
volatile long lVals = 999;
volatile long rOut = 0;
volatile long fOut = 0;
//volatile long valsR[1000];
//volatile long valsF[1000];


void setup() {
  Serial.begin(250000);
  pinMode(switchPin, INPUT);
  pinMode(intRisePin, INPUT);
  pinMode(intFallPin, INPUT);
  pinMode(rOutPin, OUTPUT);
  pinMode(fOutPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(intRisePin), encRise, RISING);
  attachInterrupt(digitalPinToInterrupt(intFallPin), encFall, FALLING);
}

void loop() {
  //{
    delay(2000);
//   while 
//   if (Serial.available()) {
//     String input = Serial.readStringUntil('\n');
//     StaticJsonDocument<200> doc;
//     deserializeJson(doc, input);

//     String command = doc["command"];
//     if (command == "run") {
//       StaticJsonDocument<200> response;
//       response["status"] = "success";
//       response["message"] = String(millis());
//       serializeJson(response, Serial);
//       Serial.println();
//     }else if (command == "getAll"){
//       getVals();
//       StaticJsonDocument<200> response;
//       response["therm1"] = temp1;
//       response["therm2"] = temp2;
//       response["soil1a"] = soil1a;
//       response["soil1b"] = soil1b;
//       response["soil2a"] = soil2a;
//       response["soil2b"] = soil2b;
//       serializeJson(response, Serial);
//       Serial.println();
//     }else if (command == "id"){
//       StaticJsonDocument<200> response;
//       response["id"] = "PF_DataMaker1";
//       serializeJson(response, Serial);
//       Serial.println();
//     }
//     // Add more command checks and responses here
//   }
// }
}

void encRise() {
  rCur = micros();
  rDelta = rCur - rLast;
  rOut = (rDelta * 255)/20000;
  analogWrite(rOutPin, rOut);
  rLast = rCur;
}

void encFall() {
  fCur = micros();
  fDelta = fCur - fLast;
  fOut = (fDelta * 255)/20000;
  analogWrite(fOutPin, fOut);
  fLast = fCur;
}