#!/usr/bin/python

from RPi import GPIO
from time import sleep
import time

clk = 17
dt = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)


counter = 0
clkLastState = GPIO.input(clk)

try:

        while True:
                clkState = GPIO.input(clk)
                dtState = GPIO.input(dt)
                if clkState != clkLastState:
                        if dtState != clkState:
                                counter += 1
                        else:
                                counter -= 1
                        print counter
                clkLastState = clkState
                sleep(0.01)

                input_state = GPIO.input(22)
                if input_state == False:
                        print('B1 Pressed')
                        time.sleep(0.2)

                input_state = GPIO.input(23)
                if input_state == False:
                        print('B2 pressed')
                        time.sleep(0.2)

finally:
         GPIO.cleanup()
    


