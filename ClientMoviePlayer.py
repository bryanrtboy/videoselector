#!/usr/bin/python

from pssh import SSHClient, ParallelSSHClient, utils
import random
import sys
import time

output = []
hosts = ['client0', 'client1', 'client2','client3', 'client4']
client = ParallelSSHClient(hosts)

ssh_clients = []

#open a ssh connection for each host
for host in hosts :
	one_client = SSHClient(host, user="pi")
	print("Connecting to ", host)
	time.sleep(1)
	ssh_clients.append(one_client)
	
def open_movie(choice, clientID) :
	num = random.randint(0,2)
	command = "~/dbuscontrol.sh stop"
	ssh_clients[clientID].exec_command(command, user="pi")
	command = "omxplayer /mnt/usb/media/" + choice + "/mov_" + str(num) + ".mp4 --aspect-mode=stretch --loop"
	ssh_clients[clientID].exec_command(command, user="pi")
	time.sleep(2)
	pause_movie(clientID)
	print("Opening a " +choice+ " movie, number " + str(num) + " on " + hosts[clientID] + "!\r")
	
	
def play_screensaver() :
	cmds = ["~/dbuscontrol.sh stop", "sleep 1", "omxplayer /mnt/usb/media/intro.mp4 --aspect-mode=stretch --loop"]
	print("Playing screen saver on all clients")
	for cmd in cmds:
		client.run_command(cmd, user="pi", stop_on_errors=False)
	
def pause_movie(clientID) :
	command = "~/dbuscontrol.sh pause"
	ssh_clients[clientID].exec_command(command, user="pi")
	print("Pausing movie on " + hosts[clientID] + "\r")
	
def unpause_all() :
	cmds = ["~/dbuscontrol.sh pause"]
	for cmd in cmds :
		client.run_command(cmd, user="pi", stop_on_errors=False)
		
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

