import paho.mqtt.client as mqtt
import os
import time
import socket 
import subprocess
import queue 

client_queue=queue.Queue(maxsize=0)
connection_flag=0
jetson_up=0
subscrption_flag=0
# The callback for when the client receives a CONNACK response from the server.
def run_cli(cli):
    return subprocess.check_output(cli,shell=True).decode('utf-8')

def on_connect(client, userdata, flags, rc):
    global connection_flag
    global subscrption_flag
    if (rc==0):
        print("Succesfully connected to information broker!")
    else:
        print("Could not connect to infromation broker. Access refused!")
        print("Trying again in 5 seconds!")
        client.reconnect()
    connection_flag=1
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
   # client.publish("server/assign_id","Device_Type: RaspberryPi")
    client.subscribe("client/raspberrypi")
    client.subscribe("client/jetson_up")
    client.publish("server/connected_devices",str(run_cli("hostname -I"))+" "+str(run_cli("hostname")))
   
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global client_queue
    global jetson_up
    if(msg.topic=="client/raspberrypi"):
        client_queue.put(str(msg.payload.decode("utf-8")).split("\n",1)[0])
    elif(msg.topic=="client/jetson_up"):
        if(str(msg.payload.decode("utf-8")).split("\n",1)[0]=="Yes"):
            jetson_up=1
        elif(str(msg.payload.decode("utf-8")).split("\n",1)[0]=="No"):
            jetson_up=0
    
def on_disconnect(client,userdata,rc):
    if rc!=0:
        print("Unexpected device disconnection")
        print("Trying to reinitialise connection!")
        client.connect("192.168.1.8", 1883, 5)
    else:
        print("Diconnected from information broker")
    
def on_publish(client,userdata,mid):
    print("Message published with message id:"+str(mid))

def on_subscribe(client,userdata,mid,granted_qos):
    global subscrption_flag
    print("Succesfully subscribed to requested topic!")
    subscrption_flag=subscrption_flag+1
def on_unsubscribe(client,userdata,mid):
    global subscrption_flag
    print("Succesfully unsubscribed to requested topic!")
    subscrption_flag=subscrption_flag-1

client = mqtt.Client("Raspberry_Pi")
# Callback functions!
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscribe

# Setting up will on unexpected disconnection!
client.will_set("server/node_disconnection",payload=str(run_cli("hostname -I"))+" "+str(run_cli("hostname")),qos=2,retain=False)

client.reconnect_delay_set(min_delay=5,max_delay=20)

# Start connection to information broker!
client.connect("192.168.1.8", 1883, 5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface. 
input = 0
client.loop_start()

while(connection_flag==0):
    pass
while(subscrption_flag<2):
    pass
connection_flag=0
time.sleep(0.2)
while(True):
    if client.is_connected() == False:
        client.reconnect()
    while(input<500):
        if (input % 2)== 0:
            input = input+1
            print("Calculating data localy")
            print("Output from raspberry pi is: "+str(input))
        else:
            if jetson_up==1:
                print("Sending data to jetson nano")
                published_value=client.publish("server/raspberrypi",str(input),qos=2)
                if(published_value.wait_for_publish() is False):
                    print("Failed to queue message!")
                counter=0
                while(client_queue.empty()==True and jetson_up==1):
                    pass
                if(jetson_up==1):
                    temp_input=client_queue.get()
                    print("Output from gateway is: "+temp_input)
                    input=int(temp_input)
                elif(jetson_up==0):
                    print("Jetson must have gone offline we have to calculate output locally")
            elif jetson_up==0:
                print("Jetson Nano is not currently up will have to calculate output localy!")
                input = input+1
                print("Calculating data localy")
                print("Output from raspberry pi is: "+str(input))
        if client.is_connected() == False:
            client.reconnect()
            
