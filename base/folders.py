import applib
import sys, os, locale
from dataclasses import dataclass

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

CONFIG_DEFAFULTS = {"craft-coef": 1, "campaign_step": 0, "time-speed": 360}

folder = applib.AppDir(path=path, config=True, tee=True, defaults=CONFIG_DEFAFULTS)

mainfolder = folder.mkdir("Assets")
textures = mainfolder.mkdir("Textures")
saves = mainfolder.mkdir("Saves")
music = mainfolder.mkdir("Music")
sounds = mainfolder.mkdir("Sounds")
fonts = mainfolder.mkdir("Fonts")
cursors = mainfolder.mkdir("Cursors")
localizations_folder = mainfolder.mkdir("Localizations")

@dataclass
class Devmode:
    value:bool

devmode = Devmode(False)

@dataclass
class OpenGL:
    value:bool

opengl = OpenGL(False)

class Dict(dict):
    def __getitem__(self, key:str) -> str:
        current: dict = self
        for t in key.split("-"):
            if not isinstance(current, dict) or t not in current:
                folder.log.write(f"There is no translation for <{key}>", type="LocalizationError")
                return f"<{key}>"
            a = current.get(t)
            if isinstance(a, str):
                return a
            current = a
        folder.log.write(f"There is no translation for <{key}>", type="LocalizationError")
        return f"<{key}>"

localizations:dict[str, Dict] = {}
for local in localizations_folder.list():
    if not local.endswith(".json"):
        continue
    localizations[local[:-5]] = Dict(applib.Config(localizations_folder.path(local)).data)

settings = applib.Config(mainfolder.path("settings.json"), {"volume": 100, "music_volume": 100, "music": True, "fullscreen": True, "shadows": True, "fps": 60})

localization = Dict()
if settings.get("localization") is not None:
    if settings.get("localization") in localizations:
        localization = localizations[settings.get("localization")]
    else:
        folder.log.write(f"Unknows localization as <{settings.get("localization")}>", type="LocalizationError")
        if "en-us" in localizations:
            localization = localizations["en-us"]
else:
    langf = locale.getdefaultlocale()[0] or "en-us"
    lang = langf.lower().replace("_", "-")
    if lang in localizations:
        settings.set("localization", lang)
        localization = localizations[lang]
        folder.log.write(f"Founded system localization as <{lang}>", type="LocalizationInfo")
    else:
        if "en-us" in localizations:
            settings.set("localization", "en-us")
            localization = localizations["en-us"]
        folder.log.write(f"Not Founded system localization as <{lang}>", type="LocalizationInfo")

block_config = applib.Config(mainfolder.path("block_config.json"))
unit_config = applib.Config(mainfolder.path("unit_config.json"))
