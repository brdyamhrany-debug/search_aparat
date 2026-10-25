#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# loc.py - Aparat User Search on localhost
# Run: python loc.py 8000
# Open: http://localhost:8000
import sys
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def parse_port():
    default = 8000
    if len(sys.argv) > 1:
        raw = sys.argv[1].strip()
        if ":" in raw:
            raw = raw.rsplit(":", 1)[-1]
        raw = raw.strip()
        try:
            p = int(raw)
            if 1 <= p <= 65535:
                return p
        except:
            pass
        print(f"[warn] ورودی '{sys.argv[1]}' پورت معتبر نيست. از پورت {default} استفاده مي‌شود.")
        print(f"       مثال درست: python loc.py {default}")
    return default

def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        data = r.read().decode("utf-8", errors="ignore")
        return json.loads(data)

def get_aparat_user(username):
    username = (username or "").strip().lstrip("@").strip()
    if not username:
        return {"ok": False, "error": "آیدی خالی است."}
    if not re.match(r"^[A-Za-z0-9_.\-]+$", username):
        return {"ok": False, "error": "آیدی معتبر نیست. فقط حروف انگلیسی، عدد، _ و . و -"}
    if len(username) < 2 or len(username) > 64:
        return {"ok": False, "error": "طول آیدی معتبر نیست."}
    last_err = ""
    try:
        new_url = "https://www.aparat.com/api/fa/v1/user/user/information/username/" + urllib.parse.quote(username)
        j = fetch_json(new_url)
        data = j.get("data")
        if data and isinstance(data, dict):
            a = data.get("attributes", {}) or {}
            inc = j.get("included", []) or []
            socials = []
            for it in inc:
                if isinstance(it, dict) and it.get("type") == "ProfileMore":
                    s = (it.get("attributes", {}) or {}).get("social", []) or []
                    socials = s
                    break
            pic = a.get("pic_b") or a.get("pic_m") or a.get("pic_s") or ""
            return {
                "ok": True,
                "source": "v1",
                "username": a.get("username") or username,
                "name": a.get("name") or "",
                "userid": str(a.get("id") or data.get("id") or ""),
                "pic": pic,
                "cover": a.get("cover_src") or "",
                "follower": str(a.get("follower_cnt_num") or a.get("follower_cnt") or "0").strip(),
                "following": str(a.get("follow_cnt") or "0").strip(),
                "video_cnt": str(a.get("video_cnt") or "0").strip(),
                "visits": str(a.get("video_visit") or "").strip(),
                "bio": str(a.get("description") or "").strip(),
                "official": "yes" if a.get("official") else "no",
                "date": str(a.get("start_date_jalali") or a.get("start_date") or "").strip(),
                "url_aparat": a.get("url") or ("https://www.aparat.com/" + username),
                "socials": socials,
            }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"ok": False, "error": "کاربری با این آیدی پیدا نشد."}
        last_err = f"HTTP {e.code}"
    except Exception as e:
        last_err = str(e)
    try:
        old_url = "https://www.aparat.com/etc/api/profile/username/" + urllib.parse.quote(username)
        j2 = fetch_json(old_url)
        p = j2.get("profile")
        if p and isinstance(p, dict) and p.get("username"):
            pic = p.get("pic_b") or p.get("pic_m") or p.get("pic_s") or ""
            return {
                "ok": True,
                "source": "etc",
                "username": p.get("username") or username,
                "name": p.get("name") or "",
                "userid": str(p.get("userid") or ""),
                "pic": pic,
                "cover": p.get("cover_src") or "",
                "follower": str(p.get("follower_cnt") or "0"),
                "following": str(p.get("followed_cnt") or "0"),
                "video_cnt": str(p.get("video_cnt") or "0"),
                "visits": "",
                "bio": str(p.get("descr") or ""),
                "official": str(p.get("official") or "no"),
                "date": "",
                "url_aparat": "https://www.aparat.com/" + (p.get("username") or username),
                "socials": [],
            }
        else:
            return {"ok": False, "error": "کاربری با این آیدی پیدا نشد."}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"ok": False, "error": "کاربری با این آیدی پیدا نشد."}
        return {"ok": False, "error": f"خطا از سمت آپارات: HTTP {e.code}"}
    except Exception as e:
        msg = str(e) or last_err or "خطای ناشناخته"
        return {"ok": False, "error": f"خطا در دریافت اطلاعات: {msg}"}

HTML_PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سرچ اکانت آپارات | لوکال‌هاست</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Tahoma, Vazirmatn, sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.wrap{max-width:720px;margin:0 auto;padding:32px 16px 60px}
h1{text-align:center;font-size:22px;margin:10px 0 6px}
p.sub{text-align:center;color:#94a3b8;font-size:13px;margin:0 0 20px}
.card{background:#1e293b;border:1px solid #334155;border-radius:16px;padding:20px}
form{display:flex;gap:10px}
input{flex:1;padding:12px 14px;border-radius:12px;border:1px solid #475569;background:#0f172a;color:#fff;font-size:15px;outline:none}
input:focus{border-color:#38bdf8}
button{padding:12px 20px;border-radius:12px;border:0;background:#38bdf8;color:#04263b;font-weight:bold;font-size:14px;cursor:pointer}
button:hover{background:#7dd3fc}
.hint{font-size:12px;color:#94a3b8;margin-top:10px;line-height:1.9}
#result{margin-top:18px}
.profile{background:#0f172a;border:1px solid #334155;border-radius:16px;padding:20px;display:flex;gap:16px;align-items:flex-start}
.profile img.avatar{width:96px;height:96px;border-radius:50%;object-fit:cover;border:2px solid #38bdf8;background:#334155;flex-shrink:0}
.badge{display:inline-block;font-size:11px;background:#16a34a;color:#fff;padding:2px 8px;border-radius:20px;margin-right:6px}
.stats{display:flex;gap:14px;margin:12px 0;flex-wrap:wrap}
.stat{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:8px 12px;font-size:12px;text-align:center;min-width:90px}
.stat b{display:block;font-size:16px;margin-bottom:2px}
.bio{font-size:13px;line-height:1.9;color:#cbd5e1;background:#1e293b;border-radius:10px;padding:10px 12px;margin:10px 0;white-space:pre-wrap}
a.link{color:#38bdf8;font-size:13px;word-break:break-all}
.row{font-size:13px;margin:6px 0;color:#e2e8f0}
.err{background:#450a0a;border:1px solid #b91c1c;color:#fecaca;padding:12px;border-radius:12px;font-size:13px}
.loading{text-align:center;color:#94a3b8;font-size:13px;padding:16px}
.socials{margin-top:8px;font-size:12px}
.footer{text-align:center;font-size:11px;color:#64748b;margin-top:22px}
@media(max-width:560px){.profile{flex-direction:column;align-items:center;text-align:center}form{flex-direction:column}}
</style>
</head>
<body>
<div class="wrap">
<h1>🔍 سرچ اکانت آپارات</h1>
<p class="sub">روی لوکال‌هاست اجرا می‌شود | عکس کانال + بیو + اطلاعات</p>
<div class="card">
<form onsubmit="return doSearch(event)">
<input id="q" placeholder="آیدی آپارات را بنویس... مثل: alooty" autocomplete="off">
<button type="submit">جست‌وجو</button>
</form>
<div class="hint">مثال لینک لوکال‌هاست برای اشتراک: <span id="share" style="color:#38bdf8"></span><br>آیدی را بدون @ بنویس. بعد از سرچ، لینک صفحه هم با localhost ساخته می‌شود.</div>
<div id="result"></div>
</div>
<div class="footer">loc.py | Aparat Localhost Search</div>
</div>
<script>
function esc(s){return String(s||"").replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
async function doSearch(e){
if(e) e.preventDefault();
var u=document.getElementById("q").value.trim().replace(/^@/,"");
if(!u){document.getElementById("result").innerHTML='<div class="err">اول یه آیدی بنویس.</div>';return false}
var shareUrl=location.origin+"/?u="+encodeURIComponent(u);
document.getElementById("share").textContent=shareUrl;
history.replaceState(null,"","/?u="+encodeURIComponent(u));
document.getElementById("result").innerHTML='<div class="loading">در حال دریافت از آپارات...</div>';
try{
var r=await fetch("/api?username="+encodeURIComponent(u));
var d=await r.json();
if(!d.ok){document.getElementById("result").innerHTML='<div class="err">'+esc(d.error||"پیدا نشد.")+'</div>';return false}
var off=d.official==="yes"?'<span class="badge">✅ رسمی</span>':'';
var bio=d.bio?esc(d.bio):"— بیو ندارد —";
var socials="";
if(d.socials && d.socials.length){
socials='<div class="socials">🔗 سوشال: '+d.socials.map(function(s){return '<a class="link" target="_blank" href="'+esc(s.link)+'">'+esc(s.title)+': '+esc(s.username)+'</a>'}).join(" | ")+'</div>';
}
var cover=d.cover?'<div class="row">🖼️ کاور: <a class="link" target="_blank" href="'+esc(d.cover)+'">مشاهده کاور</a></div>':"";
document.getElementById("result").innerHTML=
'<div class="profile"><img class="avatar" src="'+esc(d.pic)+'" onerror="this.src=\'https://www.aparat.com/public/public/aparat/img/global/avatar-is-channel.png\'">'+
'<div style="flex:1"><div style="font-size:17px;font-weight:bold">'+esc(d.name||d.username)+' '+off+'</div>'+
'<div style="font-size:13px;color:#94a3b8" dir="ltr">@'+esc(d.username)+' | ID: '+esc(d.userid)+'</div>'+
'<div class="stats"><div class="stat"><b>'+esc(d.follower)+'</b>دنبال‌کننده</div><div class="stat"><b>'+esc(d.following)+'</b>دنبال‌شونده</div><div class="stat"><b>'+esc(d.video_cnt)+'</b>ویدیو</div>'+(d.visits?'<div class="stat"><b>'+esc(d.visits)+'</b>بازدید</div>':"")+'</div>'+
'<div class="bio">'+bio+'</div>'+
'<div class="row">📅 ساخت: '+esc(d.date||"نامشخص")+'</div>'+
'<div class="row">🔗 <a class="link" target="_blank" href="'+esc(d.url_aparat)+'">'+esc(d.url_aparat)+'</a></div>'+
cover+
'<div class="row">💾 لینک لوکال‌هاست: <a class="link" href="'+esc(shareUrl)+'">'+esc(shareUrl)+'</a></div>'+
socials+
'</div></div>';
}catch(err){document.getElementById("result").innerHTML='<div class="err">خطا در اتصال به سرور لوکال.</div>'}
return false;
}
(function(){
var p=new URLSearchParams(location.search).get("u");
if(p){document.getElementById("q").value=p;doSearch(null)}
})();
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("[%s] %s\n" % (self.address_string(), fmt % args))
    def send_html(self):
        body = HTML_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            return self.send_html()
        if path == "/api":
            qs = urllib.parse.parse_qs(parsed.query)
            username = (qs.get("username") or [""])[0]
            result = get_aparat_user(username)
            return self.send_json(result)
        if path == "/health":
            return self.send_json({"ok": True})
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Not Found".encode())

def main():
    port = parse_port()
    addr = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(addr, Handler)
    print("=" * 50)
    print(" Aparat Localhost Search running")
    print(f" http://localhost:{port}")
    print(f" http://127.0.0.1:{port}")
    print(f" مثال سرچ: http://localhost:{port}/?u=alooty")
    print(" برای توقف: Ctrl+C")
    print("=" * 50)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\ stopped.")

if __name__ == "__main__":
    main()
