try:
    import socketio
    from aiohttp import web
    import jwt

    from sqlalchemy import (create_engine,Table,Column,String,Time,MetaData)
    from sqlalchemy.exc import SQLAlchemyError
    from datetime import datetime

    import bcrypt

    # Database
    engine=create_engine('postgres://wjqxxnmi:CePq1Ir_WsuPcxcLnpz3dS8C86p1GZWR@suleiman.db.elephantsql.com:5432/wjqxxnmi')
    meta=MetaData()

    # Setup Table messages
    messages=Table('messages',meta,
    Column('timestamp',Time,primary_key=True),
        Column('sent',String),
        Column('received',String),
        Column('message',String),
    )

    # Setup Table users
    users=Table('users',meta,
        Column('username',String,primary_key=True),
        Column('name',String),
        Column('password',String)
    )

    # Create Tables
    meta.create_all(engine)

    conn=engine.connect()

    # Setup socketio server
    sio = socketio.AsyncServer(async_mode='aiohttp')

    # Setup Web Server
    app = web.Application()
    sio.attach(app)

    # Initialize session variables
    usernames=dict() # usernames -> sid
    ids=dict() # sid -> username

    # JWT secret for encrypting/decrypting
    jwtsecret='secret'

    # socketio handlers
    @sio.on('connect')
    def handle_connect(sid,env):
        print('new connection')

    @sio.on('disconnect')
    def handle_disconnect(sid):
        try:
            del usernames[ids[sid]]
            del ids[sid]
        except:
            pass
        finally:
            print('disconnection')

    @sio.on('message')
    async def handle_message(sid,data):
        if 'room' in data and room!=None:
            conn.execute(messages.insert().values(timestamp=datetime.utcnow(),sent=ids[sid],received=data['connection'],message=data['message']))
            await sio.emit('msg',data['message'],room=data['room'],skip_sid=sid)
        else:
            await sio.emit('err','Not connected\nType `:connect [username]` to connect',room=sid)        


    @sio.on('command')
    async def handle_command(sid,command):
        if command['type']=='login':
            try:
                user=conn.execute(users.select().where(users.c.username==command['username'])).fetchone()
                if user:
                    if bcrypt.checkpw(command['password'].encode(),user.password.encode()):
                        token=jwt.encode({'username':command['username']},jwtsecret,algorithm='HS256')
                        if token:
                            ids[sid]=command['username']
                            usernames[command['username']]=sid
                            await sio.emit('authenticated',token.decode('utf-8'),room=sid)
                        else:
                            await sio.emit('err','Failed to generate token')
                    else:
                        await sio.emit('authenticated',False)
                else:
                    await sio.emit('err','Username not found')
            except Exception as e:
                print(e)
                await sio.emit('err','Unknown error')
        elif command['type']=='signup':
            try:
                command['username']
                command['name']
                command['password']
                hashed_pass=bcrypt.hashpw(command['password'].encode(),bcrypt.gensalt(10)).decode('utf-8')
                conn.execute(users.insert().values(username=command['username'],name=command['name'],password=hashed_pass))
                await sio.emit('signed',{'success':True},room=sid)
            except SQLAlchemyError as e:
                if e.code=='gkpg':
                    await sio.emit('signed',{'success':False,'error':'Username exists'})
                else:
                    print(e)
                    await sio.emit('signed',{'success':False,'error':'DB Error'})
            except KeyError as e:
                await sio.emit('signed',{'success':False,'error':'Insufficient values'})
            except Exception as e:
                await sio.emit('signed',{'success':False,'error':e})

        elif command['type']=='user':
            cmd,*cargs=command['command'].split(' ')
            if cmd=='help':
                sio.emit('info','help')
            elif cmd=='connect':
                try:
                    payload=jwt.decode(command['token'],jwtsecret,algorithms=['HS256'])
                    if payload['username'] == cargs[0]:
                        await sio.emit('err','Cannot connect to self')
                    else:
                        room_name="".join(sorted(payload['username']+cargs[0]))
                        sio.enter_room(usernames[cargs[0]],room_name)
                        sio.enter_room(sid,room_name)
                        messages=conn.execute(messages.select().where(messages.c.sent in (payload['username'],cargs[0],) and messages.c.received in (cargs[0],payload['username'],)))
                        await sio.emit('info',{'info':'connected','room':room_name,'connection':payload['username'],'connected':cargs[0],messages: messages},room=room_name)
                except Exception as e:
                    print(e)
                    await sio.emit('err','Invalid token',room=sid)
            else:
                # print(f'{sid} command: {command}')
                await sio.emit('err',f'Invalid command: {command}')

    # Starting web server
    if __name__=='__main__':
        web.run_app(app,port=5001)

except ImportError as ie:
    print(e)
    print("requiremnts.txt is not supported. Revert to manual installation")