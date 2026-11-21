from __future__ import annotations
import time, threading, requests, re, webbrowser
from dataclasses import dataclass
from typing import NoReturn
from datetime import datetime
from base.folders import folder
from base.functions import safe_class

@dataclass
class Release:
    date:datetime
    text:str
    url:str

@safe_class
class OnlineGetter:
    url = r"https://api.github.com/repos/KlimovStanislav/Payload"
    releases:list[Release] = []
    __thread__:threading.Thread=None
    __every__=[]
    @staticmethod
    def open(release:Release=None) -> None:
        if release is None:
            webbrowser.open(r"https://github.com/KlimovStanislav/Payload")
        else:
            webbrowser.open(release.url)

    @staticmethod
    def connect(func):
        OnlineGetter.__every__.append(func)

    @staticmethod
    def start() -> threading.Thread:
        def main() -> NoReturn:
            def convert(text:str):
                text = re.sub(r"<img\b[^>]*>", "", text)
                text = text.replace("\r\n", "\n").strip("\n")
                return text
            while True:
                try:
                    answer = requests.get(f"{OnlineGetter.url}/releases", params={"per_page": 100})
                    answer.raise_for_status()
                    relf = answer.json()

                    releases = []

                    if relf: 
                        for r in relf:
                            date = datetime.strptime(r["tag_name"][6:], r"%d.%m.%Y")
                            releases.append(Release(date, convert(r["body"]), r["html_url"]))
                    releases.sort(key=lambda v: v.date, reverse=True)

                    for func in OnlineGetter.__every__:
                        func()
                except Exception as e:
                    folder.log.write(f"Error in retrieving releases from GitHub: <{e}>")
                    time.sleep(60)
                else:
                    folder.log.write("Successful retrieval releases from GitHub")
                    OnlineGetter.releases = releases
                    time.sleep(600)

        thread = threading.Thread(target=main, daemon=True)
        OnlineGetter.__thread__ = thread
        thread.start()
        return thread