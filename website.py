from flask import Flask, render_template

app = Flask(__name__)

GAME = {
    "name": "LOW-LEVEL",
    "version": "Alpha 0.2.21",
    "codename": "Game",
    "size": "85 MB",
    "description": "Фабрико-Строй",
    "long_description": (
        "Стройте, изучайте, короче играйте"
    ),
    "features": [
        "Тепло",
        "Блоки",
        "Буры, конвейера и т.д."
    ],
    "screenshots": ["1.png", "2.png", "3.png", "4.png"],
    "github": "https://github.com/Stanislafv/Low-Level",
    "download_win": "https://github.com/Stanislafv/Low-Level/releases/latest/download/launcher-win64.exe",
}

CHANGELOG = [
    {
        "version": "Alpha 0.2.21",
        "date": "2026г",
        "changes": [
            "Много чего",
        ],
    },
    {
        "version": "Alpha 0.2.1",
        "date": "2026г",
        "changes": [
            "релиз",
        ],
    },
]

@app.route("/")
def index():
    return render_template("index.html", game=GAME)

@app.route("/changelog")
def changelog():
    return render_template("changelog.html", game=GAME, changelog=CHANGELOG)

if __name__ == "__main__":
    app.run(debug=True)