#!/usr/bin/python

import random

def hilo(a, b, c) :
	if c < b: b, c = c,b
	if b < a: a, b = b,a
	if c < b: b, c = c,b
	return a + c

def compliment(r,g,b) :
	k = hilo(r, g, b)
	return tuple(k -u for u in (r, g, b))
	
def random_colorf(alpha) :
	col = [random.uniform(0.0,1.0),random.uniform(0.0,1.0),random.uniform(0.0,1.0),alpha]
	return col

def random_color() :
	levels = range(32,256,32)
	return tuple(random.choice(levels) for _ in range(3))
