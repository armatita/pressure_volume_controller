//Programado por: José Correia (Última atualização em 25/5/2021)
//Configurações: Arduino NANO com o "processador ATmega 328P (old bootloader)"
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);
#include <SoftwareSerial.h>
SoftwareSerial mySerial(0, 10);
double PSensor = A0;
int PinoDir = 2;
int PinoPasso = 3;
const int pinoIC = 6; //PINO DIGITAL UTILIZADO PELA CHAVE INICIO DE CURSO (pinoIC)
const int saidaIC = 11; //PINO DIGITAL UTILIZADO PELO LED (saidaIC)
const int pinoFC = 7; //PINO DIGITAL UTILIZADO PELA CHAVE FIM DE CURSO (pinoFC)
const int saidaFC = 12; //PINO DIGITAL UTILIZADO PELO LED (saidaFC)
float ST; 

                            //int vai = 20000;  -  valores de vai vem entre 500 e 30000 - Informativo
                            //int vem = 20000;  -  int estima_velocidade(double a, double b) - Informativo
                            //#include <EEPROM.h> - (desnecessário)
                            //float SetPoint = ST;  - (desnecessário)
                            //int steps = 10;       - (desnecessário)
                            // Programa que antes dos testes era igual ao programa NANO_20-5-2021.ico
                            
                            // PARA CONCRETIZAR: (incluido no Hardware)
                            // Falta forçar a paragem se forem atingidos os fim de curso
                            // Deixar de enviar sinal quando não houver sinal dos fim de curso
                            // Incluir a programação para zero inicial e linearização do transdutor

void setup() {
  pinMode(PSensor, INPUT);
  pinMode(PinoDir, OUTPUT);
  pinMode(PinoPasso, OUTPUT);
  lcd.init ();
  lcd.backlight();
  Serial.begin(9600);
  pinMode(pinoIC, INPUT_PULLUP); //DEFINE O PINO COMO ENTRADA / "_PULLUP" É PARA ATIVAR O RESISTOR INTERNO
                                //DO ARDUINO PARA GARANTIR QUE NÃO EXISTA FLUTUAÇÃO ENTRE 0 (LOW) E 1 (HIGH)
  pinMode(saidaIC, OUTPUT); //DEFINE O PINO COMO SAÍDA DO INICIO DE CURSO
  digitalWrite(saidaIC, LOW); //INICIA DESLIGADO
  pinMode(pinoFC, INPUT_PULLUP); //DEFINE O PINO COMO ENTRADA / "_PULLUP" É PARA ATIVAR O RESISTOR INTERNO
                                //DO ARDUINO PARA GARANTIR QUE NÃO EXISTA FLUTUAÇÃO ENTRE 0 (LOW) E 1 (HIGH)
  pinMode(saidaFC, OUTPUT); //DEFINE O PINO COMO SAÍDA DO FIM DE CURSO
  digitalWrite(saidaFC, LOW); //INICIA DESLIGADO
}

void Motor(boolean dir, int steps) {
  digitalWrite(PinoDir, dir);
  for (int i = 0; i < steps; i++) {
    digitalWrite(PinoPasso, HIGH);
    delayMicroseconds(100);  //Define o comprimento do pulse (pulso minimo 1.0uS)
    digitalWrite(PinoPasso, LOW);
    delayMicroseconds(100);  
  }
}
void Le_Set_Pressao() {
    float ST = Serial.parseInt();
}

void Escreve() {
  lcd.clear();
  double ValSensor1 = (analogRead(PSensor)-106); // -106 é o valor necessário para a leitura de zero pressão
  lcd.setCursor(0, 0);
  lcd.print("  LEITURAS DO CPV  ");
  lcd.setCursor(0, 1);
  lcd.print("Pressao ");
  lcd.setCursor(11, 1);
  lcd.print(ValSensor1,1);
  lcd.setCursor(17, 1);
  lcd.print("KPa");
  lcd.setCursor(0, 2);
  lcd.print("SetPressao"); 
  lcd.setCursor(11, 2);
  lcd.print(ST,1);
  lcd.setCursor(17, 2);
  lcd.print("KPa");
}

int estima_velocidade(double a, double b) {
  double diff = (b - a);
  if  (diff > 100) {   // colocar alternativas para valores intermédios
    return 20000;
  }
  else if (diff < 1.5){
    return 0;
  }
  else{
    return 1000; // colocar alternativas para valores intermédios
  }
}

void loop() {
  if(digitalRead(pinoIC) == LOW){ //SE A LEITURA DO PINO FOR IGUAL A LOW, FAZ
      digitalWrite(saidaIC, HIGH); //ENVIA SINAL PELO PINO DIGITAL 11
      Serial.println("IC_H");
      lcd.setCursor(1, 3);
      lcd.print("Limite - Inicio de curso");
      
  }else{ 
    digitalWrite(saidaIC, LOW); //NÃO ENVIA SINAL PELO PINO DIGITAL 11
    Serial.println("IC_L");
}
  if(digitalRead(pinoFC) == LOW){ //SE A LEITURA DO PINO FOR IGUAL A LOW, FAZ
      digitalWrite(saidaFC, HIGH); //ENVIA SINAL PELO PINO DIGITAL 12
      Serial.println("FC_H");
      lcd.setCursor(1, 3);
      lcd.print("Limite - Fim de curso");
  }else{ 
    digitalWrite(saidaFC, LOW); //NÃO ENVIA SINAL PELO PINO DIGITAL 12
    Serial.println("FC_L");
  }

  if (Serial.available()){
    ST = Serial.parseInt();
  }
  double ValSensor1 = (analogRead(PSensor)-106);
  Escreve();
  Serial.println(ValSensor1,1);
  if (ST != 0){
    if ((ValSensor1) < (ST-1.5)){
      Motor(true, estima_velocidade((ValSensor1),(ST-1.5)));
    }
    if ((ValSensor1) > (ST+1.5)){
      Motor(false, estima_velocidade((ST-1.5),(ValSensor1)));
    }
  }
  else{
  Escreve();
}
delay(500);
}
