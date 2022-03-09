/*
BSLI TOSU Full-scale 
Logs data from 3 different ICM 20948's and 2 different BMP280's in 'data.txt' file on SD Card and transfers data to Raspberry Pi 4
*/


// IMU 20948 and BMP 280
#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_Sensor.h>
#include <SD.h>
#include <SPI.h>
#include <usb_serial.h>


const int buzzerPin = 10;

// ICM 1 and 2, BMP 1 and 2, buzzer/LED
Adafruit_ICM20948 icm;
Adafruit_ICM20948 icm2;
Adafruit_BMP280 bmp;
Adafruit_BMP280 bmp2;
#define LEDPIN 0

#define button_pin 12
#define cal_time_sec 5

bool launch = false;
bool landed = false;
float p_last = 99999999;
int ascending = 0;
float launch_time;

long accelX, accelY, accelZ, current_micros; //micros overflows in 70 minutes!
// How can we fix this to prevent overflow?

float gForceX, gForceY, gForceZ, gMag, offsets[4];

long gyroX, gyroY, gyroZ;
float rotX, rotY, rotZ;

long loop_count = 0;

sensors_event_t accel, accel2;
sensors_event_t gyro, gyro2;
sensors_event_t mag, mag2;
sensors_event_t temp, temp2;

float bmp_p, bmp_t, bmp2_p, bmp2_t;


File f;

void printData();
void printDataSD();
void printSDHeader();
void logDataSD();
void logSDHeader();
void findOffsets(float * offsets);
void printOffsets(float * offsets);
void LED(int time);

void setup() {
  pinMode(LEDPIN, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  for (int i = 0; i < 40; i++) {
    //Blink for 8 seconds after power on
    LED(100);
    tone(buzzerPin, 50);
    delay(100);
    noTone(buzzerPin);
  }
  Serial.begin(115200);
  LED(5000);
  Serial.print("Initializing SD card...");

  if (!SD.begin(BUILTIN_SDCARD)) {
    Serial.println("initialization failed!");
    digitalWrite(LEDPIN, HIGH);
    tone(buzzerPin, 50);
    delay(10);
    noTone(buzzerPin);
    delay(10);
    tone(buzzerPin, 50);
    delay(10);
    noTone(buzzerPin);
    delay(10);
    tone(buzzerPin, 50);
    delay(10);
    noTone(buzzerPin);
    while (1);
  }
  Serial.println("initialization done.");
  f = SD.open("data.txt", FILE_WRITE);
  LED(100);
  tone(buzzerPin, 80);
  delay(100);
  noTone(buzzerPin);
  delay(100);
  tone(buzzerPin, 80);
  delay(100);
  noTone(buzzerPin);
  LED(100);
  delay(50);
  LED(100);
  icm.begin_I2C();
  icm2.begin_I2C(0x68);
  
  // add so changes ranges?????
  icm.setAccelRange(ICM20948_ACCEL_RANGE_16_G);
  icm.setGyroRange(ICM20948_GYRO_RANGE_2000_DPS);
  icm2.setAccelRange(ICM20948_ACCEL_RANGE_16_G);
  icm2.setGyroRange(ICM20948_GYRO_RANGE_2000_DPS);
  
  /* Default settings from datasheet. */
  // set bmp 2 to 0x77 not 0x76 !!!!!!!!
  bmp.begin();
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X16,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_1); /* Standby time. */
                  
  //need to solder ADR pin
  bmp2.begin(0x76);
  bmp2.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X16,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_1); /* Standby time. */
  printSDHeader();
  logSDHeader();
}


void loop() {
  loop_count ++;
  current_micros = micros(); //Record time 
  if (!landed) {  
      //ICM 20649
    icm.getEvent(&accel, &gyro, &temp, &mag);
    icm2.getEvent(&accel2, &gyro2, &temp2, &mag2);
    //BMP 280
    bmp_p = bmp.readPressure();
    bmp_t = bmp.readTemperature();
    // How differentiate?
    bmp2_p = bmp2.readPressure();
    bmp2_t = bmp2.readTemperature();
    logDataSD();
    printDataSD();
    if (loop_count == 100) {
      digitalWrite(LEDPIN, HIGH);
      f.flush();
      loop_count = 0;    
    }
    else if (loop_count == 50) {
      digitalWrite(LEDPIN, LOW);
    }
    if (bmp_p < p_last){
      ascending++;
    } else { 
      ascending = 0;
    }
    if (ascending > 10) {
      launch = true;
      launch_time = millis();
    }
    if (launch && ((millis() - launch_time) > 120000)) {
      landed = true;
    }
    p_last = bmp_p;
  } else {
    Serial.println("end");
    f.println("end");
    f.flush();
  }
}
void printDataSD() {
  Serial.print(current_micros, 10);
  //BMP1 280
  Serial.print(" ");
  Serial.print(bmp_p, 4);
  Serial.print(" ");
  Serial.print(bmp_t, 4);
  //icm1 20948
  Serial.print(" ");
  Serial.print(gyro.gyro.x, 10);
  Serial.print(" ");
  Serial.print(gyro.gyro.y, 10);
  Serial.print(" ");
  Serial.print(gyro.gyro.z, 10);
  Serial.print(" ");
  Serial.print(accel.acceleration.x, 10);
  Serial.print(" ");
  Serial.print(accel.acceleration.y, 10);
  Serial.print(" ");
  Serial.print(accel.acceleration.z, 10);
  //BMP2 280
  Serial.print(" ");
  Serial.print(bmp2_p, 4);
  Serial.print(" ");
  Serial.print(bmp2_t, 4);
  //icm2 20948
  Serial.print(" ");
  Serial.print(gyro2.gyro.x, 10);
  Serial.print(" ");
  Serial.print(gyro2.gyro.y, 10);
  Serial.print(" ");
  Serial.print(gyro2.gyro.z, 10);
  Serial.print(" ");
  Serial.print(accel2.acceleration.x, 10);
  Serial.print(" ");
  Serial.print(accel2.acceleration.y, 10);
  Serial.print(" ");
  Serial.print(accel2.acceleration.z, 10);
  Serial.println();
}


void logDataSD() {
  f.print(current_micros, 10);
  //BMP1 280
  f.print(" ");
  f.print(bmp_p,4);
  f.print(" ");
  f.print(bmp_t, 4);
  //icm1 20948
  f.print(" ");
  f.print(gyro.gyro.x, 10);
  f.print(" ");
  f.print(gyro.gyro.y, 10);
  f.print(" ");
  f.print(gyro.gyro.z, 10);
  f.print(" ");
  f.print(accel.acceleration.x, 10);
  f.print(" ");
  f.print(accel.acceleration.y, 10);
  f.print(" ");
  f.print(accel.acceleration.z, 10);
  //BMP2 280
  f.print(" ");
  f.print(bmp2_p,4);
  f.print(" ");
  f.print(bmp2_t, 4);
  //icm2 20948
  f.print(" ");
  f.print(gyro2.gyro.x, 10);
  f.print(" ");
  f.print(gyro2.gyro.y, 10);
  f.print(" ");
  f.print(gyro2.gyro.z, 10);
  f.print(" ");
  f.print(accel2.acceleration.x, 10);
  f.print(" ");
  f.print(accel2.acceleration.y, 10);
  f.print(" ");
  f.print(accel2.acceleration.z, 10);
  f.println();
}

void logSDHeader() {
  f.print("T+ [us] ");
  f.print("BMP280-1 Pressure [Pa] ");
  f.print("BMP280-1 Temperature [c] ");
  f.print("ICM 1 20948: ");
  f.print("X1 Rad/s ");
  f.print("Y1 Rad/s ");
  f.print("Z1 Rad/s ");
  f.print("X1 m/s^2 ");
  f.print("Y1 m/s^2 ");
  f.print("Z1 m/s^2 ");
  f.print("BMP280-2 Pressure [Pa] ");
  f.print("BMP280-2 Temperature [c] ");
  f.print("ICM 2 20948: ");
  f.print("X2 Rad/s ");
  f.print("Y2 Rad/s ");
  f.print("Z2 Rad/s ");
  f.print("X2 m/s^2 ");
  f.print("Y2 m/s^2 ");
  f.print("Z2 m/s^2 ");
  f.println();
}

void printSDHeader() {
  Serial.print("T+ [us] ");
  Serial.print("BMP280-1 Pressure [Pa] ");
  Serial.print("BMP280-1 Temperature [c] ");
  Serial.print("ICM1 20948: ");
  Serial.print("X1 Rad/s ");
  Serial.print("Y1 Rad/s ");
  Serial.print("Z1 Rad/s ");
  Serial.print("X1 m/s^2 ");
  Serial.print("Y1 m/s^2 ");
  Serial.print("Z1 m/s^2 ");
  Serial.print("BMP280-2 Pressure [Pa] ");
  Serial.print("BMP280-2 Temperature [c] ");
  Serial.print("ICM2 20948: ");
  Serial.print("X2 Rad/s ");
  Serial.print("Y2 Rad/s ");
  Serial.print("Z2 Rad/s ");
  Serial.print("X2 m/s^2 ");
  Serial.print("Y2 m/s^2 ");
  Serial.print("Z2 m/s^2 ");
  Serial.println();
}

//Calculates offsets and saves them to the input array --- NOT USED
// void findOffsets(float * offsets) {
//   float sumGMag = 0;
//   float sumXGyro = 0;
//   float sumYGyro = 0;
//   float sumZGyro = 0;
//   int iterations = (cal_time_sec * 100);
//   for (int i = 0; i < iterations; i++) {
//     recordAccelRegisters();
//     recordGyroRegisters();
//     sumGMag += gMag;
//     sumXGyro += rotX;
//     sumYGyro += rotY;
//     sumZGyro += rotZ;
//     delay(10);
//   }
//   float averageGMag = sumGMag / iterations;
//   float averageXAcc = sumXGyro / iterations;
//   float averageYAcc = sumYGyro / iterations;
//   float averageZAcc = sumZGyro / iterations;
//   offsets[0] = 1 - averageGMag;
//   offsets[1] = 0 - averageXAcc;
//   offsets[2] = 0 - averageYAcc;
//   offsets[3] = 0 - averageZAcc;
// }

void printOffsets(float * offsets) {
  Serial.print("G offset: ");
  Serial.print(offsets[0]);
  Serial.print(" X Gyro Offset: ");
  Serial.print(offsets[1]);
  Serial.print(" Y Gyro Offset: ");
  Serial.print(offsets[2]);
  Serial.print(" Z Gyro Offset: ");
  Serial.print(offsets[3]);
  Serial.println();
}

void LED(int time) {
  digitalWrite(LEDPIN, HIGH);
  delay (time);
  digitalWrite(LEDPIN, LOW);
}
