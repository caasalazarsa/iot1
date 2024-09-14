# Complete project details at https://RandomNerdTutorials.com

import time
from time import sleep_ms
from umqttsimple import MQTTClient
import ubinascii
import machine
from machine import Pin
import micropython
import network
import _thread
from math import atan,atan2,cos,sin


count=0

def lectura_GAS():
    global count
    
    while True:
        
        count+=1
        count=count%10
        time.sleep(1)
        
        
        
_thread.start_new_thread(lectura_GAS,())
        
        
      

    

ssid = 'Carlitosh'
password = '123456rt'
mqtt_server = 'broker.mqtt.cool'
mqtt_port = 1883
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'medida'


last_message = 0
message_interval = 5
counter = 0
ritmo=60
latlong=b'4.629500,-74.070044'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

ticks1=time.ticks_ms()




while station.isconnected() == False:
    ticks2=time.ticks_ms()
    if time.ticks_diff(ticks1, ticks2) % 10000 ==0:
        print("conectando")
    pass

print('Connection successful')
print(station.ifconfig())

def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server,port=mqtt_port,keepalive=60)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()





try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = b'%d' % count
      client.publish(topic_pub, msg)      
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()