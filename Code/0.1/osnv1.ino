#define VERSION "1.00a0"
#define TEMPERATURE 0
#define SOUND 1
#define LIGHT 2

// Global variables
float temperature, light;
int sound;

float get_temperature()
{

    int a0;
    float t, resistance;

    a0 = analogRead(TEMPERATURE);
    resistance=(float)(1023-a0)*10000/a0; 
    t=1/(log(resistance/10000)/3975+1/298.15)-276.15;

    return t;
}

int get_sound()
{
    return analogRead(SOUND);
}

float get_light()
{
    int a2 = analogRead(LIGHT);
    float l=(float)(1023-a2)*10/a2; 
    return l;
}

void setup()
{
    Serial.begin(9600);  
}

void loop()
{
    temperature = get_temperature();
    sound = get_sound();
    light = get_light();

    // Print temperature
    Serial.print("Temperature ");
    Serial.print(temperature);
    Serial.println();

    // Print noise level
    Serial.print("Noise ");
    Serial.print(sound);
    Serial.println();

    // Print luminosity
    Serial.print("Luminosity ");
    Serial.print(light);
    Serial.println();

    delay(1000);
}

