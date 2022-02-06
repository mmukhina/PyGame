#define LED 8

const int buttonPin1 = 6;     
const int buttonPin2 = 3;
const int buttonPin3 = 4;
const int buttonPin4 = 5;

const int xPin = A1;
const int yPin = A0;
int xPos = 0;
int yPos = 0;

int buttonState1 = 0;         
int buttonState2 = 0;
int buttonState3 = 0;
int buttonState4 = 0;

char character;
String data = "";
String prev_data = "5N";

void setup() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  pinMode(buttonPin3, INPUT);
  pinMode(buttonPin4, INPUT);

  pinMode(xPin, INPUT);
  pinMode(yPin, INPUT);

  delay(1000);
  while (Serial.read() != '1'){
  }
  digitalWrite(LED, HIGH);
}

void loop() {
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  buttonState3 = digitalRead(buttonPin3);
  buttonState4 = digitalRead(buttonPin4);

  xPos = analogRead(xPin);
  yPos = analogRead(yPin);
 
  if (buttonState1 == HIGH) {
    data = '1';
  } else if (buttonState2 == HIGH) {
    data = '2';
  } else if (buttonState3 == HIGH) {
    data += '3';
   }else if (buttonState4 == HIGH) {
    data = '4';
  } else{
    data = '5';
  }

  if (xPos < 1000 and xPos > 20 and yPos < 20) {
    data += 'R';
  } else if (xPos < 1000 and xPos > 20 and yPos > 1000) {
    data += 'L';
  } else if (yPos < 1000 and yPos > 20 and xPos < 20){
    data += 'U';
  } else if (yPos < 1000 and yPos > 20 and xPos > 1000){
    data += 'D';
  } else{
    data += 'N';
  }

  if (prev_data != data){
    Serial.print(data);
    Serial.print("\n");
    prev_data = data;
  }
  
  data = "";
}
