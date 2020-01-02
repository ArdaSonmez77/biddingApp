import socket
import selectors
import types
import pickle
import struct

INFO_PATH = 'INFO.txt'

def number_of_auctions():
    f = open(INFO_PATH,'r')
    content = f.read().splitlines()
    f.close()
    return len(content)
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
    print(INFO_PATH)
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

def create_auction(a_name, a_desc, a_price, a_duration, sock):
    path = 'Auctions\\'+a_name+'.txt'
    img_path = 'Auctions\\'+a_name+'.png'
    f = open(path, 'a')
    f.write(a_name)
    f.write('\n')
    f.write(a_desc)
    f.write('\n')
    f.write(a_price)
    f.write('\n')
    f.write(a_duration)
    f.write('\n')
    f.close()
    f.write(a_price)
    f.write('\n')

    f_img = open(img_path,'wb')
    size = sock.recv(4)
    size = struct.unpack('!i', size)[0]
    img_data = b''
    while size > 0 :
        if size >= 4096:
            data = sock.recv(4096)
        else:
            data = sock.recv(size)

        if not data:
            break

        size -= len(data)
        img_data += data
    f_img.write(img_data)
    f_img.close()

    f_info = open(INFO_PATH,'a')
    f_info.write(a_name)
    f_info.write('\n')
    f_info.close()

    return 1

def send_list(sock):
    f = open(INFO_PATH, 'r')
    content = f.read().splitlines()
    contents = pickle.dumps(content)
    f.close()
    sock.send(contents)

def send_auction(inc_data, sock):
    path = 'Auctions\\'+inc_data[1]+'.txt'
    f = open(path, 'r')
    content = f.read().splitlines()
    contents = pickle.dumps(content)
    f.close()
    sock.send(contents)

    path_img = 'Auctions\\'+inc_data[1]+'.png'
    f_img = open(path_img, 'rb')
    img_bytes = f_img.read()
    size = struct.pack('!i',len(img_bytes))
    sock.send(size)

    sock.send(img_bytes)

def update_offer(a_name,new_value, sock):
    path = 'Auctions\\'+a_name+'.txt'
    f = open(path, 'r')
    data = f.readlines()
    f.close()
    data[4] = new_value

    with open(path,'w') as file:
        file.writelines(data)


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
            elif inc_data[0] == 2:
                print(len(inc_data))
                create_auction(inc_data[1], inc_data[2], inc_data[3], inc_data[4],sock)
            elif inc_data[0] == 3:
                send_list(sock)
            elif inc_data[0] == 4:
                send_auction(inc_data, sock)
            elif inc_data[0] == 5:
                update_offer(inc_data[1], inc_data[2], sock)




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
