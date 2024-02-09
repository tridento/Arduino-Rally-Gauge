# Arduino-Rally-Gauge
Lightweight Python3 utility to display car telemetry data (RBR, Dirt Rally 1/2.0, WRC7/8/9, EA Sports WRC, Project CARS 1/2) on the TM1638 LED module with Arduino.
# Prerequisites
PC with Windows 7/8/10/11 (havent tested it with xp or 95/98/nt), Arduino Leonardo (or another ATmega32u4-based Arduino board) with TM1638 LED module.
# Installation
PC: No installation required, prebuilt .exe available at Releases page  
Arduino: just update the pin values for strobe, clock and data pins, upload sketch and you are good to go (don't forget: https://github.com/rjbatista/tm1638-library)
```
TM1638 module(8, 9, 7); // data pin 8, clock pin 9 and strobe pin 7
```
# Games
## Richard Burns Rally
make sure that NGP6/7 installed and working  
RichardBurnsRally.ini:  
```[NGP]
udpTelemetry=1
udpTelemetryAddress=127.0.0.1
udpTelemetryPort=6776
physicsUpdateRate=60
```
## Dirt Rally 1/2.0
Documents\My Games\DiRT Rally\hardwaresettings:  
```
<motion_platform>
  <udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
</motion_platform>
```
## WRC 7/8/9/10/Generations
https://www.racedepartment.com/downloads/wrc-telemetry-patch.38991/

## EA Sports WRC
Put ard_g.json into Documents\My Games\WRC\telemetry\udp folder. Replace Documents\My Games\WRC\telemetry\config.json.

## Project Cars 1/2:
just enable "project cars 1" udp somewhere inside the depths of ingame settings

# Credits
Arduino part — https://github.com/Billiam/pygauge (i just have slightly modified it)

# Коротко
Спидометр/тахометр/передачепоказометр на Leonardo/TM1638. Предназначен для всеми нами любимых игр, коль скоро выяснилось, что каждая из них умеет отдавать телеметрию по UDP.
