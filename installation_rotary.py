#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Wavefront obj model loading. Material properties set in mtl file.
Uses the import pi3d method to load *everything*
"""
import pi3d
import time
import RPi.GPIO as gpio
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import scaleValues as scaleVal

gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN)
gpio.setup(18, gpio.IN)

CLK=21
MISO=23
MOSI=24
CS=25

mcp= Adafruit_MCP3008.MCP3008(clk=CLK,cs=CS,miso=MISO,mosi=MOSI)

count = 0
values = [0,0,0]
noise=5

DEBUG = False

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, background=(0.0, 0.0, 0.0, 0), frames_per_second=30 )  
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
                
light = pi3d.Light(lightpos=(-2.0, 3.0, 5.0), lightcol=(30.0, 30.0, 30.0), lightamb=(1.02, 10.01, 5.03), is_point=False)

flatsh = pi3d.Shader("uv_flat")
shadermat = pi3d.Shader("mat_flat")

cow = pi3d.Model(file_string='models/cow2.obj', name='cow',z=10.0)
cow.set_line_width(line_width=1.0,strip=False,closed=False)
cow.set_shader(shadermat)
cow.scale(.5,.5,.5)

bear = pi3d.Model(file_string='models/bear.obj', name='bear', z=10.0)
bear.set_line_width(line_width=1.0,strip=False,closed=False)
bear.set_shader(shadermat)
bear.scale(.25,.25,.25)

skull = pi3d.Model(file_string='models/skull.obj', name='skull', z=10.0)
skull.set_line_width(line_width=1.0,strip=False,closed=False)
skull.set_shader(shadermat)
skull.scale(.5,.5,.5)

teapot = pi3d.Model(file_string='models/teapot.obj', name='teapot', z=10.0)
teapot.set_line_width(line_width=1.0,strip=False,closed=False)
teapot.set_shader(shadermat)
teapot.scale(.8,.8,.8)

plane = pi3d.Model(file_string='models/biplane.obj', name='plane', z=10.0)
plane.set_line_width(line_width=1.0,strip=False,closed=True)
plane.set_shader(shadermat)
plane.scale(.25,.25,.25)

mytext = '''COW'''
# 'normal' FixedString on a (fairly) solid background
str1 = pi3d.FixedString('fonts/NotoSans-Regular.ttf', mytext, font_size=32, color=(70, 70, 180, 255), background_color=None,
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
str1.sprite.position(0, -200, 2) #NB note Shape methods act on FixedString.sprite

models = [bear,cow,skull,teapot,plane]
labels = []

for x in range(0,len(models)) :
	strin = pi3d.FixedString('fonts/NotoSans-Regular.ttf', models[x].name, font_size=32, color=(70, 70, 180, 255), background_color=None,
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
	strin.sprite.position(0,-250,2)
	labels.append(strin)

currentModel =0
knobSpeed = 1

# Fetch key presses
mykeys = pi3d.Keyboard()

#ToDo, open this on it's own thread and check the value to swap out 3Dmodel
def ReadValues() :
	global count
	global values
	global currentModel
	
	input_value = gpio.input(17)
	input_value2 = gpio.input(18)
	if input_value == False:
		print('You selected a ', models[currentModel].name , '\r')
		while input_value == False:
			input_value = gpio.input(17)
	if input_value2 == False:
		print('The button 2 has been pressed...\r')
		while input_value2 == False:
			input_value2 = gpio.input(18)
	value=mcp.read_adc(0)
	
	#values[count]=value
	#count += 1
	#if count >= len(values):
	  #count=0
	
	#average = sum(values)/len(values)

	#if average-noise  > value :
		#if DEBUG == True :
			#print('Moving counterclockwise: {0}\r'.format(average))
		#currentModel -= knobSpeed
	#elif average+noise < value :
		#if DEBUG == True :
			#print('Moving clockwise: {0}\r'.format(average))
		#currentModel += knobSpeed
		
	currentModel = int(round( scaleVal.translate(value, 0,1024,0,len(models)-1)))
	

	if DEBUG == True :
			print('Channel 0: {0}\r'.format(value))



rotY =0
intervalCount = 0

while DISPLAY.loop_running():

	rotY += 1
	if rotY >= 360 :
		rotY = 0
	
	intervalCount += .1
	if intervalCount >= 1 :
		intervalCount =0
		ReadValues()
	
	models[currentModel].rotateToY(rotY)
	models[currentModel].draw()
	labels[currentModel].draw()

	k = mykeys.read()
	if k >-1:
		if k==112: #'p' key is pressed
		  pi3d.screenshot('screenshot.jpg')
		  DEBUG = not DEBUG

		elif k==27:
		  mykeys.close()
		  DISPLAY.destroy()
		  break
	
