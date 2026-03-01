
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
        <a href="/tool" class="btn btn-main mt-4 btn-lg">Launch Downloader</a>
    </div>

    <div class="row mt-4">
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-bolt fa-2x mb-3 text-info"></i><h5>Super Fast</h5><p class="small text-muted">High-speed servers for instant downloads.</p></div></div>
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-shield-alt fa-2x mb-3 text-success"></i><h5>Secure</h5><p class="small text-muted">No login required. Your privacy is our priority.</p></div></div>
        <div class="col-md-4"><div class="card-box text-center"><i class="fas fa-mobile-alt fa-2x mb-3 text-warning"></i><h5>Responsive</h5><p class="small text-muted">Optimized for all mobile and desktop devices.</p></div></div>
    </div>

    <div class="ad-box">ADVERTISEMENT - PLACEHOLDER</div>
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
                <input type="text" name="url" class="form-control bg-dark text-white border-secondary" placeholder="Paste Instagram, Pinterest or Snapchat link..." required>
                <button class="btn btn-primary px-4">Fetch</button>
            </div>
        </form>

        <div class="ad-box">ADVERTISEMENT</div>

        {{% if result %}}
        <div class="mt-4 animate__animated animate__fadeIn">
            <h5 class="mb-3 text-truncate">{{{{ result.title }}}}</h5>
            {{% if result.preview %}}
            <video controls style="width:100%; border-radius:15px; border: 1px solid #444;">
                <source src="{{{{ result.preview }}}}" type="video/mp4">
            </video>
            {{% endif %}}
            <form method="POST" action="/download">
                <input type="hidden" name="video_url" value="{{{{ result.original_url }}}}">
                <button class="btn btn-success w-100 mt-3 py-3 fw-bold">Download High Quality MP4</button>
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

BLOG_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Guides & Articles - Universal Pro</title></head>
<body>
{NAVBAR}
<div class="container py-5">
    <h2 class="mb-5 text-center fw-bold">Latest <span class="brand-text">Guides</span></h2>

    <div class="row">
        <div class="col-md-6">
            <div class="blog-card">
                <h5>1. How to download Instagram Reels in 4K?</h5>
                <p class="small text-muted">Use our tool to paste the Reels link. We automatically detect the highest resolution available, often up to 4K, for a crystal clear experience.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>2. Saving Snapchat Spotlight Videos</h5>
                <p class="small text-muted">Copy the Spotlight link from Snapchat. Our backend processes it to provide a direct download link without needing to screen record.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>3. Best Pinterest Video Downloader 2024</h5>
                <p class="small text-muted">Pinterest videos can be tricky. Universal Pro ensures you get the mp4 format directly, skipping the embedded player limitations.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>4. Tips for High-Quality Video Downloads</h5>
                <p class="small text-muted">Always check the link type. For Instagram, public profiles work best. We fetch the best available bitrate for you.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>5. Is it legal to download social media videos?</h5>
                <p class="small text-muted">Downloading for personal offline viewing is generally okay. Always respect copyright and do not distribute content without permission.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>6. Top 5 Instagram Story Downloaders</h5>
                <p class="small text-muted">While we focus on Reels and posts, using our tool ensures you get media without watermarks, unlike official download options.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>7. How to convert Pinterest Videos to MP3</h5>
                <p class="small text-muted">Download the video first using our tool, then use any free online converter to extract the audio effortlessly.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>8. Downloading Private Videos: The Truth</h5>
                <p class="small text-muted">Our tool strictly respects privacy settings. Only public videos from public profiles can be downloaded for security reasons.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>9. Mobile vs Desktop Downloaders</h5>
                <p class="small text-muted">Both platforms work equally well. The tool is fully responsive, ensuring smooth saving directly to your gallery or downloads folder.</p>
            </div>
        </div>
        <div class="col-md-6">
            <div class="blog-card">
                <h5>10. Fixing 'Link Not Found' Errors</h5>
                <p class="small text-muted">Ensure the link is public and not broken. Sometimes, removing tracking parameters (like ?utm_source) helps fetch the video correctly.</p>
            </div>
        </div>
    </div>
</div>
{FOOTER}
</body></html>
"""

ABOUT_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>About Us - Universal Pro</title></head>
<body>
{NAVBAR}
<div class="container py-5" style="max-width: 800px;">
    <div class="card-box">
        <h2 class="brand-text">About Universal Pro</h2>
        <p class="mt-4 text-muted">Universal Pro Downloader is a leading web-based tool designed to help users download media from social platforms like Instagram, Snapchat, and Pinterest. Our mission is to provide a seamless, ad-light, and fast experience for everyone.</p>
        <p class="text-muted">Developed and maintained by <strong>sknadeem</strong>, this tool utilizes advanced algorithms to fetch the highest quality available for your favorite content.</p>
        <hr class="border-secondary my-4">
        <h5>Meet the Creator</h5>
        <p class="text-muted">This project is powered by <strong>sknadeem</strong>. For updates and support, follow on Instagram: <a href="https://www.instagram.com/_sknadeem_/" target="_blank" style="color:#667eea; text-decoration:none;">@_sknadeem_</a></p>
    </div>
</div>
{FOOTER}
</body></html>
"""

CONTACT_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Contact Us - Universal Pro</title></head>
<body>
{NAVBAR}
<div class="container py-5" style="max-width: 600px;">
    <div class="card-box">
        <h2 class="brand-text text-center">Contact Us</h2>
        <p class="text-center text-muted mb-4">Have questions or feedback?</p>
        <div class="mb-4 text-center">
            <i class="fas fa-envelope fa-2x text-primary mb-2"></i>
            <p><strong>Email:</strong> nadeemshaik2007@gmail.com</p>
        </div>
        <div class="text-center">
            <i class="fab fa-instagram fa-2x text-danger mb-2"></i>
            <p><strong>DM on Instagram:</strong> <a href="https://www.instagram.com/_sknadeem_/" target="_blank" style="color:#667eea; text-decoration:none;">@_sknadeem_</a></p>
        </div>
        <hr class="border-secondary my-4">
        <p class="small text-muted text-center">We usually respond within 24-48 hours.</p>
    </div>
</div>
{FOOTER}
</body></html>
"""

PRIVACY_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Privacy Policy</title></head>
<body>
{NAVBAR}
<div class="container py-5">
    <div class="card-box">
        <h2 class="mb-4">Privacy Policy</h2>
        <p class="text-muted">At Universal Pro Downloader, accessible from this website, one of our main priorities is the privacy of our visitors. This Privacy Policy document contains types of information that is collected and recorded by us and how we use it.</p>
        <h4 class="text-white">1. Data Collection</h4>
        <p class="text-muted">We do not require any user registration or personal data like name or address. We do not store the videos you download.</p>
        <h4 class="text-white">2. Log Files</h4>
        <p class="text-muted">Universal Pro Downloader follows a standard procedure of using log files. These files log visitors when they visit websites.</p>
        <h4 class="text-white">3. Cookies</h4>
        <p class="text-muted">We may use cookies to improve user experience and analyze traffic.</p>
        <h4 class="text-white">4. Third-Party Ads</h4>
        <p class="text-muted">We use Google AdSense to serve ads. Google may use DART cookies to serve ads based on your visit to our site.</p>
    </div>
</div>
{FOOTER}
</body></html>
"""

TERMS_PAGE = f"""
<!DOCTYPE html><html><head>{COMMON_HEAD}<title>Terms & Conditions</title></head>
<body>
{NAVBAR}
<div class="container py-5">
    <div class="card-box">
        <h2 class="mb-4">Terms & Conditions</h2>
        <p class="text-muted">By using this website, you agree to comply with the following terms:</p>
        <ul class="text-muted">
            <li>You must not use this tool to download copyrighted content without permission.</li>
            <li>The tool is provided for personal use only.</li>
            <li>We are not responsible for how users use the downloaded media.</li>
            <li>We are not affiliated with Instagram, Snapchat, or Pinterest.</li>
        </ul>
        <p class="text-muted">Universal Pro Downloader (Powered by sknadeem) reserves the right to modify these terms at any time.</p>
    </div>
</div>
{FOOTER}
</body></html>
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

@app.route("/analyze", methods=["POST"])
def analyze():
    url = request.form.get("url")
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            preview_url = None
            for f in info.get("formats", []):
                if f.get("ext") == "mp4" and f.get("acodec") != "none" and f.get("vcodec") != "none":
                    preview_url = f.get("url")
                    break
            result = {
                "title": info.get("title", "Video"),
                "preview": preview_url,
                "original_url": url,
            }
            return render_template_string(TOOL_PAGE, result=result)
    except:
        return render_template_string(TOOL_PAGE, error="Invalid or Unsupported Link. Make sure the profile is public.")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("video_url")
    uid = str(uuid.uuid4())[:8]
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.mp4")
    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": file_path,
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
