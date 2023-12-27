#include <Bounce2.h>

int button=2;
int LED=13;
Bounce debouncer=Bounce();

void setup() {
  pinMode(button,INPUT_PULLUP);
  pinMode(LED,OUTPUT);
  debouncer.attach(button);
  debouncer.interval(5);
  Serial.begin(9600);
  
}


void loop(){
  debouncer.update();

  if(debouncer.fell()){
    Serial.println("Released");
    digitalWrite(LED,LOW);
  }

  if(debouncer.rose()){
    Serial.println("Pressed");
    digitalWrite(LED,HIGH);
  }
}
