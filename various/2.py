from PyQt6 import QtWidgets, QtCore, QtGui
import applib

a = QtWidgets.QApplication([])
for i in applib.Storage("various/tc").list():
    pixmapf = QtGui.QPixmap(f"various/tc/{i}")
    print(i, f"various/tc/{i}")
    pixmap = QtGui.QPixmap(pixmapf.size())
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)

    with QtGui.QPainter(pixmap) as painter:
        painter.setOpacity(0.5)
        painter.drawPixmap(0, 0, pixmapf)

    pixmap.save(f"various/tc/{i[:-4]}-alpha2.png", "png")

exit()
import applib, json
dct:dict[str: dict] = {}
for i in applib.Storage("various/tc").list():
    dct[i[:-4]] = {"type": "UseBlock", "z": 11, "relief": True, "texture": i[:-4]}
with open("b.json", "w", encoding="UTF-8") as f:
    json.dump(dct, f, indent=4)