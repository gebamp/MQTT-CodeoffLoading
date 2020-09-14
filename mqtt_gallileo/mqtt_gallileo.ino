/*
 Basic MQTT example

 This sketch demonstrates the basic capabilities of the library.
 It connects to an MQTT server then:
  - publishes "hello world" to the topic "outTopic"
  - subscribes to the topic "inTopic", printing out any messages
    it receives. NB - it assumes the received payloads are strings not binary

 It will reconnect to the server if the connection is lost using a blocking
 reconnect function. See the 'mqtt_reconnect_nonblocking' example for how tov
 achieve the same result without blocking the main loop.
 
*/
#include <Arduino.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.
// Change mac address to gallileo model.
byte mac[]    = {  0xDE, 0xED, 0xBA, 0xFE, 0xFE, 0xED };
IPAddress server(192, 168, 1, 8);//server IP
EthernetClient ethClient;
PubSubClient client(ethClient);
int counter = 0;
int flag = 0;
int jetson_up=0;

void subscribeReceive(char* topic, byte* payload, unsigned int length)
{ char return_value[100],received_payload[50],yes_arr[50],no_arr[50];
  String yes ="Yes";
  String no  ="No";
  String something;
  String received_topic(topic);
  payload[length]='\0';
  // Print the topic
  Serial.print("Topic: ");
  Serial.println(topic);
  if(received_topic.equals("client/jetson_up")){
   Serial.println("Received Message from jetson nano");
   for(int i = 0; i < length; i ++){
    return_value[i]=char(payload[i]);
  }
   yes.toCharArray(yes_arr,50);
   no.toCharArray(no_arr,50);
   if(strcmp((char *)payload,yes_arr)==0){
    jetson_up = 1; 
   }
   else if(strcmp((char *)payload,no_arr)== 0) {
    jetson_up = 0 ;
   }
  }
  else{
  Serial.print("Output from gateway is: ");
  for(int i = 0; i < length; i ++)
  {
    return_value[i]=char(payload[i]);
    Serial.print(return_value[i]);
  }
  something = String(return_value);
  counter = something.toInt();
  flag=1;
  }
  // Print a newline
}

void connect_to_broker() {
  String ip;
  char init_array[100];
  ip=DisplayAddress(Ethernet.localIP())+"\n gallileo \n";
  ip.toCharArray(init_array,100);
  // Loop until we're connected
  
  while (!client.connected()){
    Serial.println("Attempting MQTT connection");
    // Attempt to connect
    if (client.connect("gallileo","server/node_disconnection",2,false,init_array)){ 
        Serial.println("Succesfully connected to information broker!");
        setting_up_connections();
    }
    else 
    {
      Serial.print("Connection not succesfully setup! rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
  
}
void setting_up_connections(){
String ip;
char init_array[100];

    ip=DisplayAddress(Ethernet.localIP())+"\n gallileo \n";
    ip.toCharArray(init_array,100);
    client.publish("server/connected_devices",init_array);
    client.subscribe("client/gallileo");
    client.subscribe("client/jetson_up");
    return ;
}
void setup()
{ 
  Serial.begin(9600);

  client.setServer(server, 1883);
  

  Ethernet.begin(mac);
  // Allow the hardware to sort itself out
  delay(1500);
  connect_to_broker();
  client.setCallback(subscribeReceive);
}
String DisplayAddress(IPAddress address)
{
 return String(address[0]) + "." + 
        String(address[1]) + "." + 
        String(address[2]) + "." + 
        String(address[3]);
}

void loop()
{   char char_array [10];
    String output;
    String ip;
    char init_array[100];
    client.loop();
    delay(2000);
    unsigned long total_sec = millis();
    if(counter<40){
      if(random(1,10)>5){
        counter=counter+1;
        output = String(counter);
        Serial.println("Calculating data locally");
        Serial.println("Output from gallileo is:"+output);
      }
      else{
        if(jetson_up == 1 ){
        output = String(counter);
        output.toCharArray(char_array,100);
        Serial.println("Sending data to gateway");
        client.publish("server/gallileo",char_array);
        while(flag==0 && jetson_up==1){
         client.loop();
         total_sec = total_sec + millis();
         if(total_sec > 10000){
         ip=DisplayAddress(Ethernet.localIP())+"\n gallileo \n";
         ip.toCharArray(init_array,100);
         client.publish("server/connected_devices",init_array);
         total_sec =0;
      }
      }
      flag=0;
      }
        else if(jetson_up == 0){
          Serial.println("Jetson appears to be down we will have to calculate data locally!");
          counter=counter+1;
          output = String(counter);
          Serial.println("Calculating data locally");
          Serial.println("Output from gallileo is:"+output);
        }
      }  
    }
         total_sec = total_sec + millis();
         if(total_sec > 10000){
         ip=DisplayAddress(Ethernet.localIP())+"\n gallileo \n";
         ip.toCharArray(init_array,100);
         client.publish("server/connected_devices",init_array);
         total_sec =0;
         }
}
 
