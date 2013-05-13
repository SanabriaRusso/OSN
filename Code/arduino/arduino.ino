#include "XBee.h"
#include "DHT.h"

#define DHTPIN 2     // data pin of the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302)
#define SOUND_SENSOR_PIN 0

// Create DHT object
DHT dht(DHTPIN, DHTTYPE);

// Create an XBee object
XBee xbee = XBee();

/*
 * The 'payload' variable will hold the data to be sent.
 * Append a 0 for every byte you want to transmit.
 * -----------------------------------------------------
 * Fundamental data types sizes:
 *  - bool: 1 byte
 *  - char: 1 byte
 *  - short int: 2 bytes
 *  - int: 4 bytes
 *  - long int (long): 4 bytes
 *  - float: 4 bytes
 *  - double: 8 bytes
 *  - long double: 8 bytes
 */

uint8_t payload[12] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

// Union to convert float to byte string
union u_float {
    uint8_t b[4];
    float fval;
} uf;

// Union to convert int to byte string
union u_int {
    uint8_t b[4];
    int ival;
} ui;

// Union to convert char to byte string
union u_char {
    uint8_t b[1];
    char cval;
} uc;


// SH + SL Address of receiving XBee
XBeeAddress64 addr64 = XBeeAddress64(0x0013A200, 0x408B3D9B);
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
        uf.fval = h;
        for (int i=0;i<4;i++){
            payload[i]=uf.b[i];
        }

        uf.fval = t;
        for (int i=0;i<4;i++){
            payload[i+4]=uf.b[i];
        }
        
        uf.fval = s;
        for (int i=0;i<4;i++){
            payload[i+8]=uf.b[i];
        }

        xbee.send(zbTx);

        // Packet is being sent
        flashLed(statusLed, 1, 100);

        // after sending a tx request, we expect a status response
        // wait up to half second for the status response
        if (xbee.readPacket(500)) {
          // got a response!

          // should be a znet tx status            	
          if (xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
            xbee.getResponse().getZBTxStatusResponse(txStatus);

            /*
            // get the delivery status, the fifth byte
            if (txStatus.getDeliveryStatus() == SUCCESS) {
              // success.  time to celebrate
              flashLed(statusLed, 5, 50);
            } else {
              flashLed(errorLed, 3, 500);
            }
            */
          }
        } /* else if (xbee.getResponse().isError()) {
          //nss.print("Error reading packet.  Error code: ");  
          //nss.println(xbee.getResponse().getErrorCode());
        } else {
          // local XBee did not provide a timely TX Status Response -- should not happen
          flashLed(errorLed, 2, 50);
        }*/
    }
    delay(1000);
}
