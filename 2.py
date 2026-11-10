import applib, json
dct:dict[str: dict] = {}
for i in applib.Storage("tc").list():
    dct[i[:-4]] = {"type": "UseBlock", "z": 11, "relief": True, "texture": i[:-4]}
with open("b.json", "w", encoding="UTF-8") as f:
    json.dump(dct, f, indent=4)