# Complete project details at https://RandomNerdTutorials.com

import time
from time import sleep_ms
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import _thread

uart = machine.UART(2,9600, timeout=2000)
uart.init()
lectura=''


def IRQ(pin):
    global lectura
    try:
        if uart.any()>10:
            lectura=uart.readline().decode()
            print("muestra:"+lectura)
        
    except:
        print("hola")
        pass
        
machine.Pin(16).irq(IRQ, trigger=machine.Pin.IRQ_FALLING)


def lectura_GPS():
    global lectura
    uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x00\x00\xFA\x0F')) #GGA
    lectura=uart.readline()
    sleep_ms(100)
    uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x01\x00\xFB\x11')) #GLL
    lectura=uart.readline()
    sleep_ms(100)
    uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x02\x00\xFC\x13')) #GSA
    lectura=uart.readline()
    sleep_ms(100)
    uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x03\x00\xFD\x15')) #GSV
    lectura=uart.readline()
    sleep_ms(100)
    #uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x04\x00\xFE\x17')) #RMC
    #lectura=uart.readline()
    #sleep_ms(100)
    uart.write(bytearray(b'\xB5\x62\x06\x01\x03\x00\xF0\x05\x00\xFF\x19')) #VTG
    lectura=uart.readline()
    sleep_ms(100)
#     uart.write(bytearray(b'\xB5\x62\x06\x08\x06\x00\xC8\x00\x01\x00\x01\x00\xDE\x6A')) #samplerate 5hz
#     lectura=uart.readline()
#     sleep_ms(100)
    while True:
         try:
            if type(lectura) is str:
                lecturalist=lectura.split(",")
                if lecturalist[0]=="$GPRMC":
                    if len(lecturalist[3][:2])>2 and len(lecturalist[5][:3])>2:
                        latitud=float(lecturalist[3][:2])+(float(lecturalist[3][2:])/60.0)
                        longitud=-1.0*(float(lecturalist[5][:3])+(float(lecturalist[5][3:])/60.0))
                        print(latitud,longitud)
                        time.sleep_ms(100)
         except Exception as e:
            print(e)
            print("error")
            time.sleep_ms(100)
            pass
        

_thread.start_new_thread(lectura_GPS,())
        
        
    
    

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
      
      
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()