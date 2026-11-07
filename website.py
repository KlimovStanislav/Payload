from flask import Flask, render_template

app = Flask(__name__)

GAME = {
    "name": "PAYLOAD",
    "version": "Alpha 0.2.22",
    "codename": "Game",
    "size": "85 MB",
    "description": "Factory",
    "long_description": (
        "Build, study, and, in short, play."
    ),
    "features": [
        "Head",
        "Tiles",
        "Drills, campaign, etc"
    ],
    "screenshots": ["1.png", "2.png", "3.png", "4.png"],
    "github": "https://github.com/KlimovStanislav/Payload",
    "download_win": "https://github.com/KlimovStanislav/Payload/releases/latest/download/installer-win64.exe",
}

@app.route("/")
def index():
    return render_template("index.html", game=GAME)

if __name__ == "__main__":
    app.run(debug=True)