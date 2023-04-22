#! /home/justnyan/jplay-gui/venv/bin/python3

from PyQt5 import QtWidgets, QtCore, QtGui

import sys

import audio

import time

class MyLoop(QtCore.QThread):
    def __init__(self, parent= ...) -> None:
        super().__init__(parent)
        self.app=None
    
    def run(self) -> None:
        while True:
            inf = self.app.player.get_info()
            ind = inf[1]
            lst = inf[3]
            dur = lst["metadata"][ind].length

            pos = self.app.player.mixer.get_pos()/1000
            # dur = lst.keys()
            l = [pos,dur]

            sec0_all = l[0]
            sec = l[0] % (24*3600)
            hour = round(sec // 3600)
            sec = sec % 3600
            min = round(sec // 60)
            sec = round(sec % 60)

            sec1_all = l[1]
            sec1 = l[1] % (24*3600)
            hour1 = round(sec1 // 3600)
            sec1 = sec1 % 3600
            min1 = round(sec1 // 60)
            sec1 = round(sec1 % 60)

            if (hour == 23) and (min == 59) and (sec == 60):
                self.app.next()
                continue
            elif (hour != 0 and min != 0):
                self.app.time.setText(f"{hour}:{min}:{sec} / {hour1}:{min1}:{sec1}")
                self.app.time_slider.setValue(int((100/sec1_all)*sec0_all))
            else:
                self.app.time.setText(f"{min}:{sec} / {min1}:{sec1}")
                self.app.time_slider.setValue(int((100/sec1_all)*sec0_all))

            
            time.sleep(0.3)

class App:
    def __init__(self) -> None:
        self.pc = 0

        self.player = audio.Player()

        self.app = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()

        self.window.setWindowTitle("JPlay")
        self.window.setFixedSize(int(210),int(290))
        # self.window.move(1020,5)

        self.vol_save = 100

        path = QtWidgets.QFileDialog(parent=self.window).getExistingDirectory(parent=self.window)
    
        self.player.playlist_gen(path=path,name="rnd")
        self.player.start_playing(playlist="rnd",start=True,shuffle=True)
        # except:
        #     sys.exit()

        self.window.setStyleSheet("background-color: #222222")
        self.window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.vol_slider = QtWidgets.QSlider(QtCore.Qt.Vertical, parent=self.window)
        self.vol_slider.setFixedSize(25,110)
        self.vol_slider.move(99+25+25+25,25)
        self.vol_slider.setValue(100)
        self.vol_slider.setMaximum(100)
        self.vol_slider.valueChanged.connect(self.set_vol)

        self.time = QtWidgets.QLabel(parent=self.window)
        self.time.setStyleSheet("color: #979797")
        self.time.setText("shadsa")
        self.time.setFixedSize(60,35)
        self.time.move(105-30,195)

        self.time_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, parent=self.window)
        self.time_slider.setFixedSize(135,15)
        self.time_slider.move(105-70,220)
        self.time_slider.setValue(0)
        self.time_slider.setMaximum(100)
        self.time_slider.setDisabled(True)
        # self.time_slider.setStyleSheet("")



        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Q"),self.window)
        self.qsh.activated.connect(sys.exit)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("M"),self.window)
        self.qsh.activated.connect(self.mute)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Right"),self.window)
        self.qsh.activated.connect(self.next)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Left"),self.window)
        self.qsh.activated.connect(self.pervious)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+P"),self.window)
        self.qsh.activated.connect(self.plpa)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"),self.window)
        self.qsh.activated.connect(self.shuffle)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Up"),self.window)
        self.qsh.activated.connect(self.up_vol)

        self.qsh = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Down"),self.window)
        self.qsh.activated.connect(self.down_vol)

        self.title = QtWidgets.QLabel("Just Player GUI",parent=self.window)
        self.title.setStyleSheet("color: #979797")
        self.title.setFixedSize(210,30)
        self.title.move(0,-5)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.pic = QtWidgets.QLabel(parent=self.window)
        # self.picture = QtGui.QImage("default.png")
        pm = QtGui.QPixmap("resources/default.png")
        pm = pm.scaled(QtCore.QSize(100,100))
        self.pic.setPixmap(pm)
        self.pic.setFixedSize(100,100)
        self.pic.move(int((210-100)/2),40)

        self.song_name = QtWidgets.QLabel(parent=self.window)
        self.song_name.setAlignment(QtCore.Qt.AlignCenter)
        self.song_name.setFixedSize(210,40)
        self.song_name.move(0,160)
        self.song_name.setWordWrap(True)
        self.song_name.setStyleSheet("color: #979797;")

        pl = self.player.now["playlist"]
        idx = self.player.now["index"]
        sng = self.player.playlists[pl]["list"][idx]
        self.song_name.setText(sng)


        self.btnpre = self.btn(clicked=self.pervious, icon="resources/p.png",pos=(33,240))
        self.btnpp = self.btn(clicked=self.plpa, icon="resources/pause.png",pos=(66+25,240))
        self.btnn = self.btn(clicked=self.next, icon="resources/n.png",pos=(99+25+25,240))

        self.btn_sound = self.btn(clicked=self.mute,icon="resources/sound.png",pos=(99+25+25+25,135))

        self.loop = MyLoop(parent=self.window)
        self.loop.app = self
        self.loop.start()

        self.window.show()
        sys.exit(self.app.exec_())



    def btn(self, clicked=None, text=None, icon=None, fsize=(25,25), pos=(0,0)):
        button = QtWidgets.QPushButton(parent=self.window,text=text)
        button.setIcon(QtGui.QIcon(icon))
        button.setFixedSize(fsize[0],fsize[1])
        button.move(pos[0],pos[1])
        button.clicked.connect(clicked)
        button.setStyleSheet("border: false")
        return button
    

    def pervious(self,arg=None):
        if not self.player.now["playing"]:
            self.btnpp.setIcon(QtGui.QIcon("resources/pause.png"))
            self.pc += 1
        self.player.pervious()
        pl = self.player.now["playlist"]
        idx = self.player.now["index"]
        sng = self.player.playlists[pl]["list"][idx]

        
        self.song_name.setText(sng)

    def plpa(self, arg=None):
        self.player.play_pause()
        if self.pc % 2 == 0:
            self.btnpp.setIcon(QtGui.QIcon("resources/play.png"))
        else:
            self.btnpp.setIcon(QtGui.QIcon("resources/pause.png"))
        self.pc += 1

    def next(self, arg=None):
        if not self.player.now["playing"]:
            self.btnpp.setIcon(QtGui.QIcon("resources/pause.png"))
            self.pc += 1
        self.player.next()
        pl = self.player.now["playlist"]
        idx = self.player.now["index"]
        sng = self.player.playlists[pl]["list"][idx]
        # mll.set_title("0:0 / 0:0")

        self.song_name.setText(sng)
        # args1[1].set_text(str(idx+1))

    def shuffle(self, arg=None):
        if not self.player.now["playing"]:
            self.btnpp.setIcon(QtGui.QIcon("resources/pause.png"))
            self.pc += 1
        self.player.shuffle()
        pl = self.player.now["playlist"]
        idx = self.player.now["index"]
        sng = self.player.playlists[pl]["list"][idx]

        
        self.song_name.setText(sng)
        # args1[1].set_text(str(idx+1))
        # mll.set_title("0:0 / 0:0")

    def up_vol(self):
        vol = self.player.up_vol(0.04)
        # print(vol)
        self.vol_slider.setValue(int(vol*100))
        if vol > 0:
            self.btn_sound.setIcon(QtGui.QIcon("resources/sound.png"))
    
    def down_vol(self):
        vol = self.player.down_vol(0.01)
        # print(vol)
        self.vol_slider.setValue(int(vol*100))
        if vol == 0:
            self.btn_sound.setIcon(QtGui.QIcon("resources/mute.png"))
    def set_vol(self):
        self.player.mixer.set_volume(self.vol_slider.value()/100)
    
    def mute(self):
        if self.vol_slider.value() != 0:
            self.vol_save = self.vol_slider.value()
            self.vol_slider.setValue(0)
            self.player.mixer.set_volume(0)
            self.btn_sound.setIcon(QtGui.QIcon("resources/mute.png"))
        else:
            self.vol_slider.setValue(self.vol_save)
            self.player.mixer.set_volume(self.vol_save/100)
            self.btn_sound.setIcon(QtGui.QIcon("resources/sound.png"))
if __name__ == "__main__":
    jplay = App()
