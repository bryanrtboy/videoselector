![alt text](https://github.com/bryanrtboy/videoselector/blob/master/IMG_0099.jpg)

## Video Selector

This project uses a Raspberry Pi 3 as a server/controller to play videos on 5 client Pi's connected via a WIFI network. There should be no limit to the number of clients used. 

To run, this set of python scripts should be running on the server in a directory located in '/home/pi/', in my case it's in a folder called 'naropa_installation'. Update the script with the path you are using. 

The server is wired up through GPIO in order to get input from a rotary encoder [(script)](https://github.com/modmypi/Rotary-Encoder/) , [(instructions)](https://www.modmypi.com/blog/how-to-use-a-rotary-encoder-with-the-raspberry-pi) and two buttons. The rotary dial allows the user to scroll through 3D models rendered on screen, a button is then used to make a selection. Once the button is pressed, a video on one of the client machines starts up. The second button shuts down all of the clients, and then the server.

The script could be altered to accept keyboard commands and not use any GPIO hardware. To do so, set the 'counter' variable to the value -1 with the left arrow key, +1 with the right this would scroll the models left to right.  Use a key press to set READBUTTON to True in order to make the selection. READKNOB is probably not needed, that is used to poll the hardware at a reasonable rate, rather than the 60 FPS of the display loop.

The most difficult part of this project was setting up automatic login from the server to the clients. Notes on how I did that are below.

### Server dependencies
The following should be installed on the server Pi:
- [Paralell-SSH](http://parallel-ssh.readthedocs.io/en/latest/index.html) for connecting to the clients
- [Pi 3D](https://pi3d.github.io/html/) to display the interface elements

### Client dependencies
- [omxplayer](https://github.com/popcornmix/omxplayer)
- [dbuscontrol.sh](https://github.com/popcornmix/omxplayer) install dbuscontrol.sh at the root of each client machine

### Setting up the Server to log in automatically

I generated ssh keys to allow me to start a ssh Terminal session from my MacBook and connect to the server without a password prompt. You should be able to enter `ssh pi@server.local` and log in with no warnings. Do that first, so that you can understand the process of generating and copying keys. Once that is working, you do the same process from the server Pi's terminal to each client. 

Follow the instructions here for to allow [remote access without passwords](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md) on the clients. I was able to use those instructions to do the same on my mac as well.

On the mac, make sure the username you use matches, i.e. bryan@bryans-macbook-2015 where the instructions above say say eben@pi
Once you've done this, if the Terminal keeps asking for a password enter:

```
ssh-add
```
If you get warnings from the mac about suspicious behaviors after swapping out SD cards on the Pi, you need to add/update the pi in the mac's keychain. In Terminal:
`ssh-keygen -f "/Users/bryan/.ssh/known_hosts" -R server.local`

When doing this from the server pi to the clients, use the command:
`ssh-keygen -f "/home/pi/.ssh/known_hosts" -R client0.local`

On the Pi, the `ssh-add` command would not work returning `could not connect agent`.  This seems to mean that the ssh-agent is not running. You need to start it up first:
```
pi@server: exec ssh-agent bash
pi@server: ~/.ssh $ ssh-add
```
This page has some helpful instructions for how to [automatically run ssh-add without a prompt](https://unix.stackexchange.com/questions/90853/how-can-i-run-ssh-add-automatically-without-password-prompt). 

You will need to generate a key on the serving machine and then send it over to the client machine, making sure that you have already  set  the client Pi to allow empty passwords. 

From the server, follow instructions to [remote access without passwords](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md) in order to log in into the client machine without a password prompt. You'll need to set up each client to allow empty passwords : `sudo nano /etc/ssh/sshd_config` , look for the option to do so in that file.

Copy over the id_rsa.pub to the client machine as instructed in that article. Technically, you can leave the server’s sshd_config as is, just the client needs to allow no password, but following these instructions I set up the server to allow my mac to login without a prompt as well.

#### Setting up a client Pi:

1. Install [jessie or stretch](https://www.raspberrypi.org/documentation/installation/installing-images/), NOT jessie-lite or stretch-lite, omxplayer needs some things.
2. Set the pi up so it does not launch Pixel desktop
3. Create a .ssh folder
```
cd ~
install -d -m 700 ~/.ssh
```
4. Set sshd_config to allow no password : `sudo nano /etc/ssh/sshd_config`
5. From the server pi, [copy over the id_rsa.pub key to the client](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)
6. Install [dbuscontrol.sh](https://github.com/popcornmix/omxplayer)
```
sudo nano ~/dbuscontrol.sh
sudo chmod 755 ~/dbuscontrol.sh
```
7. Create a [mount point](https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=38058) for the USB drive, where we will store our videos 
   - On the Pi make a directory: `sudo mkdir -p /mnt/usb`
   - Then set it to start up and mount to that directory: `sudo nano /etc/fstab`
   - Add this line to the end of fstab: `/dev/sda1 /mnt/usb vfat defaults,nofail 0 2`
   - This setup assumes there is only one usb drive plugged in and it's going to be called `sda`.

If you get errors running dbuscontrol from your scripts, you might need to run omxplayer as sudo.

### Preparing the USB Drives

The clients each expect to have a USB stick with a folder called 'media'. In the media folder, there should be an 'intro.mp4' and child folders corresponding to the names of the 3D models in 'main.py', i.e. gun, cake, fork, knife and bear.  
- media
  - gun
    - mov_01.mp4
    - mov_02.mp4
    - etc..
  - cake
  - fork
  - knife
  - bear
  - intro.mp4

Each folder has the same number of videos, numbered in sequence starting with 'mov_01.mp4'. The script randomly picks and plays from those folders.


### Setting up WIFI on all the machines

Add wifi login information to each clients' wpa_supplicant.conf file
```
wpa_passphrase "YOUR_WIFI_NETWORK" "YOUR_PASSWORD" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null 
```
After doing that, you can check what was added :
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
### Automatically running the script on Startup

Writing the command:
```
sleep 10
python naropa_installation/main.py
```
into `nano ~/.bashrc` works, but it runs with each login. You may have to change [ownership and permissions](https://raspberrypi.stackexchange.com/questions/12853/automatically-run-a-program-as-root-for-gpio) on the main.py and Client scripts for that to work, since the server is using the GPIO pins.

I would love a pull request with a better startup script idea. Seems like there are too many ways to do this on the Raspberry Pi, and many all have issues with permissions, user, etc. For example, adding this to `/etc/rc.local` did not seem to work:
```
startscript(){
  sleep 10
  XAUTHORITY=~pi/.Xauthority DISPLAY=:0 python /home/pi/naropa_installation/main.py
  exit 1
}
startscript&
exit 0
```
The SSH script could not connect to the clients, I'm sure it's because the ssh keys are generated from 'pi' user, not root, and starting up is done by root. Putting the commands to [log into the LXDE](http://www.opentechguides.com/how-to/article/raspberry-pi/5/raspberry-pi-auto-start.html) environment allowed SSH to connect, the clients launched their videos. But, the server display did not show the interface. I could not figure out why not. 

Unless someone is trying to do the same thing, i.e. connect via SSH at startup, use the server as the main display, etc., it's difficult to parse where the problem lies and what the best approach might be to run this at startup. Using `~/.bashrc` is OK, but since the display is running as root, it won't respond to keyboard commands. Logging in via another machine, causes a new instance to run, which does respond to keyboard commands, but leaves the first instance running. To quit, you have to:
```
ps aux | less
```
Find the UID of the process
```
killall -9 [UID]
``` 


