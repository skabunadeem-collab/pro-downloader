import os, uuid
from flask import Flask, render_template_string, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ---------------- LANDING PAGE ----------------
LANDING_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Universal Pro Downloader</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:#0a0a12;color:white;font-family:Poppins;}
.hero{text-align:center;padding:80px 20px;}
.btn-main{padding:14px 35px;border-radius:40px;background:linear-gradient(45deg,#764ba2,#667eea);border:none;color:white;}
.card-box{background:#161625;padding:30px;border-radius:20px;margin-top:40px;}
.ad-box{background:#1a1a2e;border:2px dashed #444;padding:25px;text-align:center;color:#888;border-radius:15px;margin:25px 0;}
</style>
</head>
<body>
<div class="container">
<div class="hero">
<h1 class="fw-bold">Universal Pro Downloader</h1>
<p class="mt-3">Download YouTube Videos, Shorts, Instagram Reels & Stories in High Quality.</p>
<a href="/tool" class="btn btn-main mt-3">Start Now</a>
</div>

<div class="card-box">
<h4>Why Use Our Tool?</h4>
<ul>
<li>HD Video Download (360p / 720p / 1080p)</li>
<li>MP3 Audio Download</li>
<li>Fast & Secure</li>
<li>Mobile Friendly</li>
</ul>
</div>

<div class="ad-box">Google AdSense Header Ad</div>
<div class="ad-box">Google AdSense In-Content Ad</div>
<div class="ad-box">Google AdSense Footer Ad</div>

<div class="text-center mt-5">
<a href="/blog" class="text-info">Read Our Blog</a>
</div>

</div>
</body>
</html>
"""

# ---------------- BLOG PAGE (SEO READY) ----------------
BLOG_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>How to Download YouTube & Instagram Videos</title>
<meta name="description" content="Learn how to download YouTube videos and Instagram reels easily using Universal Pro Downloader.">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:#0a0a12;color:white;font-family:Poppins;}
.container{padding:40px 20px;}
.ad-box{background:#1a1a2e;border:2px dashed #444;padding:25px;text-align:center;color:#888;border-radius:15px;margin:25px 0;}
</style>
</head>
<body>
<div class="container">
<h1>How to Download YouTube & Instagram Videos</h1>
<p class="mt-3">
Universal Pro Downloader ek simple aur powerful tool hai jo aapko YouTube videos,
Shorts, Instagram reels aur stories download karne deta hai.
</p>

<div class="ad-box">Google AdSense Blog Ad</div>

<h3>Steps to Download:</h3>
<ol>
<li>Video link copy kare</li>
<li>Tool page par paste kare</li>
<li>Quality select kare</li>
<li>Download button dabaye</li>
</ol>

<p class="mt-4">
Yeh tool fast, secure aur mobile friendly hai.
</p>

<a href="/tool" class="btn btn-success mt-3">Go to Downloader</a>
</div>
</body>
</html>
"""

# ---------------- TOOL PAGE ----------------
TOOL_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pro Downloader Tool</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{background:#0a0a12;color:white;font-family:Poppins;}
.card-box{background:#161625;padding:25px;border-radius:20px;margin-top:40px;}
.ad-box{background:#1a1a2e;border:2px dashed #444;padding:20px;text-align:center;color:#888;border-radius:15px;margin:20px 0;}
video{width:100%;border-radius:15px;margin-top:15px;}
</style>
</head>
<body>
<div class="container">
<h2 class="text-center mt-4">All-in-One Downloader</h2>

<div class="card-box">
<form method="POST" action="/analyze">
<input type="text" name="url" class="form-control mb-3" placeholder="Paste Link Here..." required>

<select name="quality" class="form-control mb-3">
<option value="best">Best Quality</option>
<option value="360">360p</option>
<option value="720">720p</option>
<option value="1080">1080p</option>
<option value="audio">Audio Only (MP3)</option>
</select>

<button class="btn btn-primary w-100">Fetch Video</button>
</form>

<div class="ad-box">Google AdSense Tool Ad</div>

{% if result %}
<h5 class="mt-4">{{ result.title }}</h5>

{% if result.preview %}
<video controls>
<source src="{{ result.preview }}" type="video/mp4">
</video>
{% endif %}

<form method="POST" action="/download">
<input type="hidden" name="video_url" value="{{ result.original_url }}">
<input type="hidden" name="quality" value="{{ result.quality }}">
<button class="btn btn-success w-100 mt-3">Download</button>
</form>
{% endif %}

{% if error %}
<div class="alert alert-danger mt-3">{{ error }}</div>
{% endif %}

</div>
</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(LANDING_PAGE)

@app.route("/blog")
def blog():
    return render_template_string(BLOG_PAGE)

@app.route("/tool")
def tool():
    return render_template_string(TOOL_PAGE)

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.form.get("url")
    quality = request.form.get("quality")

    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

            preview_url = None

            # Find progressive mp4 format (video + audio together)
            for f in info.get("formats", []):
                if f.get("ext") == "mp4" and f.get("acodec") != "none" and f.get("vcodec") != "none":
                    preview_url = f.get("url")
                    break

            result = {
                "title": info.get("title", "Video"),
                "preview": preview_url,
                "original_url": url,
                "quality": quality
            }

            return render_template_string(TOOL_PAGE, result=result)

    except Exception as e:
        return render_template_string(TOOL_PAGE, error="Invalid or Unsupported Link")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("video_url")
    quality = request.form.get("quality")
    uid = str(uuid.uuid4())[:8]

    if quality == "audio":
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.mp3")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": file_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }
    else:
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.mp4")
        if quality == "360":
            fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif quality == "720":
            fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif quality == "1080":
            fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        else:
            fmt = "best"

        ydl_opts = {
            "format": fmt,
            "outtmpl": file_path,
            "merge_output_format": "mp4",
            "quiet": True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except:
                pass
            return response

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Download Failed: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
