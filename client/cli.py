import socketio
from Session import Session
from getpass import getpass

sio=socketio.Client()

session=None

from Userconfig import Userconfig
conf=Userconfig()

username=None

@sio.on('connect')
def handle_connect_client():
    print('Connecting...')

@sio.on('connect_error')
def handle_connect_error_client(e):
    print('Error connecting')
    # print(e)

@sio.on('disconnect')
def handle_disconnect_client():
    print('disconnecting')

@sio.on('msg')
def handle_msg_client(msg):
    print('\r>>',msg)

@sio.on('info')
def handle_info_client(info):
    global session,username
    if info['info']=='connected':
        if 'room' in info:
            session.set_room(info['room'])
        if 'connected' in info:
            session.set_connection(info['connected'])
            print(f":::::::: Connected with {info['connected'] if username==info['connection'] else info['connection']}")

@sio.on('err')
def handle_err_client(err):
    print(f'err: {err}')
    exit()

def exec_command(session,command):
    cmd,*arg=command.split(' ')
    if cmd == 'exit':
        print('Disconnecting...')
        sio.disconnect()
        sio.eio.disconnect(True)
        print('Exiting...')
        exit()
    elif cmd == 'set':
        try:
            if '=' in arg[0]:
                arg,val=arg[0].split('=')
                conf.setv(arg,val)
            else:
                conf.setv(arg[0],arg[1])
            conf.savec()
        except:
            pass
    elif cmd == 'disconnect':
        session.set_room(None)
        session.set_connection(None)
    else:
        sio.emit('command',{'type':'user','token':session.get_token(),'command':command})

def auth():
    global username
    authType=input('Login/Signin ').lower()

    if authType=='l' or authType=='login':
        username=input('Username: ')
        password=getpass(prompt='Password: ')

        sio.emit('command',{'type':'login','username':username,'password':password,'sid':sio.sid})

        @sio.event
        def authenticated(token):
            global session
            print(f'Welcome {username}')
            if token:
                session=Session(sid=sio.sid,token=token)
                while True:
                    if conf.getv('show_usernames'):
                        print('\r(',username,')<',sep='',end='')
                        m=input()
                    else:
                        m=input('\r<')
                    if m.startswith(':'):
                        exec_command(session,m[1:])
                    else:
                        sio.emit('message',{'token':session.get_token(),'message':m,'room':session.get_room(),'connection':session.get_connection()})
            else:
                print('Unauthorized')
                auth()
    elif authType=='s' or authType=='signup':
        name=input('Name: ')
        username=input('Username: ')
        password=getpass(prompt='Password: ')

        sio.emit('command',{'type':'signup','name':name,'username':username,'password':password})

        @sio.event
        def signed(data):
            if data['success']:
                print('Signed up successfully')
                auth()
            else:
                print(data['error'])
                exit()
    else:
        auth()

if __name__ == "__main__":
    try:
        sio.connect('http://127.0.0.1:5001')
        auth()
    except Exception as e:
        print(e)
