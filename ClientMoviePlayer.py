#!/usr/bin/python

from pssh import SSHClient, ParallelSSHClient, utils
import random
import sys

output = []
hosts = ['client0', 'client1', 'client2','client3', 'client4']
client = ParallelSSHClient(hosts)

ssh_clients = []

#open a ssh connection for each host
for host in hosts :
	one_client = SSHClient(host)
	ssh_clients.append(one_client)
	
def open_movie(choice, clientID) :
	num = random.randint(0,2)
	command = "~/dbuscontrol.sh stop"
	ssh_clients[clientID].exec_command(command)
	command = "omxplayer /mnt/usb/media/" + choice + "/mov_" + str(num) + ".mp4 --aspect-mode=stretch --loop"
	ssh_clients[clientID].exec_command(command)
	print("Opening a " +choice+ " movie, number " + str(num) + " on " + hosts[clientID] + "!\r")
	
	
def play_screensaver() :
	cmds = ["~/dbuscontrol.sh stop", "omxplayer /mnt/usb/media/intro.mp4 --aspect-mode=stretch --loop"]
	
	#run all the commands on all the clients
	for cmd in cmds:
		client.run_command(cmd, stop_on_errors=False)
		
def shutdown_all():
  cmds=["shutdown now"]
  for cmd in cmds:
     output.append(client.run_command(cmd, stop_on_errors=False, sudo=True))

  for _output in output:
     client.join(_output)
     print(_output)
  print("Finished shutting down clients")
