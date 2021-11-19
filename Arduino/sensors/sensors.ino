/*
BSLI SUBSCALE NOVEMBER 19 2021
Logs data from MPU6050, ICM 20948, BMP280 in 'data.txt' file on SD Card.
*/



#include <Arduino.h>
#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MPU6050.h>
#include <SPI.h>
#include <SD.h>

Adafruit_ICM20948 icm;
Adafruit_MPU6050 mpu;
Adafruit_BMP280 bmp;
#define LEDPIN 0
#define button_pin 12
#define cal_time_sec 5

long accelX, accelY, accelZ, current_micros; //micros overflows in 70 minutes!

float gForceX, gForceY, gForceZ, gMag, offsets[4];

long gyroX, gyroY, gyroZ;
float rotX, rotY, rotZ;

long loop_count = 0;

sensors_event_t accel;
sensors_event_t gyro;
sensors_event_t mag;
sensors_event_t temp;

sensors_event_t mpu_a, mpu_g, mpu_temp;

float bmp_p, bmp_t;


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
  for (int i = 0; i < 40; i++) {
    //Blink for 8 seconds after power on
    LED(100);
    delay(100);
  }
  Serial.begin(115200);
  LED(5000);
  Serial.print("Initializing SD card...");

  if (!SD.begin(BUILTIN_SDCARD)) {
    Serial.println("initialization failed!");
    digitalWrite(LEDPIN, HIGH);
    while (1);
  }
  Serial.println("initialization done.");
  f = SD.open("data.txt", FILE_WRITE);
  LED(100);
  delay(50);
  LED(100);
  delay(50);
  LED(100);
  mpu.begin(0x68, &Wire);
  bmp.begin();
  icm.begin_I2C();
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
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
    //ICM 20649
  icm.getEvent(&accel, &gyro, &temp, &mag);
  //MPU 6050
  mpu.getEvent(&mpu_a, &mpu_g, &mpu_temp);
  //BMP 280
  bmp_p = bmp.readPressure();
  bmp_t = bmp.readTemperature();
  logDataSD();
  printDataSD();
  f.flush();
  if (loop_count % 100 == 0) {
    LED(1);
  }
  else {
  }
}

void printDataSD() {
  Serial.print(current_micros, 10);
  //mpu 6050
  Serial.print(" ");
  Serial.print(mpu_g.gyro.x, 10);
  Serial.print(" ");
  Serial.print(mpu_g.gyro.y, 10);
  Serial.print(" ");
  Serial.print(mpu_g.gyro.z, 10);
  Serial.print(" ");
  Serial.print(mpu_a.acceleration.x, 10);
  Serial.print(" ");
  Serial.print(mpu_a.acceleration.y, 10);
  Serial.print(" ");
  Serial.print(mpu_a.acceleration.z, 10);
  Serial.print(" ");
  Serial.print(mpu_temp.temperature, 4);
  Serial.print(" ");
  Serial.print(bmp_p, 4);
  Serial.print(" ");
  Serial.print(bmp_t, 4);
  //icm 20948
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
  Serial.println();
}

void logDataSD() {
  f.print(current_micros, 10);
  //mpu 6050
  f.print(" ");
  f.print(mpu_g.gyro.x, 10);
  f.print(" ");
  f.print(mpu_g.gyro.y, 10);
  f.print(" ");
  f.print(mpu_g.gyro.z, 10);
  f.print(" ");
  f.print(mpu_a.acceleration.x, 10);
  f.print(" ");
  f.print(mpu_a.acceleration.y, 10);
  f.print(" ");
  f.print(mpu_a.acceleration.z, 10);
  f.print(" ");
  f.print(mpu_temp.temperature, 4);
  f.print(" ");
  f.print(bmp_p, 4);
  f.print(" ");
  f.print(bmp_t, 4);
  //icm 20948
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
  f.println();
}

void logSDHeader() {
  f.print("T+ [us] ");
  f.print("MPU 6050: ");
  f.print("X Rad/s ");
  f.print("Y Rad/s ");
  f.print("Z Rad/s ");
  f.print("X m/s^2 ");
  f.print("Y m/s^2 ");
  f.print("Z m/s^2 ");
  f.print("IMU Temp [c] ");
  f.print("BMP280 Pressure [Pa] ");
  f.print("BMP280 Temperature [c] ");
  f.print("ICM 20948: ");
  f.print("X Rad/s ");
  f.print("Y Rad/s ");
  f.print("Z Rad/s ");
  f.print("X m/s^2 ");
  f.print("Y m/s^2 ");
  f.print("Z m/s^2 ");
  f.println();
}

void printSDHeader() {
  Serial.print("T+ [us] ");
  Serial.print("MPU 6050: ");
  Serial.print("X Rad/s ");
  Serial.print("Y Rad/s ");
  Serial.print("Z Rad/s ");
  Serial.print("X m/s^2 ");
  Serial.print("Y m/s^2 ");
  Serial.print("Z m/s^2 ");
  Serial.print("IMU Temp [c] ");
  Serial.print("BMP280 Pressure [Pa] ");
  Serial.print("BMP280 Temperature [c] ");
  Serial.print("ICM 20948: ");
  Serial.print("X Rad/s ");
  Serial.print("Y Rad/s ");
  Serial.print("Z Rad/s ");
  Serial.print("X m/s^2 ");
  Serial.print("Y m/s^2 ");
  Serial.print("Z m/s^2 ");
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