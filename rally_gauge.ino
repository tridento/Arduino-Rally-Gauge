#include <TM1638.h> //https://github.com/rjbatista/tm1638-library
TM1638 module(10, 9, 8); // НЕ ЗАБУДЬ ВЫСТАВИТЬ СВОИ ЗНАЧЕНИЯ / REPLACE WITH YOUR OWN VALUES

byte blink_interval = 50;
boolean blink_on = false;
unsigned long current_millis = 0;
unsigned long previous_millis = 0;
unsigned long update_millis = 0;

word rpm_led_set [10] = {
0b00000000 | 0b00000000 << 8,
0b00000001 | 0b00000000 << 8,
0b00000011 | 0b00000000 << 8,
0b00000111 | 0b00000000 << 8,
0b00001111 | 0b00000000 << 8,
0b00011111 | 0b00000000 << 8,
0b00111111 | 0b00000000 << 8,
0b01111111 | 0b01000000 << 8,
0b11111111 | 0b11000000 << 8,
0b11111111 | 0b11111111 << 8,
};

float led_ranges[10] = {
  0.0,
  0.15,
  0.31, //16
  0.45, //14
  0.57, //12
  0.69, //10
  0.78, //09
  0.85, //07
  0.9,  //05
  0.95, //05
};

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50);
  module.setupDisplay(true, 1);
}

void loop() {
  int i;
  char buf[20];
  byte d1;
  byte d2;

  long time = millis();

  if (Serial.available() >= 10)  {
    for (i=0; i<10; i++) {
      buf[i] = Serial.read();
    }
    update_millis = time;
  } else {
    if (time - update_millis > 10000) {
      module.clearDisplay();
      module.setLEDs(rpm_led_set[0]);
    }
    return;
  }

  if(buf[5]='G'){ //передача --->
    byte gear = buf[6];
    char* n = "n";
    char* r = "r";
    if(gear == 0) module.setDisplayToString(n, 0, 7);
    if(gear == 10) module.setDisplayToString(r, 0, 7);
    if(gear>0&&gear<10) module.setDisplayDigit(gear, 7, false);
  } // <---

  if(buf[7]=='S') { //скорость --->
    for (i=0; i<3; i++) {
      module.clearDisplayDigit(i, false);
    }
    d1 = buf[8];
    d2 = buf[9];
    String speed_sym = String((d1<<8)+d2);
    module.setDisplayToString(speed_sym, 0, 0);
  } // <---

  unsigned int rpm;
  unsigned int rpmleds = 0;
  unsigned int max_rpm;
  float rpm_percent = 0;
  byte rpmdata = 0;

  if (buf[0] == 'R' ) {
    d1 = buf[1];
    d2 = buf[2];
    rpm = ((d1<<8) + d2);

    d1 = buf[3];
    d2 = buf[4];
    max_rpm = ((d1<<8) + d2);

    if (rpm && max_rpm && max_rpm > 0) {
      rpmdata=1;
    }
  }

  if (rpmdata == 1) {
    rpm_percent = rpm / (float)max_rpm;
    for(unsigned int a = 9; a >= 0; a--) {
      if (led_ranges[a] <= rpm_percent) {
        rpmleds = a;
        break;
      }
    }
    if (rpmleds == 9) {
      current_millis = time;
      if (current_millis - previous_millis > blink_interval) {
        previous_millis = current_millis;
        blink_on = !blink_on;
      }
      if (!blink_on) {
        rpmleds = 0;
      }
    }
    module.setLEDs(rpm_led_set[rpmleds]);
    rpmdata=0;
  }

}
