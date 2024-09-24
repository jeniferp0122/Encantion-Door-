
#include <SPI.h>          // Communication with the Arduino microcontroller
#include <MFRC522.h>      // RFID reader module

#define SDApin 10         // SDA from the reader is connected to pin 10
#define RSTpin 9          // RST from the reader is connected to pin 9
#define redLED 5          // Red LED connected to pin 5
#define yellowLED 6       // Yellow LED connected to pin 6

MFRC522 mfrc522(SDApin, RSTpin); // Create MFRC522 instance.

void setup() {
    SPI.begin();                // Starts the SPI communication
    Serial.begin(9600);         // Serial monitor function
    mfrc522.PCD_Init();         // Initialize the RFID reader

    pinMode(redLED, OUTPUT);    // Set red LED as output
    pinMode(yellowLED, OUTPUT); // Set yellow LED as output
}

void loop() {
    if (!mfrc522.PICC_IsNewCardPresent()) {
        return;
    }

    if (!mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    String tag = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
        tag.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
        tag.concat(String(mfrc522.uid.uidByte[i], HEX));
    }
    Serial.println();

    tag.toUpperCase();

    if (tag.substring(1) == "21 F8 7C 26" || tag.substring(1) == "D3 99 12 2E") {
        digitalWrite(yellowLED, HIGH);
        delay(1500);
        digitalWrite(yellowLED, LOW);
    } else {
        digitalWrite(redLED, HIGH);
        delay(1500);
        digitalWrite(redLED, LOW);
    }

    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
}
