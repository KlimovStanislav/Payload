import applib
import sys, os

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

folder = applib.AppDir(path=path, config=True, tee=True, create_folders=False, defaults={"devmode": False, "craft_coef": 1, "campaign_step": 0})

mainfolder = folder.mkdir("Assets")
textures = mainfolder.mkdir("Textures")
saves = mainfolder.mkdir("Saves")
music = mainfolder.mkdir("Music")
sounds = mainfolder.mkdir("Sounds")
fonts = mainfolder.mkdir("Fonts")
cursors = mainfolder.mkdir("Cursors")

settings = applib.Config(mainfolder.path("settings.json"), {"volume": 100, "music_volume": 100, "music": True, "fps": 60})

block_config:dict = mainfolder.read("block_config.json", type="json")
unit_config:dict = mainfolder.read("unit_config.json", type="json")

