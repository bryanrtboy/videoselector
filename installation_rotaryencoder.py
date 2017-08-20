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
from time import sleep
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

DEBUG = False
READKNOB = False
READBUTTON = False
ROTARYKNOB = True


# Setup display and initialise pi3d
backgroundColor = (0,0,0,1)


DISPLAY = pi3d.Display.create(x=200, y=200, background=backgroundColor, frames_per_second=30)  #anti-alias use 'samples=4'
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


def ModelSetup() :
	global screenWidth
	global positionIncrement
	global selectable
	
	pos = -screenWidth #start positioning from the left edge

	for model in models :
		model.obj.set_line_width(line_width=1.0,strip=True,closed=True)
		model.obj.set_material(material=validColor)
		model.isValidSelection = True
		if ROTARYKNOB == True :
			pos += positionIncrement
			model.obj.positionX(pos)
			print ( "Placing ", str(model.obj.name), " at ", str(round(model.obj.x(),4)), "\r")
	
ModelSetup()
print("Done setting up models")
new_models = models[:]

#set up the waiting screen and camera for it
waitscreen = pi3d.FixedString(home_path + 'fonts/NotoSans-Regular.ttf', "Loading...", font_size=72, color=(0, 255, 255, 255), background_color=(255,0,0,0),
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
threshold = 2

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
clockwise = True

def ReadRotaryInput() :
	global counter
	global clkLastState
	global clockwise
	global READBUTTON
	global READKNOB
	
	clkState = GPIO.input(clk)
	dtState = GPIO.input(dt)
	if clkState != clkLastState:
		if dtState != clkState:
			counter += 1
			clockwise = True
		else:
			counter -= 1
			clockwise = False
		print (str(counter), "\r")
	clkLastState = clkState
	#sleep(0.01)
	
	input_state = GPIO.input(22)
	if input_state == False:
		print('B1 Pressed')
		READKNOB = True
		#time.sleep(0.2)
	
	input_state = GPIO.input(23)
	if input_state == False:
		print('B2 pressed')
		READBUTTON = True
		#time.sleep(0.2)


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
	
	input_value = GPIO.input(22)
	input_value2 = GPIO.input(23)
	 
	if delayMode == False :
		if input_value == False:
			READBUTTON = True
			while input_value == False:
				input_value = GPIO.input(22)
			
		if READKNOB == True :
			last_knobValue = current_knobValue
			#current_knobValue=mcp.read_adc(0)
			if len(models) >= 1 :  
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
			input_value2 = GPIO.input(23)

while DISPLAY.loop_running():	

	if isPlayingVideoLoop == False :
		rotY += 1
		if rotY >= 360 :
			rotY = 0
		
		intervalCount += .1
		if intervalCount >= 1 :
			intervalCount =0
			READKNOB = True
		
		clockwise = True
		amount = 0
			
		for model in models :
			model.obj.draw()
			
			pos = 0 
			rewindPos = screenWidth - positionIncrement
			#Move object
			pos = model.obj.x() + (1 * counter)
			if pos >= screenWidth :
				pos = -rewindPos
				
			model.obj.positionX(pos)
		
			zOffset = 0.0
			
			if model.obj.x() > -2.5 and model.obj.x() < 2.5 : # In the Selection Zone
				
				if model.isValidSelection == True :
					zOffset = (2.5 - abs(model.obj.x())) * 5
					selectionID = models.index(model)
					model.obj.rotateIncX(-3)
			else :
				model.obj.rotateToX(0)
			model.obj.positionZ(-zOffset + 20.0)
			model.obj.positionY((zOffset*.4) - 4)
			model.obj.rotateToY(rotY)
	
		if delayMode == False : #Delay Mode is to give the client movie time to load, before pausing it, so we don't want new Input either
			#ReadInput()
			ReadRotaryInput()
			#drawing needs to be after reading input because we are deleting items from the array with a knob
			
			models[selectionID].obj.rotateToY(rotY)
			models[selectionID].obj.rotateToX(rotX)
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
					#DISPLAY.set_background(1,1,1,1)
					unpauseAllVideos=True
					isPlayingVideoLoop = True
		
		if READBUTTON == True :
			READBUTTON = False
			if selectionID in selected :
				print("Not a valid selection\r")
			elif abs(models[selectionID].obj.x()) <= 2.5 :
				delayMode = True
				print("Opening a ", names[selectionID], " movie on ", clientMachine, "\r")
				selected.append(selectionID)
				models[selectionID].obj.set_material(material=invalidColor)
				models[selectionID].isValidSelection = False
				if clientMachine >= 4 :
					DISPLAY.set_background(invalidColor[0], invalidColor[1], invalidColor[2],1)
				clientPlayer.open_movie(names[selectionID], clientMachine)
			else :
				print("Object is not the selection area")
			
	else :
		waitscreen.draw()

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
			clientPlayer.play_at_position(positionCount, pos)
			print("sending position " + str(pos) + " to " + str(positionCount) + "\r")
			positionCount += 1
			time.sleep(.1)
			if positionCount >= 5 :
				setPositions=False
				positionCount=0
		
		if unpauseAllVideos == True :
			unpauseAllVideos = False
			clientPlayer.unpause_all()
			print("Unpaused all the videos\r")
			delayMode = True

		if finalCountdown >= 600 : #need to insure that the delays are not truncated by this function...
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
	
