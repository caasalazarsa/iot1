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
import MPU6050
from math import atan,atan2,cos,sin


i2c = machine.I2C(1,freq=400000,scl=Pin(22), sda=Pin(21))

print(i2c.scan())  

# Set up the MPU6050 class 
mpu = MPU6050.MPU6050(i2c)

mpu.wake()

angulos=''


angx_g=0
angy_g=0

angx_a=0
angy_a=0




def lectura_IMU():
    global mpu,angulos,angx_g,angy_g,angx_a,angy_a
    while True:
        gyro = mpu.read_gyro_data()
        accel = mpu.read_accel_data()
#         print("Gyro: " + str(gyro) + ", Accel: " + str(accel))
        
        angx_g=angx_g+(gyro[0]-10)*0.1
        angy_g=angy_g+gyro[1]*0.1
        
        angx_a=atan(accel[1]/(accel[0]**2+accel[2]**2)**0.5)
        angy_a=-atan(accel[0]/(accel[1]**2+accel[2]**2)**0.5)
        
#         print(angx_g,angy_g,angx_a,angy_a)
        
        angx=0.98*angx_a+0.02*angx_g
        angy=0.98*angy_a+0.02*angy_g
        
        angulos="{},{}".format(angx,angy)
        
        time.sleep(0.1)
        

_thread.start_new_thread(lectura_IMU,())
        

    

ssid = 'Carlitosh'
password = '123456rt'
mqtt_server = 'broker.mqtt.cool'
mqtt_port = 1883
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'notification'
topic_pub = b'ritmo'
topic_pub2 = b'latlong'
topic_pub3 = b'orientacion'
topic_pub4 = b'angulos'

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
      msg = b'#%d' % ritmo
      msg2= latlong
      msg3= b'0.0,70.0,20.0'
      client.publish(topic_pub, msg)
      client.publish(topic_pub2, msg2)
      client.publish(topic_pub3, msg3)
      client.publish(topic_pub4, angulos)
      
      
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()