#!/usr/bin/python
from __future__ import absolute_import, division, print_function, unicode_literals
""" Installation using a physical rotary potentiometer to browser, and a button to
select an item. Once selected, a message is sent to a remote client, telling it to play a video
that corresponds to the selection. After all the selections are made, the videos play for
15 seconds and then the clients revert to a screen-saver video loop.
"""
#import ClientMoviePlayer as clientPlayer

#start up client machines
#clientPlayer.play_screensaver()

import pi3d
import time
import os
import RPi.GPIO as gpio
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import ScaleValues as scaleVal

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
READBUTTON = False
ROTARYKNOB = True

# Setup display and initialise pi3d
DISPLAY = pi3d.Display.create(x=200, y=200, background=(0,0,0,.5), frames_per_second=30)  #anti-alias use 'samples=4'
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
          
#light = pi3d.Light(lightpos=(-2.0, 3.0, 5.0), lightcol=(10.0, 10.0, 30.0), lightamb=(1.02, 10.01, 5.03), is_point=False)
light = pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 1.0), lightamb=(0.25, 0.2, 0.3))

flatsh = pi3d.Shader("uv_flat")
#shadermat = pi3d.Shader("mat_flat")

#Set up the 3D models
xyz = .02

gun = pi3d.Model(file_string= home_path + 'models/gun.obj', camera=CAMERA, name='gun',z=10.0)
gun.scale(xyz,xyz,xyz)

bear = pi3d.Model(file_string=home_path + 'models/bear.obj', camera=CAMERA, name='bear', z=10.0)
bear.scale(xyz,xyz,xyz)

fork = pi3d.Model(file_string=home_path + 'models/fork.obj', camera=CAMERA, name='fork', z=10.0)
fork.scale(xyz,xyz,xyz)

knife = pi3d.Model(file_string=home_path + 'models/knife.obj', camera=CAMERA, name='knife', z=10.0)
knife.scale(xyz,xyz,xyz)

cake = pi3d.Model(file_string=home_path + 'models/cake.obj', camera=CAMERA, name='cake', z=10.0)
cake.scale(xyz,xyz,xyz)

models = [bear,gun,fork,cake,knife]
validColor = (1.0,1.0,1.0)
invalidColor = (0.1,0.1,0.1)
startPosition = -15
maxMovePosition = 18

for i in range(len(models)):
	models[i].set_line_width(line_width=2.0,strip=True,closed=True)
	models[i].set_material(material=validColor)
	if ROTARYKNOB == True :
		models[i].positionX( startPosition + (i * 8))
		print ( "Placing ", str(models[i].name), " at ", str(models[i].x()))
	
new_models = models[:]

#set up the waiting screen and camera for it
waitscreen = pi3d.FixedString(home_path + 'fonts/NotoSans-Regular.ttf', "Waiting for a bit...", font_size=72, color=(255, 0, 0, 255), background_color=(255,255,255,255),
camera=CAMERA2D, shader=flatsh, f_type='SMOOTH')
waitscreen.sprite.position(0,0,0)

selectionID = 0
selected = [] #keep track of what has been selected...
makeSelection = False
clientMachine = 0
isPlayingVideoLoop = False


#set initial rotation value
rotY =0
rotX = 0
moveX_increment = 0.01


#start counting to read serial data
intervalCount = 0

# Fetch key presses
mykeys = pi3d.Keyboard()

finalCountdown =0
unpauseAllVideos = False
setPositions=False
positionCount = 0

delayMode = False
delayCount=0
delayIncrement = .1
delayMax = 5
delayedClient =0

current_knobValue = 0.0
last_knobValue =0.0

def ReadInput() :
	global selectionID
	global READKNOB
	global READBUTTON
	global ROTARYKNOB
	global clientMachine
	global delayMode
	global makeSelection
	global current_knobValue
	global last_knobValue
	
	input_value = gpio.input(17)
	input_value2 = gpio.input(18)
	 
	if delayMode == False :
		if input_value == False:
			READBUTTON = True
			while input_value == False:
				input_value = gpio.input(17)
			
		if READKNOB == True :
			last_knobValue = current_knobValue
			current_knobValue=mcp.read_adc(0)
			if len(models) >= 1 :  
				if ROTARYKNOB == False :
					selectionID = int(round( scaleVal.translate(current_knobValue, 0,1024,0,len(models)-1))) #Scales the volume dial to the array range
				else :
					makeSelection = True #go ahead and select whatever model is nearest to positionX = 0
			
			READKNOB = False
	
			if DEBUG == True :
				print('Channel 0: {0}\r'.format(current_knobValue))
			
	if input_value2 == False:
		print('The button 2 has been pressed...\r')
		#clientPlayer.shutdown_all()
		time.sleep(5)
		os.system("sudo shutdown -h now")
		while input_value2 == False:
			input_value2 = gpio.input(18)


while DISPLAY.loop_running():
	
	if isPlayingVideoLoop == False :
		rotY += 1
		if rotY >= 360 :
			rotY = 0
		
		intervalCount += .1
		if intervalCount >= 1 :
			intervalCount =0
			READKNOB = True
		
		if ROTARYKNOB == True :
			for model in models :
				model.rotateToY(rotY)
				amount = abs( current_knobValue - last_knobValue)
				if current_knobValue < last_knobValue :
					model.translateX(-amount * moveX_increment)
					if model.x() <= -maxMovePosition :
						model.positionX(maxMovePosition)
				else :
					model.translateX(amount * moveX_increment)
					if model.x() >= maxMovePosition :
						model.positionX(-maxMovePosition)
					
				temp_id = models.index(model)
				#if temp_id in selected :
					#model.set_line_width(line_width=0.01)
				#else :
					#model.set_line_width(line_width=2.0)
					
				model.draw()


				if makeSelection == True and model.x() > -1.5 and model.x() < 1.5 :
					makeSelection = False
					
					if temp_id in selected :
						if DEBUG == True :
							print("Not a valid selection\r")
					else :
						selectionID = models.index(model)
					if DEBUG == True :
						print ("Selection ID is ", str(selectionID), ", a ", model.name, "\r")

		
		if delayMode == False :
			ReadInput()
			#drawing needs to be after reading input because we are deleting items from the array
			if ROTARYKNOB == False :
				models[selectionID].rotateToY(rotY)
				models[selectionID].rotateToX(rotX)
				models[selectionID].draw()
		else :
			delayCount += delayIncrement
			if delayCount >= delayMax :
				delayMode = False
				delayCount = 0
				print("Sending a pause message to " + str(clientMachine) + "\r")
				#clientPlayer.pause_movie(clientMachine)
				if ROTARYKNOB == False :
					models.remove(models[selectionID]) #Don't need to do remove when using a rotary knob
				
				selected.append(selectionID) #add the ID to the selected objects
				
				clientMachine += 1 #move on to the next machine			
				if clientMachine >= 5 : #we selected the last item, do the other things...
					clientMachine = 0
					
					models = new_models[:] #Do not need to reset the array anymore
					selected = [] #reset the selected ID array
					DISPLAY.set_background(1,1,1,1)
					unpauseAllVideos=True
					isPlayingVideoLoop = True
		
		if READBUTTON == True :
			READBUTTON = False
			delayMode = True
			models[selectionID].set_material(material=invalidColor)
			#clientPlayer.open_movie(models[selectionID].name, clientMachine)
			
			
	else :
		waitscreen.draw()
		#finalCountdown += 1
		
		if delayMode == True :
			delayCount += delayIncrement
			
			if delayCount >= delayMax :
				delayMode = False
				delayCount = 0
				setPositions = True
		else : 
			finalCountdown += 1
		
		if setPositions == True and delayMode == False:
			pos = 4500000 - (positionCount * 1000000)
			#clientPlayer.play_at_position(positionCount, pos)
			print("sending position " + str(pos) + " to " + str(positionCount) + "\r")
			positionCount += 1
			time.sleep(.1)
			if positionCount >= 5 :
				setPositions=False
				positionCount=0
		
		if unpauseAllVideos == True :
			unpauseAllVideos = False
			#clientPlayer.unpause_all()
			print("Unpaused all the videos\r")
			delayMode = True

		if finalCountdown >= 600 : #need to insure that the delays are not truncated by this function...
			isPlayingVideoLoop = False
			#clientPlayer.play_screensaver()
			finalCountdown=0
			DISPLAY.set_background(0,0,0,.5)
		

	k = mykeys.read()
	if k >-1:
		if k==112: #'p' key is pressed
		  pi3d.screenshot('screenshot.jpg')
		elif k==100 : #'d' key pressed
		  DEBUG = not DEBUG
		elif k==27:
		  #clientPlayer.stop_all_runningmovies()
		  mykeys.close()
		  DISPLAY.destroy()
		  break
	
