#!/usr/bin/python

from pssh import SSHClient, ParallelSSHClient, utils
import datetime
import time
import random
import sys

output = []
hosts = ['client0', 'client1', 'client2','client3', 'client4']
client = ParallelSSHClient(hosts)
values = ["bear","cake","fork","pipe","gun"]

def open_movies(my_values, delay):
	
	choices = list(my_values)
	for x in range(len(hosts)):
		if x < len(hosts) - 1:
			prompt = "Type "
			for v in choices:
				prompt += v + ", "
			prompt = prompt[:-2]
			prompt += " :"
			choice = get_valid_input(prompt)
			choices.remove(choice.lower())
			open_movie(choice, x)
		else:
			choice = choices[0]
			open_movie(choice, x)
       
	print("wait {0} seconds".format(delay))
	time.sleep(delay) 
	print("done waiting, back to the command and play idle movies on clients")
	
	cmds = ["~/dbuscontrol.sh stop", "sleep 2", "omxplayer /mnt/usb/media/intro.mp4 --aspect-mode=stretch --loop"]
	
	#run all the commands on all the clients
	for cmd in cmds:
		client.run_command(cmd, stop_on_errors=False)
	
	#show a prompt to decide what to do next
	next = raw_input("Hit return to continue or 'Q' to quit:")
	if next == "Q":
		print("quitting")
		exit()
	else:
		open_movies()
		
def open_movie(choice, clientID) :
	one_client = SSHClient(hosts[clientID])
	num = random.randint(0,2)
	command = "~/dbuscontrol.sh stop"
	one_client.exec_command(command)
	command = "omxplayer /mnt/usb/media/" + choice + "/mov_" + str(num) + ".mp4 --aspect-mode=stretch --loop"
	one_client.exec_command(command)
	print("Opening a " +choice+ " movie, number " + str(num) + " on " + hosts[clientID] + "!")
	
	
def get_valid_input(prompt):
  while True:
    data = raw_input(prompt)
    #check if the entered word is in our list of values
    if data.lower() not in values:
        print("Not an appropriate choice.")
    else:
        break
  return data

#if you need to get a response back from the client, use this functio
#instead of open_movies(). 
#Note with --loop argument in cmds, the process will never quit
#requires CTRL-C to end the process
def open_movies_wait_for_output():
  cmds = ["omxplayer /mnt/usb/media/gun/mov_0.mp4 --aspect-mode=stretch --loop"]
  start = datetime.datetime.now()
  for cmd in cmds:
   output.append(client.run_command(cmd, stop_on_errors=False))
  end = datetime.datetime.now()
  print("Started %s commands on %s host(s) in %s" % (
   len(cmds), len(hosts), end-start,))
  start = datetime.datetime.now()
  for _output in output:
    print("waiting for output")
    client.join(_output)
    print(_output)
  end = datetime.datetime.now()
  print("All commands finished in %s" % (end-start,))


if __name__ == "__main__":
  open_movies(values, 15)
