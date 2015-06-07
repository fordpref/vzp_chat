import socket, sys, curses, threading


class ChatUI:
    ''' borrowed the object and some chat code from https://github.com/calzoneman/python-chatui '''
    def __init__(self, stdscr, userlist_width=16):
        self.stdscr = stdscr
        self.userlist = []
        self.inputbuffer = ""
        self.linebuffer = []
        self.chatbuffer = []

        # Curses, why must you confuse me with your height, width, y, x
        userlist_hwyx = (curses.LINES - 2, userlist_width - 1, 0, 0)
        chatbuffer_hwyx = (curses.LINES - 2, curses.COLS-userlist_width-1,
                           0, userlist_width + 1)
        chatline_yx = (curses.LINES - 1, 0)
        self.win_userlist = stdscr.derwin(*userlist_hwyx)
        self.win_chatline = stdscr.derwin(*chatline_yx)
        self.win_chatbuffer = stdscr.derwin(*chatbuffer_hwyx)
        
        self.redraw_ui()

    def resize(self):
        """Handles a change in terminal size"""
        u_h, u_w = self.win_userlist.getmaxyx()
        h, w = self.stdscr.getmaxyx()

        self.win_chatline.mvwin(h - 1, 0)
        self.win_chatline.resize(1, w)

        self.win_userlist.resize(h - 2, u_w)
        self.win_chatbuffer.resize(h - 2, w - u_w - 2)

        self.linebuffer = []
        for msg in self.chatbuffer:
            self._linebuffer_add(msg)

        self.redraw_ui()

    def redraw_ui(self):
        """Redraws the entire UI"""
        h, w = self.stdscr.getmaxyx()
        u_h, u_w = self.win_userlist.getmaxyx()
        self.stdscr.clear()
        self.stdscr.vline(0, u_w + 1, "|", h - 2)
        self.stdscr.hline(h - 2, 0, "-", w)
        self.stdscr.refresh()

        self.redraw_userlist()
        self.redraw_chatbuffer()
        self.redraw_chatline()

    def redraw_chatline(self):
        """Redraw the user input textbox"""
        h, w = self.win_chatline.getmaxyx()
        self.win_chatline.clear()
        start = len(self.inputbuffer) - w + 1
        if start < 0:
            start = 0
        self.win_chatline.addstr(0, 0, self.inputbuffer[start:])
        self.win_chatline.refresh()

    def redraw_userlist(self):
        """Redraw the userlist"""
        self.win_userlist.clear()
        h, w = self.win_userlist.getmaxyx()
        for i, name in enumerate(self.userlist):
            if i >= h:
                break
            #name = name.ljust(w - 1) + "|"
            self.win_userlist.addstr(i, 0, name[:w - 1])
        self.win_userlist.refresh()
    def get_userlist(self):
        ''' return the userlist '''
        return(self.userlist)

    def redraw_chatbuffer(self):
        """Redraw the chat message buffer"""
        self.win_chatbuffer.clear()
        h, w = self.win_chatbuffer.getmaxyx()
        j = len(self.linebuffer) - h
        if j < 0:
            j = 0
        for i in range(min(h, len(self.linebuffer))):
            self.win_chatbuffer.addstr(i, 0, self.linebuffer[j])
            j += 1
        self.win_chatbuffer.refresh()

    def chatbuffer_add(self, msg):
        """
        Add a message to the chat buffer, automatically slicing it to
        fit the width of the buffer
        """
        self.chatbuffer.append(msg)
        self._linebuffer_add(msg)
        self.redraw_chatbuffer()
        self.redraw_chatline()
        self.win_chatline.cursyncup()

    def _linebuffer_add(self, msg):
        h, w = self.stdscr.getmaxyx()
        u_h, u_w = self.win_userlist.getmaxyx()
        w = w - u_w - 2
        while len(msg) >= w:
            self.linebuffer.append(msg[:w])
            msg = msg[w:]
        if msg:
            self.linebuffer.append(msg)

    def prompt(self, msg):
        """Prompts the user for input and returns it"""
        self.inputbuffer = msg
        self.redraw_chatline()
        res = self.wait_input()
        res = res[len(msg):]
        return res

    def wait_input(self, prompt=""):
        """
        Wait for the user to input a message and hit enter.
        Returns the message
        """
        global sock, server_address
        self.inputbuffer = prompt
        self.redraw_chatline()
        self.win_chatline.cursyncup()
        last = -1
        while last != ord('\n'):
            last = self.stdscr.getch()
            if last == ord('\n'):
                tmp = self.inputbuffer
                self.inputbuffer = ""
                self.redraw_chatline()
                self.win_chatline.cursyncup()
                return tmp[len(prompt):]
            elif last == curses.KEY_BACKSPACE or last == 127:
                if len(self.inputbuffer) > len(prompt):
                    self.inputbuffer = self.inputbuffer[:-1]
            elif last == curses.KEY_RESIZE:
                self.resize()
            elif 32 <= last <= 126:
                self.inputbuffer += chr(last)
            self.redraw_chatline()




def netchat():
    global peerlist, ui, sock, threadkill, name, ipaddr
    #Get data from sockets and add to input
    while threadkill == '':
        data, address = sock.recvfrom(16384)
        checkuser = data.split('> ')
        if data.startswith('/'):
            data = data.split(' ')
            if "/addpeer" in data:
                if data[1] == ipaddr and address not in peerlist:
                    peerlist.append(address)
                else:
                    peer = (data[1], 2288)
                    peerlist.append(peer)
                ui.userlist.append(data[2])
                ui.redraw_userlist()
                ui.chatbuffer_add('added peer from ' + data[2] + ': ' + data[1])
        elif checkuser[0] not in ui.userlist:
            ui.userlist.append(checkuser[0])
            ui.redraw_userlist()
            if address not in peerlist:
                peerlist.append(address)
            ui.chatbuffer_add(data)
        else:
            ui.chatbuffer_add(data)
            



def commands(inp):
    global peerlist, ui, sock, nc, threadkill, name, ipaddr
    inp = inp.split(' ')
    if "/quit" in inp:
        threadkill = "FUCKING STOP THE THREADS"
        exit()
    elif "/addpeer" in inp:
        if inp[1] not in peerlist:
            peer = (inp[1], 2288)
            peerlist.append(peer)
            ui.chatbuffer_add('added peer: ' + inp[1])
            for peer in peerlist:
                inp = ' '.join(inp)
                inp = inp + ' ' + name
                send = sock.sendto(inp, peer)
    elif '/userlist' in inp:
        users = ', '.join(ui.userlist)
        ui.chatbuffer_add(users)
    return()



def main(stdscr):
    global peerlist, sock, ui, nc, name, ipaddr


    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    server_address = ('', 2288)
    sock.bind(server_address)

    #setup UI, get local username
    stdscr.clear()
    ui = ChatUI(stdscr)
    name = ui.wait_input("Username: ")
    ui.userlist.append(name)
    ui.redraw_userlist()
    inp = ""

    #start netchat thread
    nc = threading.Thread(target=netchat)
    nc.setDaemon(True)
    nc.start()

    while True:
        
        #Get input, append name, send to peers
        inp = ui.wait_input()
        if inp.startswith('/'):
            commands(inp)
        else:
            inp = name + '> ' + inp
            ui.chatbuffer_add(inp)
            if len(peerlist) != 0:
                for peer in peerlist:
                    send = sock.sendto(inp, peer)

        #Command parsing here
        


peerlist = []
threadkill = ''
ipaddr = raw_input('What is your IP address: ')



curses.wrapper(main)
