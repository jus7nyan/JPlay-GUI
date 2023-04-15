#import mutagen
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from random import *

import lyricsgenius

pygame.init()

class Player:
    def __init__(self) -> None:
        self.token = "XHUCKXOEPYzU8jy0kopz6e5NdhNNnpoTxgOzlq5vSMhvIFjXB72W-Kc_JnKzJmZF"
        self.genius = lyricsgenius.Genius(self.token,verbose=False)
        

        self.mixer = pygame.mixer.music
        self.playlists= {}
        self.now = {"playing": False, "playlist": None, "index": 0}
        
    
    def get_info(self):
        playing = self.mixer.get_busy
        playlist = self.now["playlist"]
        index = self.now["index"]
        lst = self.playlists[playlist]
        volume = self.mixer.get_volume

        return (playing, index, playlist, lst, volume)

    def up_vol(self, u):
        self.mixer.set_volume(self.mixer.get_volume()+u)
        return self.mixer.get_volume()
    def down_vol(self, u):
        self.mixer.set_volume(self.mixer.get_volume()-u)
        return self.mixer.get_volume()
    def get_vol(self):
        return int(self.mixer.get_volume())

    def playlist_gen(self, path, name=None):
        if path[-1] != "/":
            path += '/'
        lst = os.listdir(os.path.abspath(path))
        lst_t = []
        lst_m = []
        lst_p = []
        for i in range(len(lst)):
            if os.path.splitext(lst[i])[1] in (".mp3"):
                lst_t.append(lst[i])
                # print(MP3(path+lst[i]).info)
                lst_m.append(MP3(path+lst[i]).info)
                lst_p.append(path+lst[i])
            
            elif os.path.splitext(lst[i])[1] in (".wav"):
                lst_t.append(lst[i])
                # print(WAVE(path+lst[i]).info)
                lst_m.append(WAVE(path+lst[i]).info)
                lst_p.append(path+lst[i])
        
        if not name:
            name = str(int(list(self.playlists.keys())[-1])+1)

        self.playlists.update({f"{name}":{"list":lst_t, "metadata":lst_m, "path":lst_p}})
    
    def play_pause(self):
        if self.now["playing"]:
            self.mixer.pause()
            self.now["playing"] = False

        elif not self.now["playing"]:
            self.mixer.unpause()
            self.now["playing"] = True
            if not self.mixer.get_busy():
                self.mixer.play()
    
    def start_playing(self, playlist, idx = 0, start=False, shuffle=False):
        try:
            lst = self.playlists[playlist]
        except:
            lst = self.playlists[list(self.playlists.keys())[0]]
        
        name = lst["list"][idx]
        path = lst["path"][idx]
        # dur = lst["metadata"][idx].streaminfo.duration
        self.mixer.load(path)
        if start:
            self.mixer.play()
            self.now["playing"] = True
            self.mixer.pause()
            self.mixer.unpause()
        else:
            self.now["playing"] = False
        self.now["playlist"] = playlist
        self.now["index"] = idx


        if shuffle:
            self.shuffle()
            #self.mixer.play()

        return (name)
    
    def get_playlist(self, playlist):
        return self.playlists[playlist]
    
    def shuffle(self):
        p_name = self.now["playlist"]
        lst = self.playlists[p_name]["list"]
        mdata = self.playlists[p_name]["metadata"]
        pathl = self.playlists[p_name]["path"]

        for i in range(len(lst)):
            rn = randint(0,len(lst)-1)
            l1,m1,p1 = lst[i], mdata[i], pathl[i]
            l2,m2,p2 = lst[rn], mdata[rn], pathl[rn]
            lst[rn],mdata[rn],pathl[rn] = l1,m1,p1
            lst[i],mdata[i],pathl[i] = l2,m2,p2

        self.playlists[p_name]["list"] = lst
        self.playlists[p_name]["metadata"] = mdata
        self.playlists[p_name]["path"] = pathl
        self.now["playing"] = True
        self.now["index"] = 0
        self.mixer.load(pathl[0])
        self.mixer.play()
    
    def next(self):
        idx = self.now["index"]
        pl = self.now["playlist"]
        try:
            pathn = self.playlists[pl]["path"][idx+1]
            idx += 1
        except:
            pathn = self.playlists[pl]["path"][0]
            idx = 0
        self.mixer.pause()
        self.mixer.load(pathn)
        self.now["playing"] = True
        self.mixer.play()
        self.mixer.pause()
        self.mixer.unpause()
        self.now["index"] = idx


    def pervious(self):
        idx = self.now["index"]
        pl = self.now["playlist"]
        lst = self.playlists[pl]["path"]
        if idx == 0:
            idx = len(lst)-1
        else:
            idx -= 1
        pathn = lst[idx]
        self.mixer.pause()
        self.mixer.load(pathn)
        self.now["playing"] = True
        self.mixer.play()
        self.mixer.pause()
        self.mixer.unpause()
        self.now["index"] = idx
    

    def get_lyr(self):
        ind,ln = self.now["index"], self.now["playlist"]
        sng = self.playlists[ln]["list"][ind].replace("(1)","").replace("(2)","")
        songs = self.genius.search(sng[:-3])["hits"]
        res = []
        for i in songs:
            artist = i["result"]["artist_names"]
            title = i["result"]["title"]
            res.append(f"{artist} -- {title}")
        
        return res
    
    def get_text(self, song):
        artist, title = song.split(" -- ")

        song = self.genius.search_song(title,artist)

        lyrics = song.lyrics

        return [lyrics, artist, title]

        

if __name__ == "__main__":
    from sys import argv
    p = Player()
    p.playlist_gen(argv[1:][0], "pl1")
    song = p.start_playing("pl1",13,True)


    # while True:
    #     a = input()
    #     if ("nex") in a:
    #         p.next()
    #     elif ("pre") in a:
    #         p.pervious()
    #     elif ("sh") in a:
    #         p.shuffle()
    #     elif ("p") in a:
    #         p.play_pause()
    #     print(p.mixer.get_pos()/1000)
    #     print(p.playlists["pl1"]["metadata"][0].streaminfo.duration)
