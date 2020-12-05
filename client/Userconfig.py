import pickle
from pathlib import Path

class Userconfig:
    def __init__(this):
        try:
            configfile=open(Path.joinpath(Path(__file__).parent.absolute(),'configfile'),'rb')
            saved_conf=pickle.load(configfile)
            this.config_=saved_conf
            configfile.close()
        except Exception as e:
            this.config_={
                'show_usernames':False
            }
            this.savec()

    def setv(this,key_,value_):
        if key_ in this.config_:
            if key_=='show_usernames':
                this.config_['show_usernames']=True if value_.lower() in ('true','1','yes') else False
            this.savec()
        else:
            raise KeyError(f'Invalid variable {key_}')

    def getv(this,key_):
        try:
            this.config_[key_]
            return this.config_[key_]
        except KeyError:
            raise KeyError(f'Invalid variable {key_}')

    def savec(this):
        configfile=open(Path.joinpath(Path(__file__).parent.absolute(),'configfile'),'wb')
        pickle.dump(this.config_,configfile)
        configfile.close()

    def __repr__(this):
        return str(this.config_)
