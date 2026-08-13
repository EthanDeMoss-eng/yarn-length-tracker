#define CLK 2
#define DT 3
#define SW 4

const int PULSES_PER_REV = 40;
const float GEOMETRY_FACTOR = 2.75;

long pulseCount = 0;
int lastCLK;
float diameterCm = 0;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 5;

void setup() {
  Serial.begin(9600);
  pinMode(CLK, INPUT);
  pinMode(DT, INPUT);
  pinMode(SW, INPUT_PULLUP);
  lastCLK = digitalRead(CLK);
  Serial.println("READY");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.startsWith("D:")) {
      diameterCm = input.substring(2).toFloat();
      Serial.print("DIAMETER_SET:");
      Serial.println(diameterCm);
    } else if (input == "RESET") {
      pulseCount = 0;
      Serial.println("RESET");
    }
  }

  int currentCLK = digitalRead(CLK);
  int currentDT = digitalRead(DT);

  if (currentCLK != lastCLK) {
    unsigned long currentTime = millis();
    if ((currentTime - lastDebounceTime) > debounceDelay) {
      lastDebounceTime = currentTime;

      if (currentDT != currentCLK) {
        pulseCount++;
      } else {
        pulseCount--;
      }

      if (diameterCm > 0) {
        float circumference = GEOMETRY_FACTOR * diameterCm;
        float rotations = (float)pulseCount / PULSES_PER_REV;
        float lengthCm = rotations * circumference;
        float lengthM = lengthCm / 100;
        float lengthYd = lengthM * 1.09361;

        Serial.print("Length:");
        Serial.print(lengthYd, 3);
        Serial.println("yd");
      }
    }
    lastCLK = currentCLK;
  }

  if (digitalRead(SW) == LOW) {
    pulseCount = 0;
    Serial.println("RESET");
    delay(300);
  }
}