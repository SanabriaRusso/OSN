#include <Arduino.h>

int main(void)
{
	init();

#if defined(USBCON)
	USBDevice.attach();
#endif
	
	setup();
    
	for (;;) {
		loop();
		if (serialEventRun) serialEventRun();
	}
        
	return 0;
}

void setup();
float getAverage(int pin, int samples);
void loop();
void flashLed(int pin, int times, int wait);
#line 1 "build/arduino.ino"
#include "XBee.h"
#include "DHT.h"

#define DHTPIN 2     // data pin of the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define SOUND_SENSOR_PIN 0

// Create DHT object
DHT dht(DHTPIN, DHTTYPE);

// Create an XBee object
XBee xbee = XBee();

// we are going to send two floats of 4 bytes each
uint8_t payload[12] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

// Union to convert float to byte string
union u_tag {
    uint8_t b[4];
    float fval;
} u;


// SH + SL Address of receiving XBee
XBeeAddress64 addr64 = XBeeAddress64(0x0013A200, 0x408B3D92);
ZBTxRequest zbTx = ZBTxRequest(addr64, payload, sizeof(payload));
ZBTxStatusResponse txStatus = ZBTxStatusResponse();

int statusLed = 13;
int errorLed = 13;

void flashLed(int pin, int times, int wait)
{

    for (int i = 0; i < times; i++)
    {
        digitalWrite(pin, HIGH);
        delay(wait);
        digitalWrite(pin, LOW);

        if (i + 1 < times)
        {
            delay(wait);
        }
    }
}

float getAverage(int pin, int samples)
{
    float avg = 0.0;

    for (int i=0; i<samples; i++)
    {
        avg += analogRead(pin);
        delay(10); // safety?
    }

    return avg/samples;
}

void setup()
{
    pinMode(statusLed, OUTPUT);
    pinMode(errorLed, OUTPUT);
    dht.begin();
    xbee.begin(9600);
}

void loop()
{
    // Reading temperature or humidity takes about 250 milliseconds!
    // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float s = getAverage(SOUND_SENSOR_PIN, 10);

    // Check if returns are valid
    if (!isnan(t) && !isnan(h)) {

        // Convert humidity and temperature into a byte array and copy it into the payload array
        u.fval = h;
        for (int i=0;i<4;i++){
            payload[i]=u.b[i];
        }

        u.fval = t;
        for (int i=0;i<4;i++){
            payload[i+4]=u.b[i];
        }
        
        u.fval = s;
        for (int i=0;i<4;i++){
            payload[i+8]=u.b[i];
        }

        xbee.send(zbTx);

        // flash TX indicator
        flashLed(statusLed, 1, 100);

        // after sending a tx request, we expect a status response
        // wait up to half second for the status response
        if (xbee.readPacket(500)) {
          // got a response!

          // should be a znet tx status            	
          if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
            xbee.getResponse().getZBTxStatusResponse(txStatus);

            // get the delivery status, the fifth byte
            if (txStatus.getDeliveryStatus() == SUCCESS) {
              // success.  time to celebrate
              flashLed(statusLed, 5, 50);
            } else {
              flashLed(errorLed, 3, 500);
            }
          }
        } else if (xbee.getResponse().isError()) {
          //nss.print("Error reading packet.  Error code: ");  
          //nss.println(xbee.getResponse().getErrorCode());
        } else {
          // local XBee did not provide a timely TX Status Response -- should not happen
          flashLed(errorLed, 2, 50);
        }
    }
    delay(1000);
}
