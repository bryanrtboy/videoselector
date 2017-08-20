#!/usr/bin/python

import pi3d

class MySelectableObject :
	home_path = "/home/pi/naropa_installation/"
	obj = pi3d.Model(file_string= home_path + 'models/gun.obj', name='gun',z=0.0)
	isSelected = False
	isValidSelection = True

	
