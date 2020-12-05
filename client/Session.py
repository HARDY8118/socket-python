class Session():
    def __init__(this,sid,token):
        this.__sid=sid
        this.__rid=None
        this.__token=token
        this.__connection=None
    
    def set_room(this,rid):
        this.__rid=rid

    def get_room(this):
        return this.__rid

    def destroy(this):
        this.__token=None

    def get_token(this):
        return this.__token
    
    def get_connection(this):
        return this.__connection

    def set_connection(this,connected):
        return this.__connection

    def __repr__(this):
        return this.__token    
