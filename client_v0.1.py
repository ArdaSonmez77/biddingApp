import socket
import selectors
import types
import tkinter


HOST = '127.0.0.1'
PORT = 65432

sel = selectors.DefaultSelector()

def start_connection():
    server_addr = (HOST, PORT)
    print('Starting connection'
          '\nConnection ID:',connid,
          '\nConnecting to:',server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(connid=connid,
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
    sel.register(sock, events, data=data)

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

#master = tkinter.Tk(className='Client Interface')
#master.geometry('1366x768')

#signUP = tkinter.Button(master, text='Sign Up', width=25)
#signUP.pack()

#master.mainloop()
messages = []
connid = int(input('Enter ID for Connection'))
message = input('Enter Message:')

messages.append(bytes(message, encoding='ascii'))

start_connection()

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