import socket
import selectors
import types
import pickle



def accept_wrapper(sock):
    conn, addr = sock.accept()
    print('Accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def create_user(username, password):
    f_users = open("users.txt", 'a')
    user = username+'--'+password
    print(user)
    f_users.write(str(user))
    f_users.write('\n')
    f_users.close()
def check_credentials(username, password):
    f_users = open("users.txt", 'r')
    content = f_users.read().splitlines()
    print(content)
    for i in range(0, len(content)):
        cur = content[i]
        curr = cur.split('--')
        cur_username = curr[0]
        cur_password = curr[1]
        if cur_username == username:
            if cur_password == password:
                return 1
    return 0

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(4096)
        inc_data = pickle.loads(recv_data)
        print(inc_data)
        if recv_data:
            if inc_data[0] == 0:
                create_user(inc_data[1], inc_data[2])
            elif inc_data[0] == 1:
                sock.send(bytes(str(check_credentials(inc_data[1], inc_data[2])),'utf-8'))



        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


HOST = '127.0.0.1'
PORT = 65432

sel = selectors.DefaultSelector()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print('Listening on', (HOST, PORT))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
