import os, uuid
from flask import Flask, render_template_string, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# ---------------- SHARED STYLES & NAV ----------------
COMMON_HEAD = """
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google-adsense-account" content="ca-pub-4065684390234340">
<script async
src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4065684390234340"
crossorigin="anonymous"></script>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<style>
    body{background:#0a0a12; color:#ffffff; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6;}
    .navbar { background: rgba(22, 22, 37, 0.95); backdrop-filter: blur(10px); border-bottom: 1px solid #333; }
    .nav-link { color: #ffffff !important; font-weight: 500; }
    .nav-link:hover { color: #667eea !important; }
    .hero{text-align:center; padding:100px 20px 60px;}
    .btn-main{padding:14px 35px; border-radius:12px; background:linear-gradient(45deg,#764ba2,#667eea); border:none; color:white; font-weight:600; transition: 0.3s;}
    .btn-main:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(118, 75, 162, 0.3); }
    .card-box{background:#161625; padding:30px; border-radius:24px; border: 1px solid #2d2d3f; margin-top:30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);}
    .ad-box{background:#11111f; border:1px solid #333; padding:20px; text-align:center; color:#555; border-radius:15px; margin:20px 0; font-size: 0.8rem;}
    footer { background: #07070c; padding: 40px 0; border-top: 1px solid #222; margin-top: 50px; text-align: center; }
    .footer-link { color: #ffffff; text-decoration: none; margin: 0 10px; font-size: 0.9rem; }
    .footer-link:hover { color: #667eea; }
    .brand-text { background: linear-gradient(45deg, #764ba2, #667eea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
    .blog-card { background: #161625; border-radius: 15px; padding: 20px; margin-bottom: 20px; border-left: 4px solid #764ba2; transition: 0.3s; cursor: pointer; text-decoration: none; display: block; color: #ffffff; }
    .blog-card:hover { transform: scale(1.02); background: #1c1c2e; }
    h1, h2, h3, h4, h5, p, span, li { color: #ffffff !important; }
    .text-muted { color: #b0b0b0 !important; }
</style>
"""

AD_UNIT_CODE = """
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4065684390234340"
     data-ad-slot="YOUR_AD_SLOT_HERE"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""

NAVBAR = """
<nav class="navbar navbar-expand-lg sticky-top navbar-dark">
    <div class="container">
        <a class="navbar-brand fw-bold" href="/">UP <span class="brand-text">Downloader</span></a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
                <li class="nav-item"><a class="nav-link" href="/">Home</a></li>
                <li class="nav-item"><a class="nav-link" href="/tool">Downloader</a></li>
                <li class="nav-item"><a class="nav-link" href="/blog">Blog</a></li>
                <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
                <li class="nav-item"><a class="nav-link" href="/contact">Contact</a></li>
            </ul>
        </div>
    </div>
</nav>
"""

FOOTER = """
<footer>
    <div class="container">
        <p>Powered by <a href="https://www.instagram.com/_sknadeem_/" target="_blank" class="text-info" style="text-decoration:none;">sknadeem</a></p>
        <div class="mb-3">
            <a href="/privacy" class="footer-link">Privacy Policy</a>
            <a href="/terms" class="footer-link">Terms & Conditions</a>
            <a href="/contact" class="footer-link">Support</a>
        </div>
        <p style="font-size: 0.8rem; color: #ffffff;">© 2024 Universal Pro Downloader. Developed by <a href="https://www.instagram.com/_sknadeem_/" target="_blank" style="color:#764ba2; text-decoration:none;">@_sknadeem_</a></p>
    </div>
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
"""

# ---------------- PAGES (BLOG, ABOUT, CONTACT, etc.) ----------------

LANDING_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Universal Pro Downloader</title></head>
<body>
{NAVBAR}
<div class="container">
    <div class="hero">
        <h1 class="display-4 fw-bold">Universal Pro <span class="brand-text">Downloader</span></h1>
        <p class="lead mt-3 text-muted">The fastest way to save Snapchat, Pinterest, and Instagram Reels in HD.</p>
        <a href="/tool" class="btn btn-main mt-4 btn-lg">Launch Downloader</a>
    </div>
    <div class="ad-box">{AD_UNIT_CODE}</div>
</div>
{FOOTER}
</body></html>
"""

TOOL_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Pro Downloader Tool</title></head>
<body>
{NAVBAR}
<div class="container" style="max-width: 700px;">
    <div class="card-box">
        <h3 class="text-center mb-4">Paste Video Link</h3>
        <form method="POST" action="/analyze">
            <div class="input-group mb-3">
                <input type="text" name="url" class="form-control bg-dark text-white border-secondary" placeholder="Paste link..." required>
                <button class="btn btn-primary px-4">Fetch</button>
            </div>
        </form>
        <div class="ad-box">{AD_UNIT_CODE}</div>
        {{% if result %}}
        <div class="mt-4">
            <h5 class="mb-3">{{{{ result.title }}}}</h5>
            <form method="POST" action="/download">
                <input type="hidden" name="video_url" value="{{{{ result.original_url }}}}">
                <button class="btn btn-success w-100 py-3 fw-bold">Download High Quality MP4</button>
            </form>
        </div>
        {{% endif %}}
        {{% if error %}}
        <div class="alert alert-danger mt-3">{{{{ error }}}}</div>
        {{% endif %}}
    </div>
</div>
{FOOTER}
</body></html>
"""

BLOG_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Guides - Universal Pro</title></head>
<body>{NAVBAR}<div class="container py-5">
<h2 class="mb-5 text-center fw-bold">Latest <span class="brand-text">Guides</span></h2>
<div class="row">
<div class="col-md-6"><div class="blog-card"><h5>1. How to download Instagram Reels?</h5><p class="small text-muted">Paste the link and get HD video instantly.</p></div></div>
<div class="col-md-6"><div class="blog-card"><h5>2. Snapchat Spotlight Saving</h5><p class="small text-muted">Direct download for Snapchat videos.</p></div></div>
</div></div>{FOOTER}</body></html>
"""

ABOUT_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>About Us</title></head>
<body>{NAVBAR}<div class="container py-5"><div class="card-box"><h2>About Universal Pro</h2><p>Developed by sknadeem for fast HD downloads.</p></div></div>{FOOTER}</body></html>
"""

CONTACT_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Contact Us</title></head>
<body>{NAVBAR}<div class="container py-5 text-center"><div class="card-box"><h2>Contact Us</h2><p>Email: nadeemshaik2007@gmail.com</p></div></div>{FOOTER}</body></html>
"""

PRIVACY_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Privacy Policy</title></head><body>{NAVBAR}<div class="container py-5"><div class="card-box"><h2>Privacy Policy</h2><p>We do not store your data.</p></div></div>{FOOTER}</body></html>"""
TERMS_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Terms</title></head><body>{NAVBAR}<div class="container py-5"><div class="card-box"><h2>Terms & Conditions</h2><p>For personal use only.</p></div></div>{FOOTER}</body></html>"""

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

@app.route("/about")
def about():
    return render_template_string(ABOUT_PAGE)

@app.route("/contact")
def contact():
    return render_template_string(CONTACT_PAGE)

@app.route("/privacy")
def privacy():
    return render_template_string(PRIVACY_PAGE)

@app.route("/terms")
def terms():
    return render_template_string(TERMS_PAGE)

# --- ZAROORI ROUTES FOR ADSENSE ---
@app.route("/ads.txt")
def ads_txt():
    return "google.com, pub-4065684390234340, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

@app.route("/robots.txt")
def robots_txt():
    return "User-agent: *\nAllow: /", 200, {'Content-Type': 'text/plain'}

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.form.get("url")
    if not url:
        return render_template_string(TOOL_PAGE, error="Please paste a valid URL.")
    try:
        ydl_opts = {"quiet": True, "no_warnings": True, "format": "best[ext=mp4]/best"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            result = {"title": info.get("title", "Video"), "original_url": url}
            return render_template_string(TOOL_PAGE, result=result)
    except Exception as e:
        return render_template_string(TOOL_PAGE, error=str(e))

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("video_url")
    uid = str(uuid.uuid4())[:8]
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.mp4")
    try:
        ydl_opts = {"format": "best[ext=mp4]/best", "outtmpl": file_path, "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        @after_this_request
        def remove_file(response):
            try: os.remove(file_path)
            except: pass
            return response
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Download Failed: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
