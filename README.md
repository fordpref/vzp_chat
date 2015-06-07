# vzp_chat
shitty little fun project to make a VERY basic peer to peer chat. linux is better, but does work in windows but you will need the module from here for curses:  http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses

Usage:  python chat-main.py
/addpeer to connect to another client
/quit to quit
/nick to change your username


uses a simple chatui in cursses from:  https://github.com/calzoneman/python-chatui
threads out the network listener to take input from the network separate from the keyboard.

listens and connects on udp 2288

Working on a few more features, and working on some bug stuff with curses in windows to get it working there.
Going to firewall it up also with iptables so that it won't listen for a peer unless told to do so.  

The program is very basic and likely easily exploitable.
