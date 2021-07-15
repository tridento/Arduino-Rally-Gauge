#include <TM1638.h>
TM1638 module(10, 9, 8);
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  module.setupDisplay(true, 1);
  module.clearDisplay();
}

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

float led_ranges[10] = { 0.0, 0.15, 0.31, 0.45, 0.57, 0.69, 0.78, 0.85, 0.9, 0.95 };
byte blink_interval = 50;
boolean blink_on = false;
unsigned long current_millis = 0;
unsigned long previous_millis = 0;
unsigned long update_millis = 0;

void loop() {
    int i;
    char bufferArray[20];
    unsigned int rpm;
    unsigned int rpmleds = 0;
    unsigned int rpmmax;
    float rpm_percent = 0;

    byte d1; byte d2; byte d3; byte d4; byte d5;
    signed short int gear;

    byte rpmdata = 0;
    byte speeddata = 0;
    byte geardata = 0;

    long time = millis();

    if (Serial.available() >= 10)  {
      for (i = 0; i < 12; i++) {
        bufferArray[i] = Serial.read();
      }
      
      update_millis = time;
    } else {
      if (time - update_millis > 10000) {
        module.clearDisplay();
        module.setLEDs(rpm_led_set[0]);
      }
      return;
    }

    if (bufferArray[0] == 'R' ) {
      d1 = bufferArray[1];
      d2 = bufferArray[2];
      rpm = ((d1 << 8) + d2);
      d1 = bufferArray[3];
      d2 = bufferArray[4];
      rpmmax = ((d1 << 8) + d2);

      if (rpm && rpmmax && rpmmax > 0) {
        rpmdata = 1;
      }
    }
    float f_carspeed;
    unsigned char speedArray[4];
    if (bufferArray[7] == 'S' ) {
      speedArray[0] = bufferArray[11]; speedArray[1] = bufferArray[10]; 
      speedArray[2] = bufferArray[9]; speedArray[3] = bufferArray[8];
      memcpy(&f_carspeed, speedArray, sizeof(float));
      speeddata = 1;
    }
    
    if (speeddata == 1) {
      char speed[20];
      dtostrf(f_carspeed, 1, 1, speed);
      module.setDisplayToString(speed,0,1);
      speeddata = 0;
    }

    if (bufferArray[5] == 'G' ) {
      gear = bufferArray[6];
      geardata = 1;
    }

    if (geardata == 1) {
      char* neutral = "n";
      char* reverse = "r";

      if (gear >= 1 and gear < 10 ) {
        module.setDisplayDigit(gear, 7, false);
      } else if (gear == 0) {
        module.setDisplayToString(neutral, 0, 7);
      } else if ((gear == 10) || (gear == -1)) {
        module.setDisplayToString(reverse, 0, 7);
      }
      geardata = 0;
    }

    if (rpmdata == 1) {
      rpm_percent = rpm / (float)rpmmax;
      for (unsigned int a = 9; a >= 0; a--) {
        if (led_ranges[a] <= rpm_percent) {
          rpmleds = a;
          break;
        }
      }
      if (rpmleds == 9) {
        current_millis = time;
        if (current_millis - previous_millis > blink_interval)
        {
          previous_millis = current_millis;
          blink_on = !blink_on;
        }
        if (!blink_on) {
          rpmleds = 0;
        }
      }
      module.setLEDs(rpm_led_set[rpmleds]);
      rpmdata = 0;
    }
  }