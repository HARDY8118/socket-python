try:
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets
    import socketio
    from Session import Session
    from getpass import getpass
    import gc
    gc.disable()
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



    def auth(authType,username,password,name=None):
        if authType=='l' or authType=='login':

            sio.emit('command',{'type':'login','username':username,'password':password,'sid':sio.sid})

            @sio.event
            def authenticated(token):
                global session
                if token:
                    session=Session(sid=sio.sid,token=token)
                    # Authenticated
                    # Handle messaging
                   
                else:
                    print('Unauthorized')
                    # Show unauthorized error
                    # Restart

        elif authType=='s' or authType=='signup':
            sio.emit('command',{'type':'signup','name':name,'username':username,'password':password})

            @sio.event
            def signed(data):
                if data['success']:
                    print('Signed up successfully')
                    # Close register window
                    # Open message window
                else:
                    print(data['error'])
                    # Show error
        else:
            exit()
    
    class Ui_chat_win(object):
        def setupUi(self, chat_win):
            self.msgs={'hello':'s','hi':'r','how':'s','where':'r','when':'s'}
            chat_win.setObjectName("chat_win")
            chat_win.resize(420, 399)
            self.centralwidget = QtWidgets.QWidget(chat_win)
            self.centralwidget.setObjectName("centralwidget")
            self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.scrollArea.setGeometry(QtCore.QRect(10, 10, 401, 321))
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 399, 319))
            self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
            self.i=10
            self.j=80
            for msg in self.msgs:
                if self.msgs[msg]=='r':
                    self.recv_msg = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
                    self.recv_msg.setGeometry(QtCore.QRect(10, self.i, 231, 51))
                    self.recv_msg.setObjectName("recv_msg")
                    self.recv_msg.append(msg)
                    self.i+=135
                elif self.msgs[msg]=='s':
                    self.sent_msg = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
                    self.sent_msg.setGeometry(QtCore.QRect(160, self.j, 231, 51))
                    self.sent_msg.setObjectName("sent_msg")
                    self.sent_msg.append(msg)
                    self.j+=135
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.msg_enter = QtWidgets.QTextEdit(self.centralwidget)
            self.msg_enter.setGeometry(QtCore.QRect(10, 340, 331, 51))
            self.msg_enter.setMarkdown("")
            self.msg_enter.setObjectName("msg_enter")
            self.send_butt = QtWidgets.QPushButton(self.centralwidget)
            self.send_butt.setGeometry(QtCore.QRect(350, 340, 61, 51))
            self.send_butt.clicked.connect(self.sendbuttclick)
            font = QtGui.QFont()
            font.setPointSize(9)
            font.setBold(True)
            font.setWeight(75)
            self.send_butt.setFont(font)
            self.send_butt.setObjectName("send_butt")
            chat_win.setCentralWidget(self.centralwidget)

            self.retranslateUi(chat_win)
            QtCore.QMetaObject.connectSlotsByName(chat_win)

        def retranslateUi(self, chat_win):
            _translate = QtCore.QCoreApplication.translate
            chat_win.setWindowTitle(_translate("chat_win", "MainWindow"))
            self.msg_enter.setPlaceholderText(_translate("chat_win", "Enter Message"))
            self.send_butt.setText(_translate("chat_win", "SEND"))
    
        def sendbuttclick(self):
            if len(self.msg_enter.text())!=0:
                self.msgs[self.msg_enter.text()]='s'
                self.sent_msg = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
                self.sent_msg.setGeometry(QtCore.QRect(160, self.j, 231, 51))
                self.sent_msg.setObjectName("sent_msg")
                self.sent_msg.append(self.msg_enter.text())
                self.j+=135

    class Ui_RegWindow(object):
        def setupUi(self, RegWindow):
            RegWindow.setObjectName("RegWindow")
            RegWindow.resize(405, 314)
            self.centralwidget = QtWidgets.QWidget(RegWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.label = QtWidgets.QLabel(self.centralwidget)
            self.label.setGeometry(QtCore.QRect(100, 30, 181, 41))
            font = QtGui.QFont()
            font.setPointSize(16)
            font.setBold(True)
            font.setWeight(75)
            self.label.setFont(font)
            self.label.setObjectName("label")
            self.label_2 = QtWidgets.QLabel(self.centralwidget)
            self.label_2.setGeometry(QtCore.QRect(50, 160, 111, 21))
            font = QtGui.QFont()
            font.setPointSize(11)
            font.setBold(True)
            font.setWeight(75)
            self.label_2.setFont(font)
            self.label_2.setObjectName("label_2")
            self.label_3 = QtWidgets.QLabel(self.centralwidget)
            self.label_3.setGeometry(QtCore.QRect(90, 120, 71, 21))
            font = QtGui.QFont()
            font.setPointSize(11)
            font.setBold(True)
            font.setWeight(75)
            self.label_3.setFont(font)
            self.label_3.setObjectName("label_3")
            self.label_4 = QtWidgets.QLabel(self.centralwidget)
            self.label_4.setGeometry(QtCore.QRect(50, 200, 101, 21))
            font = QtGui.QFont()
            font.setPointSize(11)
            font.setBold(True)
            font.setWeight(75)
            self.label_4.setFont(font)
            self.label_4.setObjectName("label_4")
            self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
            self.lineEdit.setGeometry(QtCore.QRect(160, 120, 151, 22))
            self.lineEdit.setObjectName("lineEdit")
            self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
            self.lineEdit_2.setGeometry(QtCore.QRect(160, 160, 151, 22))
            self.lineEdit_2.setObjectName("lineEdit_2")
            self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
            self.lineEdit_3.setGeometry(QtCore.QRect(160, 200, 151, 22))
            self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
            self.lineEdit_3.setObjectName("lineEdit_3")
            self.pushButton = QtWidgets.QPushButton(self.centralwidget)
            self.pushButton.setGeometry(QtCore.QRect(150, 260, 93, 28))
            self.pushButton.setObjectName("pushButton")
            self.pushButton.clicked.connect(self.regbuttclick)
            RegWindow.setCentralWidget(self.centralwidget)

            self.retranslateUi(RegWindow)
            QtCore.QMetaObject.connectSlotsByName(RegWindow)

        def retranslateUi(self, RegWindow):
            _translate = QtCore.QCoreApplication.translate
            RegWindow.setWindowTitle(_translate("RegWindow", "MainWindow"))
            self.label.setText(_translate("RegWindow", "Registration"))
            self.label_2.setText(_translate("RegWindow", "Username:"))
            self.label_3.setText(_translate("RegWindow", "Name:"))
            self.label_4.setText(_translate("RegWindow", "Password:"))
            self.pushButton.setText(_translate("RegWindow", "Register"))

        def regbuttclick(self):
            global username

            # Close login window
            username=self.lineEdit_2.text()
            password=self.lineEdit_3.text()
            name=self.lineEdit.text()
            auth('s',username,password,name)

    class Ui_chat_un_enter(object):
        def setupUi(self, chat_un_enter):
            chat_un_enter.setObjectName("chat_un_enter")
            chat_un_enter.resize(393, 138)
            self.centralwidget = QtWidgets.QWidget(chat_un_enter)
            self.centralwidget.setObjectName("centralwidget")
            self.text = QtWidgets.QLabel(self.centralwidget)
            self.text.setGeometry(QtCore.QRect(80, 20, 231, 16))
            font = QtGui.QFont()
            font.setPointSize(11)
            self.text.setFont(font)
            self.text.setObjectName("text")
            self.un_enter = QtWidgets.QLineEdit(self.centralwidget)
            self.un_enter.setGeometry(QtCore.QRect(110, 60, 171, 22))
            self.un_enter.setObjectName("un_enter")
            self.proceed_butt = QtWidgets.QPushButton(self.centralwidget)
            self.proceed_butt.setGeometry(QtCore.QRect(150, 100, 93, 28))
            self.proceed_butt.setObjectName("proceed_butt")
            self.proceed_butt.clicked.connect(self.proceedbuttclick)
            chat_un_enter.setCentralWidget(self.centralwidget)

            self.retranslateUi(chat_un_enter)
            QtCore.QMetaObject.connectSlotsByName(chat_un_enter)

        def retranslateUi(self, chat_un_enter):
            _translate = QtCore.QCoreApplication.translate
            chat_un_enter.setWindowTitle(_translate("chat_un_enter", "MainWindow"))
            self.text.setText(_translate("chat_un_enter", "Enter username to chat with"))
            self.proceed_butt.setText(_translate("chat_un_enter", "Proceed"))

        def proceedbuttclick(self):
            un=self.un_enter.text()
            #pass un to the message funtion and return to response
            #if response==approved
            #self.win=QtWidgets.QMainWindow()
            #self.ui=Ui_RegWindow()
            #self.ui.setupUi(self.win)
            #self.win.show()
            #else
            #pass

    class Ui_main_window(object):
        def setupUi(self, main_window):
            main_window.setObjectName("main_window")
            main_window.resize(409, 335)
            self.centralwidget = QtWidgets.QWidget(main_window)
            self.centralwidget.setObjectName("centralwidget")
            self.username_label = QtWidgets.QLabel(self.centralwidget)
            self.username_label.setGeometry(QtCore.QRect(50, 100, 111, 21))
            font = QtGui.QFont()
            font.setPointSize(14)
            self.username_label.setFont(font)
            self.username_label.setObjectName("username_label")
            self.pass_label = QtWidgets.QLabel(self.centralwidget)
            self.pass_label.setGeometry(QtCore.QRect(50, 150, 101, 21))
            font = QtGui.QFont()
            font.setPointSize(14)
            self.pass_label.setFont(font)
            self.pass_label.setObjectName("pass_enter_2")
            self.username_enter = QtWidgets.QLineEdit(self.centralwidget)
            self.username_enter.setGeometry(QtCore.QRect(172, 100, 181, 22))
            self.username_enter.setObjectName("username_enter")
            self.pass_enter = QtWidgets.QLineEdit(self.centralwidget)
            self.pass_enter.setGeometry(QtCore.QRect(170, 150, 181, 22))
            self.pass_enter.setEchoMode(QtWidgets.QLineEdit.Password)
            self.pass_enter.setClearButtonEnabled(True)
            self.pass_enter.setObjectName("pass_enter")
            self.login_button = QtWidgets.QPushButton(self.centralwidget)
            self.login_button.setGeometry(QtCore.QRect(250, 200, 93, 28))
            self.login_button.setObjectName("login_button")
            self.login_button.clicked.connect(self.LoginButtonClicked)
            self.reg_button = QtWidgets.QPushButton(self.centralwidget)
            self.reg_button.setGeometry(QtCore.QRect(70, 200, 93, 28))
            self.reg_button.setObjectName("reg_button")
            self.reg_button.clicked.connect(self.RegButtonClicked)
            main_window.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(main_window)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 409, 26))
            self.menubar.setObjectName("menubar")
            self.menuOptions = QtWidgets.QMenu(self.menubar)
            font = QtGui.QFont()
            font.setPointSize(4)
            self.menuOptions.setFont(font)
            self.menuOptions.setObjectName("menuOptions")
            main_window.setMenuBar(self.menubar)
            self.statusbar = QtWidgets.QStatusBar(main_window)
            self.statusbar.setObjectName("statusbar")
            main_window.setStatusBar(self.statusbar)
            self.kb_short_butt = QtWidgets.QAction(main_window)
            font = QtGui.QFont()
            font.setFamily("MS Sans Serif")
            font.setPointSize(8)
            font.setBold(True)
            font.setWeight(75)
            self.kb_short_butt.setFont(font)
            self.kb_short_butt.setObjectName("kb_short_butt")
            self.about_butt = QtWidgets.QAction(main_window)
            font = QtGui.QFont()
            font.setFamily("MS UI Gothic")
            font.setPointSize(9)
            font.setBold(True)
            font.setWeight(75)
            self.about_butt.setFont(font)
            self.about_butt.setObjectName("about_butt")
            self.menuOptions.addAction(self.kb_short_butt)
            self.menuOptions.addAction(self.about_butt)
            self.menubar.addAction(self.menuOptions.menuAction())

            self.retranslateUi(main_window)
            QtCore.QMetaObject.connectSlotsByName(main_window)

        def retranslateUi(self, main_window):
            _translate = QtCore.QCoreApplication.translate
            main_window.setWindowTitle(_translate("main_window", "Online Chat Application"))
            self.username_label.setText(_translate("main_window", "Username:"))
            self.pass_label.setText(_translate("main_window", "Password:"))
            self.username_enter.setStatusTip(_translate("main_window", "Enter your Username"))
            self.pass_enter.setStatusTip(_translate("main_window", "Enter your Password"))
            self.login_button.setStatusTip(_translate("main_window", "Click to Login after entering Credentials"))
            self.login_button.setText(_translate("main_window", "Login"))
            self.reg_button.setStatusTip(_translate("main_window", "Click to Register"))
            self.reg_button.setText(_translate("main_window", "Register"))
            self.menuOptions.setTitle(_translate("main_window", "Options"))
            self.kb_short_butt.setText(_translate("main_window", "Keyboard Shortcuts"))
            self.about_butt.setText(_translate("main_window", "About"))

        def LoginButtonClicked(self):
            username=self.username_enter.text()
            password=self.pass_enter.text()
            auth('l',username,password)
            self.win=QtWidgets.QMainWindow()
            self.ui=Ui_chat_un_enter()
            self.ui.setupUi(self.win)
            self.win.show()
            

        def RegButtonClicked(self):
            self.win=QtWidgets.QMainWindow()
            self.ui=Ui_RegWindow()
            self.ui.setupUi(self.win)
            self.win.show()
            


    if __name__ == "__main__":
        try:
            sio.connect('http://127.0.0.1:5001')
            app = QtWidgets.QApplication(sys.argv)
            main_window = QtWidgets.QMainWindow()
            ui = Ui_main_window()
            ui.setupUi(main_window)
            main_window.show()
            sys.exit(app.exec_())
        except Exception as e:
            print(e)
            # Exit with error

except ImportError as ie:
    print(ie)
    print("requiremnts.txt is not supported. Revert to manual installation")