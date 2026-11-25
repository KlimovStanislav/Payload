import tkinter as tk, subprocess, sys, pymsgbox, os
from dataclasses import dataclass

CONFIGS_DEFAFULTS = {"config": {"craft_coef": 1, "campaign_step": 0}, "settings": {"volume": 100, "music_volume": 100, "music": True, "fps": 60}}

@dataclass
class Mode:
    path:str
    fileexecname:str
    cmd_args:bool

if getattr(sys, 'frozen', False):
    mode = Mode(os.path.dirname(sys.executable), "Pays.exe", False)
else:
    mode = Mode(os.path.dirname(os.path.abspath(sys.argv[0])), "pays.py", True)

def view(path):
    if sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path])

ERRORS = {3221225477: "Critical Qt failure", 3221225725: "Stack overflow", 3221226505: "Stack overflow"}

class CsBtn:
    def __init__(self, menu, title, subtitle, cmd):
        item = tk.Frame(menu, bg="#ffffff", cursor="hand2")
        item.pack(fill="x")
        
        arrow = tk.Label(item, text="→", font=("Consolas", 22), bg="#ffffff", fg="#2980b9")
        arrow.pack(side="left", padx=(10, 15), pady=8)
        
        text_frame = tk.Frame(item, bg="#ffffff")
        text_frame.pack(side="left", fill="x", expand=True)
        
        lbl_title = tk.Label(text_frame, text=title, font=("Consolas", 12), bg="#ffffff", fg="#2980b9", anchor="w")
        lbl_title.pack(fill="x")
        
        lbl_sub = None
        if subtitle:
            lbl_sub = tk.Label(text_frame, text=subtitle, font=("Consolas", 9), bg="#ffffff", fg="#7f8c8d", anchor="w")
            lbl_sub.pack(fill="x")
        
        tk.Frame(menu, height=1, bg="#e0e0e0").pack(fill="x")
        widgets:list[tk.Label] = [item, text_frame, lbl_title, arrow, lbl_sub] if lbl_sub else [item, text_frame, lbl_title, arrow]
        def on_enter(*ф):
            for w in widgets:
                w.config(bg="#f0f0f0")
        
        def on_leave(*фкпы):
            for w in widgets:
                w.config(bg="#ffffff")
        
        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda *args, e=cmd: e())

def reset_config(root):
    try:
        import json
        cpath = os.path.join(mode.path, "config.json")
        if not os.path.exists(cpath):
            open(cpath, "x").close()
        with open(cpath, "w", encoding="UTF-8") as f:
            json.dump(CONFIGS_DEFAFULTS["config"], f)

        spath = os.path.join(mode.path, "Assets", "settings.json")
        if not os.path.exists(spath):
            open(spath, "x").close()
        with open(spath, "w", encoding="UTF-8") as f:
            json.dump(CONFIGS_DEFAFULTS["settings"], f)

    except Exception:
        pymsgbox.alert(f"Unable to restore config", "Failure", root=root, icon=pymsgbox.STOP)
    else:
        pymsgbox.alert(f"Config restored successfully", "Successfull", root=root, icon=pymsgbox.INFO)

class SupportToolsWindow(tk.Toplevel):
    def __init__(self, w):
        super().__init__(w)
        self.title("Payload Launcher")
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        
        self.geometry(f"500x380+{w//2+200}+{h//2-190}")
        self.resizable(False, False)

        self.configure(bg="#ffffff")
        
        header = tk.Frame(self, bg="#ffffff")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        tk.Label(header, text="Support Tools", font=("Segoe UI", 16), bg="#ffffff", fg="#2980b9").pack(side="left")
        
        menu = tk.Frame(self, bg="#ffffff")
        menu.pack(fill="x", padx=20, pady=10)
        
        CsBtn(menu, "Reset Config", "Reset a application config", cmd=lambda: reset_config(self))

class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.process:subprocess.Popen = None
        self.after(16, self.refresh)
        self.title("Payload Launcher")
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()

        self.geometry(f"500x380+{w//2-250}+{h//2-190}")
        self.resizable(False, False)
        
        self.configure(bg="#ffffff")

        header = tk.Frame(self, bg="#ffffff")
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(header, text="Welcome", font=("Segoe UI", 16), bg="#ffffff", fg="#2980b9").pack(side="left")

        self.tools = SupportToolsWindow(self)
        self.tools.withdraw()

        menu = tk.Frame(self, bg="#ffffff")
        menu.pack(fill="x", padx=20, pady=10)

        CsBtn(menu, "Launch", "Simply enjoy Payload", cmd=lambda: self.start())
        CsBtn(menu, "Launch(OpenGL)", "Test the OpenGL render", cmd=lambda: self.start("--opengl"))
        CsBtn(menu, "Launch(Debug mode)", "Devmode for Payload", cmd=lambda: self.start("--devmode"))
        CsBtn(menu, "User Folder", "Open user data", cmd=lambda: view(mode.path))
        CsBtn(menu, "Support tools", "Tools for troubleshooting problems with the application", cmd=lambda: self.tools.deiconify())

    def refresh(self):
        if self.process is not None:
            ret = self.process.poll()
            if ret is not None:
                if ret == 0:
                    self.destroy()
                    return

                if ret == 2:
                    self.process.kill()
                    self.process=None
                    self.deiconify()
                
                if ret not in [1, 2]:
                    pymsgbox.alert(f"Emergency shutdown due to reason: <{ERRORS.get(ret, ret)}>", f"<{ERRORS.get(ret, ret)}>", root=self, icon=pymsgbox.STOP)
                    self.process.kill()
                    self.process=None
                    self.deiconify()
        
        self.after(16, self.refresh)

    def start(self, *args):
        self.process = subprocess.Popen([sys.executable, mode.fileexecname, *args] if mode.cmd_args else [mode.fileexecname, *args])
        self.withdraw()
        if self.tools.winfo_viewable():
            self.tools.withdraw()

window = Window()
window.mainloop()