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
import os
import ScaleValues as scaleVal
import Selectable as selectable
from RPi import GPIO
import time

home_path = "/home/pi/naropa_installation/"

clk = 17
dt = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

counter = 0
clkLastState = GPIO.input(clk)
move_speed = .5

DEBUG = False
READKNOB = False
READBUTTON = False
ROTARYKNOB = True

# Setup display and initialise pi3d
backgroundColor = (0,0,0,1)


DISPLAY = pi3d.Display.create(x=0, y=0, background=backgroundColor, frames_per_second=60)  #anti-alias use 'samples=4'
CAMERA = pi3d.Camera()
CAMERA2D = pi3d.Camera(is_3d=False)
          
#light = pi3d.Light(lightpos=(-2.0, 3.0, 5.0), lightcol=(10.0, 10.0, 30.0), lightamb=(1.02, 10.01, 5.03), is_point=False)
light = pi3d.Light(lightpos=(1, -1, -3), lightcol=(1.0, 1.0, 1.0), lightamb=(0.75, 0.75, 0.75), is_point=False)

flatsh = pi3d.Shader("uv_flat")
shadermat = pi3d.Shader("mat_light")

#Set up the 3D models
xyz = .03

names = ["gun","bear","fork","knife","cake"]
models = []

for objname in names :
	temp = selectable.MySelectableObject()
	temp.obj = pi3d.Model(file_string= home_path + 'models/' + objname + '.obj', camera=CAMERA, name=objname,z=0.0)
	temp.obj.scale(xyz,xyz,xyz)
	temp.obj.set_shader(shadermat)
	temp.obj.set_light(light)
	temp.obj.set_fog(fogshade=(.0,.0,.0,.0), fogdist=32)
	models.append(temp)

validColor = (0.0,1.0,1.0)
invalidColor = (0.1,0.1,0.4)
selectedColor = (1.0,.2,.0)

screenWidth = 40
positionIncrement = screenWidth/6 #we need 6 spaces for 5 models
screenWidth = screenWidth/2 #make the width relative to center of the screen, i.e -10 to 10
rewindPos = screenWidth - positionIncrement

def ModelSetup() :
	global screenWidth
	global positionIncrement
	global selectable
	
	pos = -screenWidth #start positioning from the left edge

	for model in models :
		model.obj.set_line_width(line_width=1.0,strip=True,closed=True)
		model.obj.set_material(material=validColor)
		model.isValidSelection = True
		pos += positionIncrement
		model.obj.positionX(pos)
		print ( "Placing ", str(model.obj.name), " at ", str(round(model.obj.x(),4)), "\r")
	
ModelSetup()

new_models = models[:]

#set up the waiting screen and camera for it
waitscreen = pi3d.FixedString(home_path + 'fonts/NotoSans-Regular.ttf', "[ listen ]", font_size=72, color=(0, 0,0, 255), background_color=(255,255,255,0),
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
delayMax = 10

def ReadRotaryInput() :
	global counter
	global clkLastState
	
	clkState = GPIO.input(clk)
	dtState = GPIO.input(dt)
	if clkState != clkLastState:
		if dtState != clkState:
			counter = 1
		else:
			counter = -1
		#print (str(counter), "\r")
	else :
		counter = 0
	clkLastState = clkState


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
	global clockwise
	
	input_value = GPIO.input(23)
	input_value2 = GPIO.input(22)
	 
	if delayMode == False :
		if input_value == False:
			READBUTTON = True
			while input_value == False:
				input_value = GPIO.input(23)
			
		if READKNOB == True : 
			selectByPosition = True #go ahead and select whatever model is nearest to positionX = 0
			READKNOB = False
			if DEBUG == True :
				print('Channel 0: {0}\r'.format(current_knobValue))
			
	if input_value2 == False:
		print('The button 2 has been pressed...\r')
		clientPlayer.shutdown_all()
		time.sleep(5)
		os.system("sudo shutdown -h now")
		while input_value2 == False:
			input_value2 = GPIO.input(22)

moveAmount = 0

while DISPLAY.loop_running():	

	if isPlayingVideoLoop == False :
		ReadRotaryInput()
		
		if counter == 1 and moveAmount  < 1.0 :
			moveAmount += .1
		elif counter == -1 and moveAmount > -1.0 :
			moveAmount -= .1
		else :
			moveAmount *= .9
	
		rotY += 1
		if rotY >= 360 :
			rotY = 0
		
		intervalCount += .1
		if intervalCount >= 1 :
			intervalCount =0
			READKNOB = True
			
		for model in models :
			model.obj.draw()
			pos = 0 
			#Get objects new X coordinate
			#pos = model.obj.x() + (move_speed * counter)
			model.obj.translateX(moveAmount)
			pos = model.obj.x()
			#Recylce off screen
			if pos >= screenWidth :
				pos = -rewindPos
			elif pos <= -screenWidth :
				pos = rewindPos

			model.obj.positionX(pos)		
			zOffset = 0.0
			#Find out if this object is in the middle of the screen
			if abs(model.obj.x()) < 2.5 :
				#slowly move the object forward as it approaches x=0
				if model.isValidSelection == True :
					zOffset = (2.5 - abs(model.obj.x())) * 5
					selectionID = models.index(model)
					#if it is selectable, rotate it on the X axis
					model.obj.rotateIncX(-3)
			else :
				model.obj.rotateToX(0)

			model.obj.positionZ(-zOffset + 20.0)
			model.obj.positionY((zOffset*.4) - 4)
			model.obj.rotateToY(rotY)
	
		if delayMode == False : #Delay Mode is to give the client movie time to load, before pausing it, so we don't want new Input either
			ReadInput()
			#drawing needs to be after reading input because we are deleting items from the array with a knob
			models[selectionID].obj.rotateToY(rotY)
			#models[selectionID].obj.rotateToX(rotX)
			models[selectionID].obj.draw()
		else :
			delayCount += delayIncrement
			if delayCount >= delayMax :
				delayMode = False
				delayCount = 0
				print("Sending a pause message to " + str(clientMachine) + "\r")
				clientPlayer.pause_movie(clientMachine)
				
				clientMachine += 1 #move on to the next machine			
				if clientMachine >= 5 : #we selected the last item, do the other things...
					clientMachine = 0
					ModelSetup()						
					selected = [] #reset the selected ID array
					DISPLAY.set_background(1,1,1,1)
					unpauseAllVideos=True
					isPlayingVideoLoop = True
		
		if READBUTTON == True :
			READBUTTON = False
			if selectionID in selected :
				print("Not a valid selection\r")
			elif abs(models[selectionID].obj.x()) <= 2.5 :
				delayMode = True
				#print("Opening a ", names[selectionID], " movie on ", clientMachine, "\r")
				selected.append(selectionID)
				models[selectionID].obj.set_material(material=invalidColor)
				models[selectionID].isValidSelection = False
				clientPlayer.open_movie(names[selectionID], clientMachine)
			else :
				print("Object is not the selection area")
			
	else :
		waitscreen.draw()
		
		#after videos are unpaused, wait a bit before sending the position message
		if delayMode == True :
			delayCount += delayIncrement
			
			if delayCount >= delayMax :
				delayMode = False
				delayCount = 0
				setPositions = True
		else : 
			finalCountdown += 1
		
		if unpauseAllVideos == True :
                        unpauseAllVideos = False
                        clientPlayer.unpause_all()
                        print("Unpaused all the videos\r")
                        delayMode = True

		if setPositions == True :
			videoPosition = 9500000
			clientPlayer.play_at_position(positionCount,videoPosition)
			positionCount += 1
			#delay before playing the next movie
			time.sleep(.7)
			if positionCount >= 5 :
				setPositions=False
				positionCount=0
		
		if finalCountdown >= 300 : #need to insure that the delays are not truncated by this function...
			isPlayingVideoLoop = False
			clientPlayer.play_screensaver()
			finalCountdown=0
			DISPLAY.set_background(backgroundColor[0],backgroundColor[1], backgroundColor[2], backgroundColor[3])
		

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
	
