#!/usr/bin/python

from pssh import SSHClient, ParallelSSHClient, utils
import random
import sys
import time

output = []
hosts = ['client0.local', 'client1.local', 'client2.local','client3.local', 'client4.local']
client = ParallelSSHClient(hosts)

ssh_clients = []

#open a ssh connection for each host
for host in hosts :
	one_client = SSHClient(host, user="pi")
	print("Connecting to ", host)
	#time.sleep(.5)
	ssh_clients.append(one_client)
	
def open_movie(choice, clientID) :
	num = random.randint(1,2)
	command = "~/dbuscontrol.sh stop"
	ssh_clients[clientID].exec_command(command, user="pi")
	command = "omxplayer /mnt/usb/media/" + choice + "/mov_" + str(num) + ".mp4 --aspect-mode=stretch --amp=1000"
	ssh_clients[clientID].exec_command(command, user="pi")
	print("Opening a " +choice+ " movie, number " + str(num) + " on " + hosts[clientID] + "!\r")

def play_screensaver() :
	cmds = ["~/dbuscontrol.sh stop"]
	for cmd in cmds:
		client.run_command(cmd, user="pi", stop_on_errors=False)
	time.sleep(.1)	
	cmds = ["omxplayer /mnt/usb/media/intro.mp4 --aspect-mode=stretch --loop --no-osd"]
	for cmd in cmds:
		client.run_command(cmd, user="pi", stop_on_errors=False)
	print("Playing screen saver on all clients \r")
	
def pause_movie(clientID) :
	command = "~/dbuscontrol.sh pause"
	ssh_clients[clientID].exec_command(command, user="pi")

	
def unpause_all() :
	cmds = ["~/dbuscontrol.sh pause"]
	for cmd in cmds :
		client.run_command(cmd, user="pi", stop_on_errors=False)
		
def rewind_all() :
	cmds = ["~/dbuscontrol.sh setposition=0"]
	for cmd in cmds :
		client.run_command(cmd, user="pi", stop_on_errors=False)

def setposition_all_delayed(delayTime) :
	for i in range(len(ssh_clients)):
		pausePosition = 4000000 - (i * 1000000)
		time.sleep(delayTime)
		command = "~/dbuscontrol.sh setposition " + str(pausePosition)
		ssh_clients[i].exec_command(command, user="pi")
		print(hosts[i] + " position set to " + str(pausePosition) + "\r")

def play_at_position(clientID, playpos) :
	command = "~/dbuscontrol.sh setposition " + str(playpos)
	ssh_clients[int(clientID)].exec_command(command, user="pi")
	
def stop_all_runningmovies() :
	cmds = ["~/dbuscontrol.sh stop"]
	for cmd in cmds :
		client.run_command(cmd, user="pi", stop_on_errors=False)
	
def shutdown_all():
  cmds=["shutdown now"]
  for cmd in cmds:
     output.append(client.run_command(cmd, stop_on_errors=False, sudo=True))

  for _output in output:
     client.join(_output)
     print(_output)
  print("Finished shutting down clients")
  

