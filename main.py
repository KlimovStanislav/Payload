try:
    import pymsgbox
except Exception:
    raise Exception("Install pymsgbox")

from time import perf_counter
start = perf_counter()

try:
    import traceback
    import os, applib, sys
    import testing

    from PyQt6.QtWidgets import QApplication
    import base.font
    import base.cursors

    from base.folders import folder, mainfolder, settings
    
    application = QApplication(sys.argv)
    base.font.__dict__[...] = application
    base.cursors.__dict__[...] = application
    
    if os.path.exists(os.path.abspath(mainfolder.path("style.qss"))):
        with open(mainfolder.path("style.qss"), encoding="utf-8") as f:
            application.setStyleSheet(f.read())
    else:
        folder.log.write(f"style.qss not found at <{mainfolder.path("style.qss")}>")

    from ui.MainWindow import MainWindow

except Exception:
    pymsgbox.alert(f"Critical StartError:\n{traceback.format_exc()}", "C1", icon=pymsgbox.STOP)
    print(traceback.format_exc())
    __import__("os").abort()

def main()->int:
    try:
        failed, critical, time = testing.start(testing.Mode.SMOKE)

        if critical:
            folder.log.write("\n".join(critical), type="StartError", set_error=True)
            pymsgbox.alert(f"Critical StartError:\n{"\n".join(critical)}", "C2", icon=pymsgbox.STOP)
            return 1

        if failed:
            folder.log.write("\n".join(failed), type="StartError", set_error=True)
            if pymsgbox.confirm(f"Failed {len(failed)} tests:\n{"\n".join(failed)}\nLaunch the game?", "StartError", icon=pymsgbox.WARNING) != pymsgbox.OK_TEXT:
                return 1

        folder.plugins.init()
        folder.plugins.call("pre_start", application)

        if not failed and not critical:
            folder.log.write(f"All systems online. Start lasted {(perf_counter()-start)*1000:.0f} milliseconds. Smoke tests completed in {time:.0f} milliseconds.", type="StartInfo")

        window = MainWindow()
        window.showMaximized() if settings.get("fullscreen") is False else window.showFullScreen()

        folder.plugins.call("start", window)
    except Exception as e:
        folder.log.write(traceback.format_exc(), type="StartError", set_error=True)
        if "window" in locals():
            if window is not None:
                window.close()

        pymsgbox.alert(f"Critical StartError: {e}", "C(main)", icon=pymsgbox.STOP)
        return 1
    
    return application.exec()

if __name__ == "__main__":
    code = max(main(), applib._exit_code)
    folder.config.save()
    settings.save()
    application.exit(code)
    sys.exit(code)