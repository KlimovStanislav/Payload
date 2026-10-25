from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import time, random, threading, pygame
from base.folders import settings, sounds, music
from pygame.mixer import Sound
from typing import NoReturn

pygame.mixer.init()

class MusicPlayer():
    __cache__:dict[str, Sound] = {}
    playing = False
    
    @staticmethod
    def start() -> threading.Thread:
        MusicPlayer.playing = True
        def play() -> NoReturn:
            time.sleep(random.randint(30, 40))
            while MusicPlayer.playing == True:
                music_name = random.choice(music.list())
                print(f"Playing: <{music.path(music_name)}>")
                pygame.mixer.music.load(music.path(music_name))
                pygame.mixer.music.set_volume(settings.get("music_volume"))
                pygame.mixer.music.play(0)
                while pygame.mixer.music.get_busy():
                    if MusicPlayer.playing == False:
                        break
                    pygame.mixer.music.set_volume(settings.get("music_volume") if settings.get("music") is not False else 0)
                    time.sleep(0.1)
                time.sleep(random.randint(40, 60))

        thread = threading.Thread(target=play, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def stop():
        MusicPlayer.playing = False

    @staticmethod
    def play(path, volume=0.7) -> Sound:
        if path in MusicPlayer.__cache__:
            sound = MusicPlayer.__cache__[path]
            sound.set_volume(volume*settings.get("volume"))
            sound.play()
        else:
            sound = pygame.mixer.Sound(sounds.path(f"{path}.ogg"))
            sound.set_volume(volume*settings.get("volume"))
            sound.play()
            MusicPlayer.__cache__[path] = sound
        return sound