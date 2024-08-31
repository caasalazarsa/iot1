import machine
import time
p12 = machine.Pin(12)

pwm12 = machine.PWM(p12)

pwm12.freq(50)


while True:
    
    pwm12.duty(26)
    time.sleep(1)
    pwm12.duty(51)
    time.sleep(1)
    pwm12.duty(102)
    time.sleep(1)
    pwm12.duty(128)
    time.sleep(1)
    
    