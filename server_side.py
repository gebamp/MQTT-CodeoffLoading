import paho.mqtt.client as mqtt
import queue
import subprocess
import sys
import threading
import time 
import datetime

serving_queue = queue.Queue(maxsize=0)
connected_devices_ip = []
connected_devices_hostnames = []
subscrption_flag=0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if (rc==0):
        print("Succesfully connected to information broker!")
    else:
        print("Could not connect to infromation broker. Access refused!")
        print("Trying again in 5 seconds!")
        client.reconnect()
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("server/#")
    client.publish("client/jetson_up","Yes",qos=2)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global connected_devices_hostnames
    global connected_devices_ip
    global serving_queue
    if msg.topic == "server/raspberrypi":
        print("I got a message from the pi")
        temp = msg.topic.split("/", 2)
        serving_queue.put(("client/" + temp[1], str(msg.payload.decode("utf-8"))))
    elif msg.topic == "server/arduino":
        print("I got a message from the arduino")
        temp = msg.topic.split("/", 2)
        serving_queue.put(("client/" + temp[1], str(msg.payload.decode("utf-8"))))
    elif msg.topic == "server/beagleboard":
        print("I got a message from the beagleboard")
        temp = msg.topic.split("/", 2)
        serving_queue.put(("client/" + temp[1], str(msg.payload.decode("utf-8"))))
    elif msg.topic == "server/gallileo":
        print("I got a message from the gallileo(beagle_2)")
        temp = msg.topic.split("/", 2)
        serving_queue.put(("client/" + temp[1], str(msg.payload.decode("utf-8"))))
    elif msg.topic == "server/connected_devices":
        data = str(msg.payload.decode("utf-8"))
        ip = data.split("\n", 2)
        if ip[0] not in connected_devices_ip:
            client.publish("client/jetson_up","Yes",qos=2)
            connected_devices_ip.append(ip[0])
            connected_devices_hostnames.append(ip[1])
            print_connected_devices()
    elif msg.topic == "server/node_disconnection":
        data = str(msg.payload.decode("utf-8"))
        ip   = data.split("\n",2)
        if ip[0] in connected_devices_ip and ip[1] in connected_devices_hostnames:
            connected_devices_hostnames.remove(ip[1])
            connected_devices_ip.remove(ip[0])
            print("Device with ip: "+str(ip[0])+"and hostname: "+str(ip[1])+" just got disconnected!")
        if(not len(connected_devices_ip)):
            print("There are no currently connected devices!")
        else:
            print_connected_devices()
    elif msg.topic == "server/rtt_pi_1":
        client.publish("rasp_pi_1/rtt","1",qos=2)
    elif msg.topic == "server/rtt_pi_2":
        client.publish("rasp_pi_2/rtt","1",qos=2)
    elif msg.topic == "server/rtt_beagle_1":
        client.publish("beagle_1/rtt","1",qos=2)
    elif msg.topic == "server/rtt_beagle_2":
        client.publish("beagle_2/rtt","1",qos=2)
        
def on_publish(client,userdata,mid):
    print("Message published with message id: "+ str(mid))

def print_connected_devices():
    global connected_devices_hostnames
    global connected_devices_ip
    print("Currently Connected devices:")
    for counter in range(0, len(connected_devices_hostnames)):
        print(
        "Ip:"
        + connected_devices_ip[counter]
        + " "
        + "Hostname:"
        + connected_devices_hostnames[counter]
        )
    
def on_subscribe(client,userdata,mid,granted_qos):
    global subscrption_flag
    print("Succesfully subscribed to requested topic!")
    subscrption_flag=subscrption_flag+1
def on_unsubscribe(client,userdata,mid):
    global subscrption_flag
    print("Succesfully unsubscribed to requested topic!")
    subscrption_flag=subscrption_flag-1

def on_disconnect(client,userdata,rc):
    if rc!=0:
        print("Unexpected device disconnection")
        print("Trying to reinitialise connection!")
        client.connect("127.0.0.1", 1883, 5)
    else:
        print("Diconnected from information broker")

client = mqtt.Client("Jetson_Nano")
client.will_set("client/jetson_up",payload="No",retain=False)

client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscribe

client.connect("127.0.0.1", 1883, 4)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()
starting_time = time.time()
while True:
    elapsed_time = time.time()
    if (elapsed_time-starting_time >= 30):
        print("Timestamp: "+str(datetime.datetime.now().time()))
        print("Number of active server subscriptions: " + str(subscrption_flag))
        if(not len(connected_devices_ip)):
            print("There are no currently connected devices!")
        else:
            print_connected_devices()
        starting_time=time.time()

    while serving_queue.empty() == False:
        returning_value = serving_queue.get()
        if returning_value[0] == "client/raspberrypi":
            # Run code for pi
            print("Input from node was:" + returning_value[1])
            output = subprocess.check_output(
                ["python3", "raspberrypi.py", returning_value[1]]
            )
            subprocess.call(["nvcc","one.cu"])
            subprocess.call(["./a.out"])
            publishing_value=client.publish(returning_value[0], output,qos=2)
            publishing_value.wait_for_publish()
            if(publishing_value.wait_for_publish() is False):
                    print("Failed to queue message!")
        elif returning_value[0] == "client/arduino":
            # Run code for arduino
            print("Input from node was:" + returning_value[1])
            output = subprocess.check_output(
                ["python3", "arduino.py", returning_value[1]]
            )
            subprocess.call(["nvcc","one.cu"])
            subprocess.call(["./a.out"])
            publishing_value=client.publish(returning_value[0], output)
            publishing_value.wait_for_publish()
            if(publishing_value.wait_for_publish() is False):
                    print("Failed to queue message!")
        elif returning_value[0] == "client/gallileo":
            # Run code for gallileo
            print("Input from node was:" + returning_value[1])
            output = subprocess.check_output(
                ["python3", "gallileo.py", returning_value[1]]
            )
            subprocess.call(["nvcc","one.cu"])
            subprocess.call(["./a.out"])
            publishing_value=client.publish(returning_value[0], output,qos=2)
            publishing_value.wait_for_publish()
            if(publishing_value.wait_for_publish() is False):
                    print("Failed to queue message!")
        elif returning_value[0] == "client/beagleboard":
            # Run code for beagleboard
            print("Input from node was:" + returning_value[1])
            output = subprocess.check_output(
                ["python3", "beagleboard.py", returning_value[1]]
            ) 
            subprocess.call(["nvcc","one.cu"])
            subprocess.call(["./a.out"])
            publishing_value=client.publish(returning_value[0], output,qos=2)
            publishing_value.wait_for_publish()
            if(publishing_value.wait_for_publish() is False):
                    print("Failed to queue message!")
