import socket
import selectors
import types
import tkinter
from tkinter import messagebox, filedialog
import pickle
import struct
from PIL import Image
from PIL import ImageTk
import datetime

HOST = '127.0.0.1'
PORT = 65432
messages = []
sel = selectors.DefaultSelector()
connid=0
CUR_AUCTION = ''
USERNAME = ''
PASSWORD = ''
LOGIN = False
def start_connection():
    server_addr = (HOST, PORT)
    print('Starting connection'
          '\nConnection ID:',connid,
          '\nConnecting to:',server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(True)
    sock.connect_ex(server_addr)

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(connid=connid,
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
    sel.register(sock, events, data=data)

    return sock

sock = start_connection()

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('Received', repr(recv_data), 'from connection', data.connid)
            data.recv_total += len(recv_data)
        if not recv_data:
            print('Closing connection', data.connid)
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop()
        if data.outb:
            print('sending', repr(data.outb),'to connection', data.connid)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

def create_user(username, password):
    pid = 0
    datagram = []
    datagram.append(pid)
    datagram.append(username)
    datagram.append(password)
    data = pickle.dumps(datagram)
    sock.send(data)


class SampleApp(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.geometry('800x600')
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class StartPage(tkinter.Frame):
    def __init__(self, master):
            tkinter.Frame.__init__(self, master)
            tkinter.Label(self, text='Start Page', font=('Helvetica', 18, 'bold')).pack(side='top', fill='x', pady=5)
            tkinter.Button(self, text='Sign Up',
                           command=lambda:master.switch_frame(page_SignUp)).pack()
            tkinter.Button(self, text='Login',
                           command=lambda:master.switch_frame(page_Login)).pack()

class StartPage_2(tkinter.Frame):
    def __init__(self, master):
            tkinter.Frame.__init__(self, master)
            tkinter.Label(self, text='Start Page', font=('Helvetica', 18, 'bold')).pack(side='top', fill='x', pady=5)
            tkinter.Button(self, text='Create Auction',
                           command=lambda: master.switch_frame(createAuction)).pack()
            tkinter.Button(self, text='List of Auctions',
                           command=lambda: master.switch_frame(listAuctions)).pack()



class page_SignUp(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        tkinter.Frame.configure(self, bg='blue')
        tkinter.Label(self, text='Sign Up', font=('Helvetica', 18, 'bold')).pack(side='top', fill='x', pady=5)
        tkinter.Button(self, text='Go Back',
                       command=lambda:master.switch_frame(StartPage)).pack()
        info_box = tkinter.Frame(self)
        info_box.pack()
        tkinter.Label(info_box, text='Username').grid(row=0)
        tkinter.Label(info_box, text='Password').grid(row=1)
        tkinter.Label(info_box, text='Confirm Password').grid(row=2)
        username = tkinter.Entry(info_box)
        password_1 = tkinter.Entry(info_box, show='*')
        password_2 = tkinter.Entry(info_box, show='*')
        username.grid(row=0, column=1)
        password_1.grid(row=1, column=1)
        password_2.grid(row=2, column=1)

        tkinter.Button(info_box, text='Submit',
                       command=lambda :submit_user(username.get(),password_1.get())).grid(row=3)


        def submit_user(username_in, password_in):
            print(username_in,password_in)
            create_user(username_in, password_in)
            master.switch_frame(StartPage)

class page_Login(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        tkinter.Frame.configure(self, bg='red')
        tkinter.Label(self, text='Login', font=('Helvetica', 18, 'bold')).pack(side='top', fill='x', pady=5)
        tkinter.Button(self, text='Go Back',
                       command=lambda:master.switch_frame(StartPage)).pack()

        info_box = tkinter.Frame(self)
        info_box.pack()
        tkinter.Label(info_box, text='Username').grid(row=0)
        tkinter.Label(info_box, text='Password').grid(row=1)

        username = tkinter.Entry(info_box)
        password = tkinter.Entry(info_box, show='*')
        username.grid(row=0, column=1)
        password.grid(row=1, column=1)

        tkinter.Button(info_box, text='Login',
                       command=lambda: check_credentials(username.get(),password.get())).grid(row=3,column=1)

        def check_credentials(username_i, password_i):
            pid = 1
            datagram = []
            datagram.append(pid)
            datagram.append(username_i)
            datagram.append(password_i)
            data = pickle.dumps(datagram)
            sock.send(data)

            confirm = str(sock.recv(4096))
            confirm = confirm.split('b')[1]
            confirm = int(confirm[1])

            if confirm == 1:
                LOGIN = True
                USERNAME = username_i
                PASSWORD = password_i
                master.switch_frame(StartPage_2)
            else:
                tkinter.messagebox.showerror('Login Error',"User name and password does not match")

class createAuction(tkinter.Frame):
    def __init__(self, master):
        path = ''
        tkinter.Frame.__init__(self, master)

        form = tkinter.Frame(self)
        form.pack()
        tkinter.Label(form, text='Item Name').grid(row=0)
        tkinter.Label(form, text='Image').grid(row=1)
        tkinter.Label(form, text='Description').grid(row=2)
        tkinter.Label(form, text='Starting Price').grid(row=3)
        tkinter.Label(form, text='Duration').grid(row=4)

        name = tkinter.Entry(form)
        name.grid(row=0, column=1)
        tkinter.Button(form, text='Add Image',
                       command=lambda: choose_file()).grid(row=1, column=1)
        desc = tkinter.Entry(form)
        desc.grid(row=2, column=1)
        price = tkinter.Entry(form)
        price.grid(row=3, column=1)
        duration = tkinter.Entry(form)
        duration.grid(row=4, column=1)
        tkinter.Button(form, text='Start Auction',
                       command=lambda :submit_auction()).grid(row=5, column=1)


        def choose_file():
            self.path = filedialog.askopenfilename()
            print(self.path)
        def submit_auction():
            pid = 2
            datagram = []
            datagram.append(pid)
            datagram.append(name.get())
            datagram.append(desc.get())
            datagram.append(price.get())
            datagram.append(duration.get())

            print(self.path)
            image_file = open(self.path, 'rb')
            bytes = image_file.read()
            size = struct.pack('!i',len(bytes))
            data = pickle.dumps(datagram)
            sock.send(data)

            sock.send(size)

            sock.send(bytes)

class listAuctions(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)
        command = []
        command.append(3)
        data = pickle.dumps(command)
        sock.send(data)

        recv_data = sock.recv(4096)
        inc_data = pickle.loads(recv_data)
        number_of_auctions = len(inc_data)

        LB = tkinter.Listbox(self)
        for i in range(0,number_of_auctions):
            LB.insert(i, inc_data[i])
        LB.pack()
        b1 = tkinter.Button(self, text='Choose',
                            command=lambda : make_selection()).pack()
        b2 = tkinter.Button(self, text='Back',
                            command=lambda : master.switch_frame(StartPage_2)).pack()
        def make_selection():
            set_auction(LB.get(LB.curselection()))
            master.switch_frame(viewAuction)

def set_auction(name):
    global CUR_AUCTION
    CUR_AUCTION = name
def get_auction():
    return CUR_AUCTION

class viewAuction(tkinter.Frame):
    def __init__(self, master):
        global CUR_AUCTION
        tkinter.Frame.__init__(self, master)
        pid = 4
        command = []
        command.append(pid)
        cur_auction = get_auction()
        command.append(cur_auction)
        data = pickle.dumps(command)
        sock.send(data)

        recv_data = sock.recv(4096)
        contents = pickle.loads(recv_data)
        print(contents)

        size = sock.recv(4)
        size = struct.unpack('!i',size)[0]
        print(size)
        img_data=b''
        img_path = contents[0]+'.png'
        while size > 0:
            if size >= 4096:
                data = sock.recv(4096)
            else:
                data = sock.recv(size)

            if not data:
                break

            size -= len(data)
            img_data += data
        f_img = open(img_path,'wb')
        f_img.write(img_data)
        f_img.close()

        info = tkinter.Frame(self)
        info.pack()
        tkinter.Label(info, text='Item Name:').grid(row=0)
        tkinter.Label(info, text='Description:').grid(row=1)
        tkinter.Label(info, text='Starting Price:').grid(row=2)
        tkinter.Label(info, text='Duration:').grid(row=3)

        tkinter.Label(info, text=contents[0], fg='green').grid(row=0, column=1)
        tkinter.Label(info, text=contents[1], fg='green').grid(row=1, column=1)
        tkinter.Label(info, text=contents[2], fg='green').grid(row=2, column=1)
        tkinter.Label(info, text=contents[3], fg='green').grid(row=3, column=1)

        img = ImageTk.PhotoImage(Image.open(img_path).resize((100,100), Image.ANTIALIAS))
        panel = tkinter.Label(info, image=img)
        panel.image = img
        panel.grid(row=4)

        tkinter.Label(info, text='Current Bid:').grid(row=5)
        tkinter.Label(info, text=contents[4], fg='green').grid(row=5,column=1)
        tkinter.Label(info, text='Input Offer:').grid(row=6)
        offer = tkinter.Entry(info)
        offer.grid(row=6, column=1)
        tkinter.Button(info, text='Make Offer',
                       command=lambda: make_offer()).grid(row=7)

        tkinter.Button(info, text='Back',
                       command=lambda: master.switch_frame(listAuctions)).grid(row=7, column=1)

        tkinter.Button(info, text='Refresh',
                       command= lambda :master.switch_frame(viewAuction)).grid(row=8)

        def make_offer():
            pid = 5
            datagram = []
            datagram.append(pid)
            datagram.append(contents[0])
            datagram.append(offer.get())
            data = pickle.dumps(datagram)

            sock.send(data)
            master.switch_frame(viewAuction)


app = SampleApp()
app.mainloop()

messages = []
connid = int(input('Enter ID for Connection'))
message = input('Enter Message:')

messages.append(bytes(message, encoding='ascii'))



try:
    while True:

        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
                key.data.messages.append(bytes(input('Enter message'),encoding='ascii'))
        if not sel.get_map():
            break

except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
