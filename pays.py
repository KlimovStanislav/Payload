try:
    import pymsgbox
except Exception:
    raise Exception("Install pymsgbox")

from time import perf_counter
start = perf_counter()

import sys
import faulthandler

try:
    import traceback
    import os, applib, faulthandler
    import testing

    from base.folders import folder, mainfolder, settings, devmode, opengl
    
    if "--devmode" in sys.argv: devmode.value = True
    if "--opengl" in sys.argv: opengl.value = True

    from PyQt6.QtWidgets import QApplication
    import base.font
    import base.cursors

    from base.OnlineGetter import OnlineGetter
    
    application = QApplication(sys.argv)
    base.font.__dict__[...] = application
    base.cursors.__dict__[...] = application
    testing.__dict__[...] = application
    
    if os.path.exists(os.path.abspath(mainfolder.path("style.qss"))):
        with open(mainfolder.path("style.qss"), "r", encoding="utf-8") as f:
            application.setStyleSheet(f.read())
    else:
        folder.log.write(f"style.qss not found at <{mainfolder.path('style.qss')}>")

    from ui.MainWindow import MainWindow
    faulthandler.enable(open("crash.log", "w"))

except Exception:
    pymsgbox.alert(f"Critical StartError:\n{traceback.format_exc()}", "C1", icon=pymsgbox.STOP)
    traceback.print_exc()
    os.abort()

def main()->int:
    try:
        failed, critical, time = testing.start(testing.Mode.SMOKE)

        if critical:
            folder.log.write("\n".join(critical), type="StartError", set_error=True)
            pymsgbox.alert(f'Critical StartError:\n{"\n".join(critical)}', "C2", icon=pymsgbox.STOP)
            return 2

        if failed:
            folder.log.write("\n".join(failed), type="StartError", set_error=True)
            if pymsgbox.confirm(f"Failed {len(failed)} tests:\n{"\n".join(failed)}\nLaunch the game?", "StartError", icon=pymsgbox.WARNING) != pymsgbox.OK_TEXT:
                print(failed)
                return 2
            
        OnlineGetter.start()

        folder.plugins.init()
        folder.plugins.call("pre_start", application)

        if not failed and not critical:
            folder.log.write(f"All systems online. Start lasted {(perf_counter()-start)*1000:.0f} milliseconds. Smoke tests completed in {time:.0f} milliseconds.\nOpenGL-{opengl.value}\nDevMode-{devmode.value}", type="StartInfo")

        window = MainWindow()
        if not "--nowindow" in sys.argv:
            window.showMaximized() if settings.get("fullscreen") is False else window.showFullScreen()

        folder.plugins.call("start", window)
    except Exception as e:
        folder.log.write(traceback.format_exc(), type="StartError", set_error=True)
        if "window" in locals():
            if window is not None:
                window.close()

        pymsgbox.alert(f"Critical StartError: {e}", "C(main)", icon=pymsgbox.STOP)
        return 2
    
    return application.exec()

if __name__ == "__main__":
    code = max(main(), applib._exit_code)
    faulthandler.disable()
    folder.config.save()
    settings.save()
    application.exit(code)
    os._exit(code)