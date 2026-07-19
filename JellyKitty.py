import os
import subprocess
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

# current folder
VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
THUMB_DIR = os.path.join(VIDEO_DIR, ".thumbnails")

# folder for thumbnails
os.makedirs(THUMB_DIR, exist_ok=True)

def generate_thumbnail(video_name):
    video_path = os.path.join(VIDEO_DIR, video_name)
    thumb_name = f"{video_name}.jpg"
    thumb_path = os.path.join(THUMB_DIR, thumb_name)
    
    if os.path.exists(thumb_path):
        return thumb_name
        
    try:
        cmd = [
            'ffmpeg', '-ss', '00:00:05', '-i', video_path, 
            '-vframes', '1', '-vf', 'scale=320:-1', '-y', thumb_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return thumb_name
    except Exception:
        return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>JellyKitty</title>
    <style>
        body { font-family: sans-serif; background: #141414; color: white; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
        .card { background: #222; border-radius: 8px; overflow: hidden; text-align: center; padding-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .thumbnail-box { width: 100%; height: 140px; background: #333; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .thumbnail { width: 100%; height: 100%; object-fit: cover; }
        .card h3 { font-size: 14px; margin: 10px; padding: 0 5px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; }
        a { color: #00bcd4; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Kittythek</h1>
    <div class="grid">
        {% for video in videos %}
            <div class="card">
                <div class="thumbnail-box">
                    {% if video.thumb %}
                        <img class="thumbnail" src="/thumb/{{ video.thumb }}" alt="Thumbnail">
                    {% else %}
                        <span>Kein Bild</span>
                    {% endif %}
                </div>
                <h3>{{ video.name }}</h3>
                <a href="/watch/{{ video.name }}">Abspielen</a>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

PLAYER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spiele ab: {{ video }}</title>
    <style>
        body { background: black; color: white; text-align: center; font-family: sans-serif; }
        video { width: 80%; max-width: 1000px; margin-top: 50px; box-shadow: 0 0 20px rgba(255,255,255,0.1); }
        a { color: #00bcd4; text-decoration: none; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Spiele ab: {{ video }}</h2>
    <video controls autoplay>
        <source src="/stream/{{ video }}" type="video/mp4">
        Dein Browser unterstützt dieses Videoformat nicht.
    </video>
    <br>
    <a href="/">← Zurück zur Übersicht</a>
</body>
</html>
"""

@app.route('/')
def index():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
    
    videos_with_thumbs = []
    for video in video_files:
        thumb = generate_thumbnail(video)
        videos_with_thumbs.append({
            'name': video,
            'thumb': thumb
        })
        
    return render_template_string(HTML_TEMPLATE, videos=videos_with_thumbs)

@app.route('/watch/<path:filename>')
def watch(filename):
    return render_template_string(PLAYER_TEMPLATE, video=filename)

@app.route('/stream/<path:filename>')
def stream(filename):
    return send_from_directory(VIDEO_DIR, filename)

@app.route('/thumb/<path:filename>')
def get_thumb(filename):
    return send_from_directory(THUMB_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)