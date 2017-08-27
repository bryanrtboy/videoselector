## Video Selector

This project uses a Raspberry Pi 3 as a server/controller to play videos on 5 client Pi's connected via a WIFI network. This set of python scripts is running on the server. The server is hooked up to a rotary encoder and two buttons. The rotary dial allows the user to scroll through 3D models rendered on screen, a button is then used to make a selection. Once the button is pressed, a video on one of the client machines starts up. The second button shuts down all of the clients, and then the server.

### Setting up the Server to log in automatically

I generated ssh keys to allow me to start a ssh Terminal session from my MacBook and connect to the server without a password prompt. Do that first, so that you can understand the process of generating and copying keys. Once that is working, you do the same process from the server Pi's terminal to each client. [Remote access without passwords](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md)

On the mac, make sure the username you use matches, i.e. bryan@bryans-macbook-2015 where the instructions above say say eben@pi
Once you've done this, if the Terminal keeps asking for a password enter:
```ssh-add
```
On the Pi, the `ssh-add` command would not work returning `could not connect agent`.  This seems to mean that the ssh-agent is not running. You need to start it up first:
```
pi@server: exec ssh-agent bash
pi@server: ~/.ssh $ ssh-add
```
This page has some helpful instructions for how to [automatically run ssh-add without a prompt](https://unix.stackexchange.com/questions/90853/how-can-i-run-ssh-add-automatically-without-password-prompt). 

You will need to generate a key on the serving machine and then send it over to the client machine, making sure that you have already  set  the client Pi to allow empty passwords. 

From the server, log in into the client machine:
```sudo nano /etc/ssh/sshd_config
```
Set it to allow empty passwords. Follow the instructions for the server [here](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md) Copy over the id_rsa.pub to the client machine as instructed in that article. You can leave the server’s sshd_config as is, just the client needs to allow no password. 

#### Set up steps for the client machines:
1. Install jessie
2. Create a .ssh folder
`cd ~`
`install -d -m 700 ~/.ssh`
3. Set sshd_config to allow no password on the cl
4. On the server pi, copy over the id_rsa.pub key to the client1 pi
5. Install [dbuscontrol.sh](https://github.com/popcornmix/omxplayer)
`sudo nano ~/dbuscontrol.sh`
`sudo chmod 755 ~/dbuscontrol.sh`
You might need to run omxplayer as sudo if you get dbuscontrol errors


### Setting up WIFI on all the machines

Add wifi login information to each clients' wpa_supplicant.conf file
```
wpa_passphrase "YOUR_WIFI_NETWORK" "YOUR_PASSWORD" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null 
```
After doing that, you can check what was added :
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block
There is not much special about the client Pi systems, but they need to be set up without a password so that the server can automatically connect.

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/bryanrtboy/videoselector/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
