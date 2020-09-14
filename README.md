# MQTT-CodeoffLoading


# MQTT
  The MQTT messaging protocol was used for this project.
  MQTT Broker:  Mosquitto
  
# Server Side
  The server for this project was an NVIDIA Jetson Nano which when compared to the other nodes 
  of the system has a GPU.
  The server was subscribed to multiple topics depending on the device.
  All the clients publish in a certain topic and then the gateway runs the corresponding cuda 
  code and then sends back the results to the devices in order to boost their performance.

# Client Side
  The clients either run their code locally or they publish the arguments that they will
  run the code for. Upon sending  their message they wait until the receive the output 
  from the gateway. 
  For this project the clients used were:
  - Raspberry pi 4
  - Arduino
  - Intel Gallileo
  - Beagleboard
