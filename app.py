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

<script src="https://pl28887357.effectivegatecpm.com/f4/11/25/f4112594a7523e1fadb297e68ce1e46a.js"></script>

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
    .ad-slot-header { width: 100%; text-align: center; margin-bottom: 20px; }
</style>

<script>
    // Har click par ad refresh ya show karne ke liye logic
    function triggerAd() {
        // Agar aapke paas direct link hai toh window.open bhi kar sakte hain
        // ya simply ad script ko reload hone denge browser interaction se
        console.log("Ad Triggered");
    }
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

# ---------------- PAGES ----------------

LANDING_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Universal Pro Downloader</title></head>
<body>
{NAVBAR}
<div class="container">
    <div class="hero">
        <h1 class="display-4 fw-bold">Universal Pro <span class="brand-text">Downloader</span></h1>
        <p class="lead mt-3 text-muted">The fastest way to save Snapchat, Pinterest, and Instagram Reels in HD.</p>
        <a href="/tool" onclick="triggerAd()" class="btn btn-main mt-4 btn-lg">Launch Downloader</a>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-bolt fa-2x mb-3 text-info"></i><h5>Super Fast</h5><p class="small text-muted">High-speed servers for instant downloads.</p></div></div>
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-shield-alt fa-2x mb-3 text-success"></i><h5>Secure</h5><p class="small text-muted">No login required. Your privacy is our priority.</p></div></div>
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-mobile-alt fa-2x mb-3 text-warning"></i><h5>Responsive</h5><p class="small text-muted">Optimized for all mobile and desktop devices.</p></div></div>
    </div>
</div>
{FOOTER}
</body></html>
"""

TOOL_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Pro Downloader Tool</title></head>
<body>
{NAVBAR}
<div class="container" style="max-width: 700px;">
    
    <div class="ad-slot-header">
       </div>

    <div class="card-box">
        <h3 class="text-center mb-4">Paste Video Link</h3>
        <form method="POST" action="/analyze">
            <div class="input-group mb-3">
                <input type="text" name="url" class="form-control bg-dark text-white border-secondary" placeholder="Paste Instagram, YouTube, Pinterest or Snapchat link..." required>
                <button class="btn btn-primary px-4" onclick="triggerAd()">Fetch</button>
            </div>
        </form>
        
        {{% if result %}}
        <div class="mt-4 animate__animated animate__fadeIn">
            <h5 class="mb-3 text-truncate">{{{{ result.title }}}}</h5>

            <div class="ad-box">Advertisement</div>

            {{% if result.preview %}}
            <video controls style="width:100%; border-radius:15px; border: 1px solid #444;">
                <source src="{{{{ result.preview }}}}" type="video/mp4">
            </video>
            {{% endif %}}
            <form method="POST" action="/download">
                <input type="hidden" name="video_url" value="{{{{ result.original_url }}}}">
                <button class="btn btn-success w-100 mt-3 py-3 fw-bold" onclick="triggerAd()">Download High Quality MP4</button>
            </form>
        </div>
        {{% endif %}}

        {{% if error %}}
        <div class="alert alert-danger mt-3 bg-danger text-white border-0">{{{{ error }}}}</div>
        {{% endif %}}
    </div>
</div>
{FOOTER}
</body></html>
"""

# ... (BLOG_PAGE, ABOUT_PAGE, CONTACT_PAGE, PRIVACY_PAGE, TERMS_PAGE - Paste your original ones here)
BLOG_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Guides & Articles - Universal Pro</title></head><body>{NAVBAR}<div class="container py-5"><h2 class="mb-5 text-center fw-bold">Latest <span class="brand-text">Guides</span></h2><div class="row"><div class="col-md-6"><div class="blog-card"><h5>1. How to download Instagram Reels in 4K?</h5><p class="small text-muted">Use our tool to paste the Reels link.</p></div></div><div class="col-md-6"><div class="blog-card"><h5>2. Saving Snapchat Spotlight Videos</h5><p class="small text-muted">Copy the Spotlight link from Snapchat.</p></div></div></div></div>{FOOTER}</body></html>"""
ABOUT_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>About Us - Universal Pro</title></head><body>{NAVBAR}<div class="container py-5" style="max-width: 800px;"><div class="card-box"><h2 class="brand-text">About Universal Pro</h2><p class="mt-4 text-muted">Universal Pro Downloader is a leading web-based tool.</p></div></div>{FOOTER}</body></html>"""
CONTACT_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Contact Us - Universal Pro</title></head><body>{NAVBAR}<div class="container py-5" style="max-width: 600px;"><div class="card-box"><h2 class="brand-text text-center">Contact Us</h2><p class="text-center text-muted mb-4">nadeemshaik2007@gmail.com</p></div></div>{FOOTER}</body></html>"""
PRIVACY_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Privacy Policy</title></head><body>{NAVBAR}<div class="container py-5"><div class="card-box"><h2>Privacy Policy</h2><p class="text-muted">We do not store the videos you download.</p></div></div>{FOOTER}</body></html>"""
TERMS_PAGE = f"""<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Terms & Conditions</title></head><body>{NAVBAR}<div class="container py-5"><div class="card-box"><h2>Terms & Conditions</h2><ul class="text-muted"><li>Personal use only.</li></ul></div></div>{FOOTER}</body></html>"""

# ---------------- ROUTES ----------------

@app.route("/")
def home(): return render_template_string(LANDING_PAGE)

@app.route("/blog")
def blog(): return render_template_string(BLOG_PAGE)

@app.route("/tool")
def tool(): return render_template_string(TOOL_PAGE)

@app.route("/about")
def about(): return render_template_string(ABOUT_PAGE)

@app.route("/contact")
def contact(): return render_template_string(CONTACT_PAGE)

@app.route("/privacy")
def privacy(): return render_template_string(PRIVACY_PAGE)

@app.route("/terms")
def terms(): return render_template_string(TERMS_PAGE)

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.form.get("url")
    if not url:
        return render_template_string(TOOL_PAGE, error="Please paste a valid URL.")
    
    try:
        # PINTEREST & SNAPCHAT FIX: added user-agent and referer
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "best[ext=mp4]/best",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "referer": "https://www.pinterest.com/",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            preview_url = info.get("url")
            if "formats" in info:
                for f in info.get("formats", []):
                    if f.get("ext") == "mp4" and f.get("vcodec") != "none":
                        preview_url = f.get("url")
                        break

            result = {"title": info.get("title", "Video"), "preview": preview_url, "original_url": url}
            return render_template_string(TOOL_PAGE, result=result)
    except Exception as e:
        return render_template_string(TOOL_PAGE, error=f"Error: {str(e)}. Make sure the link is public.")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("video_url")
    if not url: return "No URL provided", 400
        
    uid = str(uuid.uuid4())[:8]
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.mp4")
    
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": file_path,
        "quiet": True,
        "no_warnings": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    
    try:
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
