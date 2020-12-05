from sqlalchemy import create_engine
from sqlalchemy import (Table,Column,String,Time,MetaData)
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

engine=create_engine('postgres://wjqxxnmi:CePq1Ir_WsuPcxcLnpz3dS8C86p1GZWR@suleiman.db.elephantsql.com:5432/wjqxxnmi')

meta=MetaData()

messages=Table('messages',meta,
Column('timestamp',Time,primary_key=True,default=datetime.utcnow()),
    Column('sent',String),
    Column('received',String),
    Column('message',String),
)

users=Table('users',meta,
    Column('username',String,primary_key=True),
    Column('name',String),
    Column('password',String)
)

meta.create_all(engine)

conn=engine.connect()

try:
    # print(conn.execute(messages.insert().values(sent='abc',received='xyz',message='lmao')))
    print(conn.execute(users.insert().values(username='zyx',name=1234,password='$2b$04$DrLvgnJ.gldN/MOFp66Bf.5adbhY4x./zafgZid6.jB6Ja/4za1RC')))
except SQLAlchemyError as e:
    if e.code=='gkpj':
        print('Username duplicate')
        print(e)
    else:
        print(e.__dict__)

# print(users)
# # us=users.query.with_entities(users.username,users.password)
# us=conn.execute(users.select().where(users.c.username=='xyz')).fetchone()
# print(us)
# # print(us)
# for u in us:
#     print(u)
