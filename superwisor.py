import tkinter as tk, subprocess, sys, pymsgbox, os

if getattr(sys, 'frozen', False):
    path = os.path.dirname(sys.executable)
else:
    path = os.path.dirname(os.path.abspath(sys.argv[0]))

ERRORS = {3221225477: "Critical Qt failure", 3221225725: "Stack overflow"}

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
        
        tk.Label(header, text="⬡", font=("Consolas", 24, "bold"), bg="#ffffff", fg="#e67e22").pack(side="left", padx=(0, 10))
        tk.Label(header, text="Welcome", font=("Segoe UI", 16), bg="#ffffff", fg="#2980b9").pack(side="left")

        menu = tk.Frame(self, bg="#ffffff")
        menu.pack(fill="x", padx=20, pady=10)

        CsBtn(menu, "Launch", "Simply enjoy Payload", cmd=lambda: self.start())
        CsBtn(menu, "Launch(OpenGL)", "Test the OpenGL render", cmd=lambda: self.start("--opengl"))
        CsBtn(menu, "Launch(Debug mode)", "Devmode for Payload", cmd=lambda: self.start("--devmode"))
        CsBtn(menu, "User Folder", "Open user data", cmd=lambda: print("Папка..."))
        CsBtn(menu, "Support tools", "Tools for troubleshooting problems with the application", cmd=lambda: print("Инструменты..."))

    def refresh(self):
        if self.process is not None:
            ret = self.process.poll()
            if ret is not None:
                if ret == 0:
                    self.destroy()
                    return
                
                if ret != 1:
                    pymsgbox.alert(f"Emergency shutdown due to reason: <{ERRORS.get(ret, ret)}>", f"<{ERRORS.get(ret, ret)}>", root=self, icon=pymsgbox.STOP)
                    self.process.kill()
                    self.process=None
                    self.deiconify()
        
        self.after(16, self.refresh)

    def start(self, *args):
        self.process = subprocess.Popen([sys.executable, "main.py", *args])
        self.withdraw()

window = Window()
window.mainloop()