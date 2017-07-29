#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Installation using a physical rotary potentiometer to browser, and a button to
select an item. Once selected, a message is sent to a remote client, telling it to play a video
that corresponds to the selection. After all the selections are made, the videos play for
15 seconds and then the clients revert to a screen-saver video loop.
"""
import ClientMoviePlayer as clientPlayer

#start up client machines
clientPlayer.play_screensaver()

import pi3d
import time
import os
import RPi.GPIO as gpio
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import ScaleValues as scaleVal
import RGBCompliment as rgbColor

home_path = "/home/pi/naropa_installation/"


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

randcolor = rgbColor.random_colorf(1.0)

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=100, y=100, background=(0,0,0,.5), frames_per_second=30)  
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
                
light = pi3d.Light(lightpos=(-2.0, 3.0, 5.0), lightcol=(30.0, 30.0, 30.0), lightamb=(1.02, 10.01, 5.03), is_point=False)

flatsh = pi3d.Shader("uv_flat")
shadermat = pi3d.Shader("mat_flat")

xyz = .001

gun = pi3d.Model(file_string= home_path + 'models/gun.obj', camera=CAMERA, name='gun',z=10.0)
gun.scale(xyz,xyz,xyz)

bear = pi3d.Model(file_string=home_path + 'models/bear.obj', camera=CAMERA, name='bear', z=10.0)
bear.scale(xyz,xyz,xyz)

fork = pi3d.Model(file_string=home_path + 'models/fork.obj', camera=CAMERA, name='fork', z=10.0)
fork.scale(xyz,xyz,xyz)

knife = pi3d.Model(file_string=home_path + 'models/knife.obj', camera=CAMERA, name='knife', z=1.0)
knife.scale(xyz,xyz,xyz)

cake = pi3d.Model(file_string=home_path + 'models/cake.obj', camera=CAMERA, name='cake', z=10.0)
cake.scale(xyz,xyz,xyz)

models = [bear,gun,fork,cake,knife]

for model in models :
	#model.set_shader(shadermat)
	model.set_line_width(line_width=1.0,strip=False,closed=True)
	
labels = []

#Generate the labels for the models
for x in range(0,len(models)) :
	strin = pi3d.FixedString(home_path + 'fonts/NotoSans-Regular.ttf', models[x].name, font_size=144, color=(255, 255, 255, 255), background_color=None,
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
	strin.sprite.position(0,0,2)
	labels.append(strin)

new_labels = labels[:] #copy the lists so we can regenerate later
new_models = models[:]

waitscreen = pi3d.FixedString(home_path + 'fonts/NotoSans-Regular.ttf', "Waiting for a bit...", font_size=72, color=(255, 0, 0, 255), background_color=(255,255,255,255),
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
waitscreen.sprite.position(0,0,0)

selectionID = 0
clientMachine = 0
isPlayingVideoLoop = False
showSelectedLabel = False

def ReadInput() :
	global selectionID
	global READKNOB
	#global clientMachine
	#global models
	#global labels
	global showSelectedLabel
	
	input_value = gpio.input(17)
	input_value2 = gpio.input(18)
	  
	if input_value == False:
		showSelectedLabel = True
		#print('You selected a ', models[selectionID].name , ' client is ', clientMachine, '\r')
		DISPLAY.set_background(.5,.5,.5,1)
		clientPlayer.open_movie(models[selectionID].name, clientMachine)	
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
labelWaitTime = 0

while DISPLAY.loop_running():

	rotY += 1
	if rotY >= 360 :
		rotY = 0
	
	intervalCount += .1
	if intervalCount >= 1 :
		intervalCount =0
		READKNOB = True

	if isPlayingVideoLoop == False :
		if showSelectedLabel == True :
			labels[selectionID].draw()
			labelWaitTime += 1
			if labelWaitTime >= 120 :
				showSelectedLabel = False
				labels.remove(labels[selectionID])
				models.remove(models[selectionID])
				labelWaitTime = 0
				DISPLAY.set_background(0,0,0,.5)
				clientMachine += 1
				if clientMachine == 4 : # we just played on the 4th client, only one left to go, so automatically progress now
					showSelectedLabel = True
					clientPlayer.open_movie(models[0].name, clientMachine)
					#clientPlayer.pause_movie(clientMachine)
					selectionID =0
					DISPLAY.set_background(.5,.5,.5,1)
				elif clientMachine == 5 : #we finished with the last delay, show the wait screen
					isPlayingVideoLoop = True
					clientMachine = 0
					models = new_models[:]
					labels = new_labels[:]
					DISPLAY.set_background(1,1,1,1)
					clientPlayer.unpause_all()
		else :
			ReadInput()
			models[selectionID].rotateToY(rotY)
			models[selectionID].rotateToX(rotX)
			models[selectionID].draw()
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
		  clientPlayer.stop_all_runningmovies()
		  mykeys.close()
		  DISPLAY.destroy()
		  break
	
