#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Installation using a physical rotary potentiometer to browser, and a button to
select an item. Once selected, a message is sent to a remote client, telling it to play a video
that corresponds to the selection. After all the selections are made, the videos play for
15 seconds and then the clients revert to a screen-saver video loop.
"""
import pi3d
import time
import os
import RPi.GPIO as gpio
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import ScaleValues as scaleVal
import ClientMoviePlayer as clientPlayer

gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.IN)
gpio.setup(18, gpio.IN)

CLK=21
MISO=23
MOSI=24
CS=25

mcp= Adafruit_MCP3008.MCP3008(clk=CLK,cs=CS,miso=MISO,mosi=MOSI)

DEBUG = False
READKNOB = False

#start up client machines
clientPlayer.play_screensaver()

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, background=(0.0, 0.0, 0.0, .5), frames_per_second=30 )  
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
                
light = pi3d.Light(lightpos=(-2.0, 3.0, 5.0), lightcol=(30.0, 30.0, 30.0), lightamb=(1.02, 10.01, 5.03), is_point=False)

flatsh = pi3d.Shader("uv_flat")
shadermat = pi3d.Shader("mat_flat")



cow = pi3d.Model(file_string='models/cow2.obj', camera=CAMERA, name='gun',z=10.0)
cow.scale(.5,.5,.5)

bear = pi3d.Model(file_string='models/bear.obj', camera=CAMERA, name='bear', z=10.0)
bear.scale(.25,.25,.25)

skull = pi3d.Model(file_string='models/skull.obj', camera=CAMERA, name='fork', z=10.0)
skull.scale(.5,.5,.5)

teapot = pi3d.Model(file_string='models/teapot.obj', camera=CAMERA, name='pipe', z=10.0)
teapot.scale(.8,.8,.8)

plane = pi3d.Model(file_string='models/biplane.obj', camera=CAMERA, name='cake', z=10.0)
plane.scale(.25,.25,.25)

models = [bear,cow,skull,teapot,plane]

for model in models :
	#model.set_shader(shadermat)
	model.set_line_width(line_width=1.0,strip=False,closed=False)
	
labels = []

#Generate the labels for the models
for x in range(0,len(models)) :
	strin = pi3d.FixedString('fonts/NotoSans-Regular.ttf', models[x].name, font_size=48, color=(70, 70, 180, 255), background_color=None,
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
	strin.sprite.position(0,-250,2)
	labels.append(strin)

new_labels = labels[:] #copy the lists so we can regenerate later
new_models = models[:]

waitscreen = pi3d.FixedString('fonts/NotoSans-Regular.ttf', "Waiting for Godot", font_size=72, color=(255, 0, 0, 255), background_color=(255,255,255,255),
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
waitscreen.sprite.position(0,0,0)

selectionID = 0
clientMachine = 0
isPlayingVideoLoop = False

def ReadInput() :
	global selectionID
	global READKNOB
	global clientMachine
	global models
	global labels
	global isPlayingVideoLoop
	
	input_value = gpio.input(17)
	input_value2 = gpio.input(18)
	
	if input_value == False:
		#DISPLAY.set_background(1,1,1,1)
		print('You selected a ', models[selectionID].name , ' client is ', clientMachine, '\r')
		
		clientPlayer.open_movie(models[selectionID].name, clientMachine)
		
		models.remove(models[selectionID])
		labels.remove(labels[selectionID])
		
		clientMachine += 1
		
		if clientMachine == 4 : #We are on the last choice
			isPlayingVideoLoop = True
			print('opening last choice on screen 5\r')
			clientPlayer.open_movie(models[0].name, 4)
			clientMachine = 0
			models = new_models[:]
			labels = new_labels[:]
			DISPLAY.set_background(1,1,1,1)
			
		READKNOB = True
		while input_value == False:
			input_value = gpio.input(17)
		
	if READKNOB == True :
		value=mcp.read_adc(0)
		if len(models) >= 1 :
			selectionID = int(round( scaleVal.translate(value, 0,1024,0,len(models)-1)))
		READKNOB = False

		if DEBUG == True :
			print('Channel 0: {0}\r'.format(value))
			
	if input_value2 == False:
		print('The button 2 has been pressed...\r')
		clientPlayer.shutdown_all()
		time.sleep(5)
		os.system("sudo shutdown -h now")
		#exit()
		while input_value2 == False:
			input_value2 = gpio.input(18)


#set initial rotation value
rotY =0
rotX = 0

#start counting to read serial data
intervalCount = 0

# Fetch key presses
mykeys = pi3d.Keyboard()
waitTime =0

while DISPLAY.loop_running():

	rotY += 1
	if rotY >= 360 :
		rotY = 0
	
	#rotX += .2
	#if rotX >= 360  :
		#rotX = 0
	
	intervalCount += .1
	if intervalCount >= 1 :
		intervalCount =0
		READKNOB = True
	
	
	
	if isPlayingVideoLoop == False :
		ReadInput()
		models[selectionID].rotateToY(rotY)
		models[selectionID].rotateToX(rotX)
		models[selectionID].draw()
		labels[selectionID].draw()
	else :
		waitscreen.draw()
		waitTime += 1
		if waitTime > 450 : #delay is 15 time 30 fps = 450
			isPlayingVideoLoop = False
			waitTime = 0
			clientPlayer.play_screensaver()
			DISPLAY.set_background(0,0,0,.5)

	k = mykeys.read()
	if k >-1:
		if k==112: #'p' key is pressed
		  pi3d.screenshot('screenshot.jpg')
		elif k==100 : #'d' key pressed
		  DEBUG = not DEBUG
		elif k==27:
		  mykeys.close()
		  DISPLAY.destroy()
		  break
	
