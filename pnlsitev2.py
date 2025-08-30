import subprocess
import sys
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import json
import os
import time
import threading
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "cappybeam_secret_key_1234"

USERS_FILE = "users.json"
SMS_APIS_FILE = "sms_apis.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_sms_apis():
    if not os.path.exists(SMS_APIS_FILE):
        # Varsayılan SMS API'leri
        default_apis = [
            {"name": "Service 1", "url": "https://api.example1.com/sms?number={phone}&message={message}"},
            {"name": "Service 2", "url": "https://api.example2.com/send?to={phone}&text={message}"},
            {"name": "Service 3", "url": "https://api.example3.com/api?phone={phone}&sms={message}"}
        ]
        with open(SMS_APIS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_apis, f, indent=2, ensure_ascii=False)
        return default_apis
    with open(SMS_APIS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sms_apis(apis):
    with open(SMS_APIS_FILE, "w", encoding="utf-8") as f:
        json.dump(apis, f, indent=2, ensure_ascii=False)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

# Tüm API'lerin tanımlandığı sözlük
API_URLS = {
    "telegram": lambda username, _: f"https://api.hexnox.pro/sowixapi/telegram_sorgu.php?username={username}",
    "isyeri": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeri.php?tc={tc}",
    "hane": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hane.php?tc={tc}",
    "baba": lambda tc, _: f"https://api.hexnox.pro/sowixapi/baba.php?tc={tc}",
    "anne": lambda tc, _: f"https://api.hexnox.pro/sowixapi/anne.php?tc={tc}",
    "ayak": lambda tc, _: f"http://api.hexnox.pro/sowixapi/ayak.php?tc={tc}",
    "boy": lambda tc, _: f"http://api.hexnox.pro/sowixapi/boy.php?tc={tc}",
    "burc": lambda tc, _: f"http://api.hexnox.pro/sowixapi/burc.php?tc={tc}",
    "cm": lambda tc, _: f"http://api.hexnox.pro/sowixapi/cm.php?tc={tc}",
    "cocuk": lambda tc, _: f"http://api.hexnox.pro/sowixapi/cocuk.php?tc={tc}",
    "ehlt": lambda tc, _: f"http://api.hexnox.pro/sowixapi/ehlt.php?tc={tc}",
    "email_sorgu": lambda email, _: f"http://api.hexnox.pro/sowixapi/email_sorgu.php?email={email}",
    "havadurumu": lambda sehir, _: f"http://api.hexnox.pro/sowixapi/havadurumu.php?sehir={sehir}",
    "imei": lambda imei, _: f"https://api.hexnox.pro/sowixapi/imei.php?imei={imei}",
    "operator": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/operator.php?gsm={gsm}",
    "hikaye": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hikaye.php?tc={tc}",
    "hanepro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hanepro.php?tc={tc}",
    "muhallev": lambda tc, _: f"https://api.hexnox.pro/sowixapi/muhallev.php?tc={tc}",
    "lgs": lambda tc, _: f"http://hexnox.pro/sowixfree/lgs/lgs.php?tc={tc}",
    "plaka": lambda plaka, _: f"http://hexnox.pro/sowixfree/plaka.php?plaka={plaka}",
    "nude": lambda _, __: f"http://hexnox.pro/sowixfree/nude.php",
    "sertifika": lambda tc, _: f"http://hexnox.pro/sowixfree/sertifika.php?tc={tc}",
    "aracparca": lambda plaka, _: f"https://hexnox.pro/sowixfree/aracparca.php?plaka={plaka}",
    "şehit": lambda ad_soyad, _: f"https://hexnox.pro/sowixfree/şehit.php?Ad={ad_soyad.split(' ')[0] if ad_soyad else ''}&Soyad={ad_soyad.split(' ')[1] if ad_soyad and ' ' in ad_soyad else ''}",
    "interpol": lambda ad_soyad, _: f"https://hexnox.pro/sowixfree/interpol.php?ad={ad_soyad.split(' ')[0] if ad_soyad else ''}&soyad={ad_soyad.split(' ')[1] if ad_soyad and ' ' in ad_soyad else ''}",
    "personel": lambda tc, _: f"https://hexnox.pro/sowixfree/personel.php?tc={tc}",
    "internet": lambda tc, _: f"https://hexnox.pro/sowixfree/internet.php?tc={tc}",
    "nvi": lambda tc, _: f"https://hexnox.pro/sowixfree/nvi.php?tc={tc}",
    "nezcane": lambda il_ilce, _: f"https://hexnox.pro/sowixfree/nezcane.php?il={il_ilce.split(' ')[0] if il_ilce else ''}&ilce={il_ilce.split(' ')[1] if il_ilce and ' ' in il_ilce else ''}",
    "basvuru": lambda tc, _: f"https://hexnox.pro/sowixfree/basvuru/basvuru.php?tc={tc}",
    "diploma": lambda tc, _: f"https://hexnox.pro/sowixfree/diploma/diploma.php?tc={tc}",
    "facebook": lambda numara, _: f"https://hexnox.pro/sowixfree/facebook.php?numara={numara}",
    "vergi": lambda tc, _: f"https://hexnox.pro/sowixfree/vergi/vergi.php?tc={tc}",
    "premadres": lambda tc, _: f"https://hexnox.pro/sowixfree/premadres.php?tc={tc}",
    "sgkpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sgkpro.php?tc={tc}",
    "mhrs": lambda tc, _: f"https://hexnox.pro/sowixfree/mhrs/mhrs.php?tc={tc}",
    "premad": lambda ad_il_ilce, _: f"https://api.hexnox.pro/sowixapi/premad.php?ad={ad_il_ilce.split(' ')[0] if ad_il_ilce else ''}&il={ad_il_ilce.split(' ')[1] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 1 else ''}&ilce={ad_il_ilce.split(' ')[2] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 2 else ''}",
    "fatura": lambda tc, _: f"https://hexnox.pro/sowixfree/fatura.php?tc={tc}",
    "subdomain": lambda url, _: f"https://api.hexnox.pro/sowixapi/subdomain.php?url={url}",
    "sexgörsel": lambda soru, _: f"https://hexnox.pro/sowixfree/sexgörsel.php?soru={soru}",
    "meslek": lambda tc, _: f"https://api.hexnox.pro/sowixapi/meslek.php?tc={tc}",
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "adsoyadil": lambda ad, soyad_il: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad_il.split(' ')[0] if soyad_il else ''}&il={soyad_il.split(' ')[1] if soyad_il and ' ' in soyad_il else ''}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sulale.php?tc={tc}",
    "vesika": lambda tc, _: f"http://20.122.193.203/apiservice/woxy/tc.php?tc={tc}&auth=woxynindaramcigi",
    "allvesika": lambda tc, _: f"http://84.32.15.160/apiservice/woxy/allvesika.php?tc={tc}&auth=cyberinsikimemesiamigotu",
    "okulsicil": lambda tc, _: f"https://merial.cfd/Daimon/freePeker/okulsicil.php?tc={tc}",
    "kizlik": lambda tc, _: f"http://212.68.34.148/apiservices/kizlik?tc={tc}",
    "okulno": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulno.php?tc={tc}",
    "isyeriyetkili": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={tc}",
    "gsmdetay": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={gsm}",
    "gsm": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsm.php?gsm={gsm}",
    "adres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/adres.php?tc={tc}",
}

# SMS bomber durumunu takip etmek için global değişken
sms_bomber_active = False
sms_bomber_thread = None

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <title>Giriş Yap - CBS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    /* Özel kaydırma çubuğu stilleri */
    ::-webkit-scrollbar {
      width: 12px;
      height: 12px;
    }

    ::-webkit-scrollbar-track {
      background: #3a3a3a;
      border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb {
      background: #555;
      border-radius: 6px;
      border: 2px solid #3a3a3a;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: #666;
    }

    /* Firefox için */
    * {
      scrollbar-width: thin;
      scrollbar-color: #555 #3a3a3a;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif;}
    body,html{height:100%;background:#2c2c2c;display:flex;justify-content:center;align-items:center;}
    .container {
      width: 360px;
      background: #3a3a3a;
      padding: 40px 30px;
      border-radius: 25px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      text-align:center;
      border: 1px solid #555;
    }
    .logo {
      width: 120px;
      height: 120px;
      margin: 0 auto 25px;
      border-radius: 50%;
      overflow: hidden;
      box-shadow: 0 0 20px rgba(0,0,0,0.3);
    }
    .logo img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 50%;
    }
    h2 {
      color: #e0e0e0;
      margin-bottom: 30px;
      font-weight: 600;
      letter-spacing: 1px;
      font-size: 1.8rem;
    }
    label {
      display: block;
      text-align: left;
      margin-bottom: 8px;
      font-weight: 600;
      color: #ccc;
    }
    input {
      width: 100%;
      padding: 12px 15px;
      border-radius: 8px;
      border: 1px solid #555;
      margin-bottom: 20px;
      font-size: 1rem;
      outline:none;
      transition: 0.3s;
      background: #4a4a4a;
      color: #e0e0e0;
    }
    input:focus {
      border-color: #0a4cff;
      box-shadow: 0 0 0 2px rgba(10,76,255,0.2);
    }
    button {
      width: 100%;
      padding: 14px 0;
      background: #0a4cff;
      border: none;
      color: white;
      font-weight: 600;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: 0.3s;
    }
    button:hover {
      background: #083ecf;
    }
    .error {
      margin-bottom: 15px;
      color: #ff6b6b;
      font-weight: 600;
      font-size: 0.9rem;
    }
    .link {
      margin-top: 15px;
      font-size: 0.9rem;
      color: #aaa;
    }
    .link a {
      color: #0a4cff;
      text-decoration: none;
      font-weight: 600;
    }
    .link a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container" role="main">
    <div class="logo" aria-label="Cappy Logo">
      <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo"/>
    </div>
    <h2>Giriş Yap</h2>
    {% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}
    <form method="POST" action="{{ url_for('login') }}" novalidate>
      <label for="username">Kullanıcı Adı</label>
      <input type="text" id="username" name="username" required autocomplete="username" />
      <label for="password">Şifre</label>
      <input type="password" id="password" name="password" required autocomplete="current-password" />
      <button type="submit">Giriş</button>
    </form>
    <div class="link" role="link" aria-label="Kayıt ol linki">
      Henüz hesabın yok mu? <a href="{{ url_for('register') }}">Kayıt Ol</a>
    </div>
  </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <title>Kayıt Ol - CBS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    /* Özel kaydırma çubuğu stilleri */
    ::-webkit-scrollbar {
      width: 12px;
      height: 12px;
    }

    ::-webkit-scrollbar-track {
      background: #3a3a3a;
      border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb {
      background: #555;
      border-radius: 6px;
      border: 2px solid #3a3a3a;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: #666;
    }

    /* Firefox için */
    * {
      scrollbar-width: thin;
      scrollbar-color: #555 #3a3a3a;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif;}
    body,html{height:100%;background:#2c2c2c;display:flex;justify-content:center;align-items:center;}
    .container {
      width: 360px;
      background: #3a3a3a;
      padding: 40px 30px;
      border-radius: 25px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      text-align:center;
      border: 1px solid #555;
    }
    .logo {
      width: 120px;
      height: 120px;
      margin: 0 auto 25px;
      border-radius: 50%;
      overflow: hidden;
      box-shadow: 0 0 20px rgba(0,0,0,0.3);
    }
    .logo img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 50%;
    }
    h2 {
      color: #e0e0e0;
      margin-bottom: 30px;
      font-weight: 600;
      letter-spacing: 1px;
      font-size: 1.8rem;
    }
    label {
      display: block;
      text-align: left;
      margin-bottom: 8px;
      font-weight: 600;
      color: #ccc;
    }
    input {
      width: 100%;
      padding: 12px 15px;
      border-radius: 8px;
      border: 1px solid #555;
      margin-bottom: 20px;
      font-size: 1rem;
      outline:none;
      transition: 0.3s;
      background: #4a4a4a;
      color: #e0e0e0;
    }
    input:focus {
      border-color: #0a4cff;
      box-shadow: 0 0 0 2px rgba(10,76,255,0.2);
    }
    button {
      width: 100%;
      padding: 14px 0;
      background: #0a4cff;
      border: none;
      color: white;
      font-weight: 600;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: 0.3s;
    }
    button:hover {
      background: #083ecf;
    }
    .error {
      margin-bottom: 15px;
      color: #ff6b6b;
      font-weight: 600;
      font-size: 0.9rem;
    }
    .link {
      margin-top: 15px;
      font-size: 0.9rem;
      color: #aaa;
    }
    .link a {
      color: #0a4cff;
      text-decoration: none;
      font-weight: 600;
    }
    .link a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <div class="container" role="main">
    <div class="logo" aria-label="Cappy Logo">
      <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo"/>
    </div>
    <h2>Kayıt Ol</h2>
    {% if error %}<div class="error" role="alert">{{ error }}</div>{% endif %}
    <form method="POST" action="{{ url_for('register') }}" novalidate>
      <label for="username">Kullanıcı Adı</label>
      <input type="text" id="username" name="username" required autocomplete="username" />
      <label for="password">Şifre</label>
      <input type="password" id="password" name="password" required autocomplete="new-password" />
      <label for="password2">Şifre Tekrar</label>
      <input type="password" id="password2" name="password2" required autocomplete="new-password" />
      <button type="submit">Kayıt Ol</button>
    </form>
    <div class="link" role="link" aria-label="Giriş yap linki">
      Zaten hesabın var mı? <a href="{{ url_for('login') }}">Giriş Yap</a>
    </div>
  </div>
</body>
</html>
"""

PANEL_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <title>CAPPYBEAMSERVICES! Panel</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    /* Özel kaydırma çubuğu stilleri */
    ::-webkit-scrollbar {
      width: 12px;
      height: 12px;
    }

    ::-webkit-scrollbar-track {
      background: #3a3a3a;
      border-radius: 6px;
    }

    ::-webkit-scrollbar-thumb {
      background: #555;
      border-radius: 6px;
      border: 2px solid #3a3a3a;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: #666;
    }

    /* Firefox için */
    * {
      scrollbar-width: thin;
      scrollbar-color: #555 #3a3a3a;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
    *{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif;}
    body,html {
      height: 100%;
      background: #2c2c2c;
      color: #e0e0e0;
      display: flex;
      flex-direction: column;
      font-size: 15px;
    }
    header {
      background: #3a3a3a;
      color: #e0e0e0;
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      border-bottom: 1px solid #555;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    header h1 {
      font-weight: 700;
      font-size: 1.4rem;
      letter-spacing: 1px;
      user-select:none;
      color: #0a4cff;
    }
    #logout-btn {
      background: #4a4a4a;
      border: 1px solid #666;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      color: #e0e0e0;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.3s ease;
    }
    #logout-btn:hover {
      background: #5a5a5a;
      border-color: #777;
    }
    main {
      flex-grow: 1;
      display: flex;
      height: calc(100vh - 64px);
      overflow: hidden;
      background: #2c2c2c;
    }
    nav {
      width: 240px;
      background: #3a3a3a;
      border-right: 1px solid #555;
      padding: 1.2rem 1rem;
      overflow-y: auto;
      box-shadow: 2px 0 10px rgba(0,0,0,0.2);
      transition: transform 0.3s ease;
    }
    nav.hide {
      transform: translateX(-100%);
    }
    nav h2 {
      font-weight: 600;
      margin-bottom: 1rem;
      color: #ccc;
      user-select:none;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid #555;
      font-size: 1.1rem;
    }
    nav ul {
      list-style: none;
    }
    nav ul li {
      margin-bottom: 0.5rem;
    }
    nav ul li button {
      width: 100%;
      background: transparent;
      border: none;
      text-align: left;
      padding: 0.5rem 0.8rem;
      border-radius: 6px;
      font-weight: 500;
      color: #ccc;
      cursor: pointer;
      transition: all 0.3s ease;
      font-size: 0.95rem;
      display: flex;
      align-items: center;
    }
    nav ul li button i {
      margin-right: 8px;
      font-size: 1rem;
      width: 20px;
      text-align: center;
    }
    nav ul li button:hover,
    nav ul li button.active {
      background: #4a4a4a;
      color: #0a4cff;
    }
    nav ul li button.active {
      font-weight: 600;
    }
    #hamburger {
      position: absolute;
      top: 15px;
      left: 15px;
      width: 30px;
      height: 24px;
      display: none;
      flex-direction: column;
      justify-content: space-between;
      cursor: pointer;
      z-index: 1001;
    }
    #hamburger div {
      height: 3px;
      background: #e0e0e0;
      border-radius: 3px;
      transition: 0.3s ease;
    }
    #hamburger.active div:nth-child(1) {
      transform: translateY(10px) rotate(45deg);
    }
    #hamburger.active div:nth-child(2) {
      opacity: 0;
    }
    #hamburger.active div:nth-child(3) {
      transform: translateY(-10px) rotate(-45deg);
    }
    section#content {
      flex-grow: 1;
      padding: 1.5rem 2rem;
      overflow-y: auto;
      background: #2c2c2c;
      user-select:none;
    }
    .home-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      padding: 2rem;
    }
    .home-logo {
      width: 180px;
      height: 180px;
      margin-bottom: 2rem;
      border-radius: 50%;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0,0,0,0.3);
      border: 5px solid #4a4a4a;
    }
    .home-logo img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      border-radius: 50%;
    }
    .home-title {
      font-size: 2.2rem;
      font-weight: 700;
      color: #0a4cff;
      margin-bottom: 1rem;
    }
    .home-subtitle {
      font-size: 1.1rem;
      color: #aaa;
      max-width: 600px;
      line-height: 1.6;
    }
    form {
      max-width: 500px;
      margin-top: 1rem;
      background: #3a3a3a;
      padding: 1.5rem;
      border-radius: 10px;
      box-shadow: 0 2px 15px rgba(0,0,0,0.2);
      border: 1px solid #555;
    }
    label {
      display: block;
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #ccc;
      font-size: 0.95rem;
    }
    input[type="text"],
    input[type="tel"],
    input[type="number"] {
      width: 100%;
      padding: 0.6rem 0.8rem;
      font-size: 0.95rem;
      border-radius: 6px;
      border: 1px solid #555;
      margin-bottom: 1rem;
      outline: none;
      transition: 0.3s;
      color: #e0e0e0;
      background: #4a4a4a;
    }
    input[type="text"]:focus,
    input[type="tel"]:focus,
    input[type="number"]:focus {
      border-color: #0a4cff;
      box-shadow: 0 0 0 2px rgba(10,76,255,0.1);
      background: #5a5a5a;
    }
    button.submit-btn {
      background: #0a4cff;
      border: none;
      padding: 0.7rem 1.2rem;
      border-radius: 6px;
      font-weight: 600;
      color: white;
      font-size: 0.95rem;
      cursor: pointer;
      transition: background 0.3s ease;
      width: 100%;
    }
    button.submit-btn:hover {
      background: #083ecf;
    }
    .result-container {
      margin-top: 1.5rem;
      border: 1px solid #555;
      border-radius: 8px;
      padding: 0;
      background: #3a3a3a;
      box-shadow: 0 2px 15px rgba(0,0,0,0.2);
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.9rem;
      color: #e0e0e0;
      max-height: 500px;
      overflow-y: auto;
      user-select: text;
    }
    .result-table {
      width: 100%;
      border-collapse: collapse;
    }
    .result-table th {
      background: #4a4a4a;
      padding: 0.6rem 0.8rem;
      text-align: left;
      font-weight: 600;
      font-size: 0.85rem;
      color: #ccc;
      border-bottom: 1px solid #555;
    }
    .result-table td {
      padding: 0.6rem 0.8rem;
      border-bottom: 1px solid #555;
      font-size: 0.85rem;
      color: #e0e0e0;
    }
    .result-table tr:last-child td {
      border-bottom: none;
    }
    .result-table tr:hover td {
      background: #4a4a4a;
    }
    .loading {
      display: inline-block;
      width: 20px;
      height: 20px;
      border: 3px solid rgba(10,76,255,0.2);
      border-radius: 50%;
      border-top-color: #0a4cff;
      animation: spin 1s ease-in-out infinite;
      margin-right: 10px;
      vertical-align: middle;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .sms-bomber-controls {
      display: flex;
      gap: 10px;
      margin-top: 15px;
      flex-wrap: wrap;
    }
    .sms-bomber-controls button {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      min-width: 120px;
    }
    #start-bomber {
      background: #e74c3c;
      color: white;
    }
    #stop-bomber {
      background: #2ecc71;
      color: white;
    }
    #sms-api-manager {
      background: #3498db;
      color: white;
    }
    .bomber-status {
      margin-top: 15px;
      padding: 10px;
      border-radius: 6px;
      text-align: center;
      font-weight: 600;
    }
    .bomber-status.active {
      background: #2ecc71;
      color: white;
    }
    .bomber-status.inactive {
      background: #e74c3c;
      color: white;
    }
    .warning {
      background: #f39c12;
      color: white;
      padding: 10px;
      border-radius: 6px;
      margin-bottom: 15px;
      text-align: center;
    }
    .category {
      margin-top: 20px;
      padding: 10px;
      border-bottom: 1px solid #555;
      color: #0a4cff;
      font-weight: 600;
    }
    @media (max-width: 850px) {
      nav {
        position: fixed;
        top: 0;
        left: 0;
        height: 100%;
        z-index: 1000;
        transform: translateX(-100%);
        background: #3a3a3a;
        box-shadow: 3px 0 15px rgba(0,0,0,0.3);
      }
      nav.show {
        transform: translateX(0);
      }
      #hamburger {
        display: flex;
      }
      main {
        flex-direction: column;
        height: auto;
      }
      section#content {
        padding: 1.2rem;
      }
      .home-logo {
        width: 140px;
        height: 140px;
      }
      .home-title {
        font-size: 1.8rem;
      }
      .sms-bomber-controls button {
        min-width: 100px;
        font-size: 0.8rem;
      }
    }
  </style>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
<header>
  <h1>CAPPYBEAMSERVICES</h1>
  <button id="logout-btn" aria-label="Çıkış yap"><i class="fas fa-sign-out-alt"></i> Çıkış Yap</button>
  <div id="hamburger" aria-label="Menüyü aç/kapat" role="button" tabindex="0" aria-expanded="false">
    <div></div><div></div><div></div>
  </div>
</header>
<main>
  <nav aria-label="Sorgu menüsü">
    <h2>Sorgular</h2>
    <ul>
      <li><button class="query-btn active" data-query="home"><i class="fas fa-home"></i> Anasayfa</button></li>
      
      <div class="category">Kişisel Sorgular</div>
      <li><button class="query-btn" data-query="adsoyad"><i class="fas fa-user"></i> Ad Soyad</button></li>
      <li><button class="query-btn" data-query="adsoyadil"><i class="fas fa-user-tag"></i> Ad Soyad İl</button></li>
      <li><button class="query-btn" data-query="tcpro"><i class="fas fa-id-card"></i> TC Kimlik No</button></li>
      <li><button class="query-btn" data-query="tcgsm"><i class="fas fa-phone"></i> TC GSM</button></li>
      <li><button class="query-btn" data-query="tapu"><i class="fas fa-home"></i> Tapu</button></li>
      <li><button class="query-btn" data-query="sulale"><i class="fas fa-users"></i> Sülale</button></li>
      <li><button class="query-btn" data-query="vesika"><i class="fas fa-id-badge"></i> Vesika</button></li>
      <li><button class="query-btn" data-query="allvesika"><i class="fas fa-id-card-alt"></i> Tüm Vesika</button></li>
      <li><button class="query-btn" data-query="okulsicil"><i class="fas fa-graduation-cap"></i> Okul Sicil</button></li>
      <li><button class="query-btn" data-query="kizlik"><i class="fas fa-female"></i> Kızlık Soyadı</button></li>
      <li><button class="query-btn" data-query="okulno"><i class="fas fa-school"></i> Okul No</button></li>
      <li><button class="query-btn" data-query="isyeriyetkili"><i class="fas fa-briefcase"></i> İşyeri Yetkili</button></li>
      <li><button class="query-btn" data-query="gsmdetay"><i class="fas fa-mobile-alt"></i> GSM Detay</button></li>
      <li><button class="query-btn" data-query="gsm"><i class="fas fa-phone-alt"></i> GSM</button></li>
      <li><button class="query-btn" data-query="adres"><i class="fas fa-map-marker-alt"></i> Adres</button></li>
      <li><button class="query-btn" data-query="hane"><i class="fas fa-house-user"></i> Hane</button></li>
      <li><button class="query-btn" data-query="baba"><i class="fas fa-male"></i> Baba</button></li>
      <li><button class="query-btn" data-query="anne"><i class="fas fa-female"></i> Anne</button></li>
      <li><button class="query-btn" data-query="ayak"><i class="fas fa-shoe-prints"></i> Ayak No</button></li>
      <li><button class="query-btn" data-query="boy"><i class="fas fa-ruler-vertical"></i> Boy</button></li>
      <li><button class="query-btn" data-query="burc"><i class="fas fa-star"></i> Burç</button></li>
      <li><button class="query-btn" data-query="cm"><i class="fas fa-ruler"></i> CM</button></li>
      <li><button class="query-btn" data-query="cocuk"><i class="fas fa-child"></i> Çocuk</button></li>
      <li><button class="query-btn" data-query="ehlt"><i class="fas fa-users"></i> EHLT</button></li>
      <li><button class="query-btn" data-query="hanepro"><i class="fas fa-house-user"></i> Hane Pro</button></li>
      <li><button class="query-btn" data-query="muhallev"><i class="fas fa-building"></i> Muhallev</button></li>
      <li><button class="query-btn" data-query="personel"><i class="fas fa-user-tie"></i> Personel</button></li>
      <li><button class="query-btn" data-query="internet"><i class="fas fa-wifi"></i> Internet</button></li>
      <li><button class="query-btn" data-query="nvi"><i class="fas fa-address-card"></i> NVI</button></li>
      <li><button class="query-btn" data-query="sgkpro"><i class="fas fa-file-medical"></i> SGK Pro</button></li>
      <li><button class="query-btn" data-query="mhrs"><i class="fas fa-hospital"></i> MHRS</button></li>
      <li><button class="query-btn" data-query="fatura"><i class="fas fa-file-invoice"></i> Fatura</button></li>
      <li><button class="query-btn" data-query="meslek"><i class="fas fa-briefcase"></i> Meslek</button></li>
      
      <div class="category">Diğer Sorgular</div>
      <li><button class="query-btn" data-query="telegram"><i class="fab fa-telegram"></i> Telegram</button></li>
      <li><button class="query-btn" data-query="email_sorgu"><i class="fas fa-envelope"></i> Email</button></li>
      <li><button class="query-btn" data-query="havadurumu"><i class="fas fa-cloud-sun"></i> Hava Durumu</button></li>
      <li><button class="query-btn" data-query="imei"><i class="fas fa-mobile"></i> IMEI</button></li>
      <li><button class="query-btn" data-query="operator"><i class="fas fa-sim-card"></i> Operatör</button></li>
      <li><button class="query-btn" data-query="hikaye"><i class="fas fa-book"></i> Hikaye</button></li>
      <li><button class="query-btn" data-query="lgs"><i class="fas fa-graduation-cap"></i> LGS</button></li>
      <li><button class="query-btn" data-query="plaka"><i class="fas fa-car"></i> Plaka</button></li>
      <li><button class="query-btn" data-query="nude"><i class="fas fa-ban"></i> Nude</button></li>
      <li><button class="query-btn" data-query="sertifika"><i class="fas fa-certificate"></i> Sertifika</button></li>
      <li><button class="query-btn" data-query="aracparca"><i class="fas fa-car-side"></i> Araç Parça</button></li>
      <li><button class="query-btn" data-query="şehit"><i class="fas fa-star-of-life"></i> Şehit</button></li>
      <li><button class="query-btn" data-query="interpol"><i class="fas fa-globe"></i> Interpol</button></li>
      <li><button class="query-btn" data-query="nezcane"><i class="fas fa-gavel"></i> Nezcane</button></li>
      <li><button class="query-btn" data-query="basvuru"><i class="fas fa-file-alt"></i> Başvuru</button></li>
      <li><button class="query-btn" data-query="diploma"><i class="fas fa-graduation-cap"></i> Diploma</button></li>
      <li><button class="query-btn" data-query="facebook"><i class="fab fa-facebook"></i> Facebook</button></li>
      <li><button class="query-btn" data-query="vergi"><i class="fas fa-receipt"></i> Vergi</button></li>
      <li><button class="query-btn" data-query="premadres"><i class="fas fa-address-book"></i> Premadres</button></li>
      <li><button class="query-btn" data-query="premad"><i class="fas fa-user-plus"></i> Premad</button></li>
      <li><button class="query-btn" data-query="subdomain"><i class="fas fa-globe"></i> Subdomain</button></li>
      <li><button class="query-btn" data-query="sexgörsel"><i class="fas fa-image"></i> Sex Görsel</button></li>
      
      <div class="category">Araçlar</div>
      <li><button class="query-btn" data-query="smsbomber"><i class="fas fa-bomb"></i> SMS Bomber</button></li>
      <li><button class="query-btn" data-query="smsapi"><i class="fas fa-cog"></i> SMS API Yönetimi</button></li>
    </ul>
  </nav>
  <section id="content" tabindex="0" aria-live="polite" aria-atomic="true">
    <div class="home-container" id="home-container">
      <div class="home-logo">
        <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo"/>
      </div>
      <h1 class="home-title">CAPPYBEAMSERVICES</h1>
      <p class="home-subtitle">
        Hoşgeldin, {{ session['user'] }}!<br />
        Sol menüden sorgu seçip sorgularınızı güvenli bir şekilde yapabilirsiniz.
      </p>
    </div>
    <form id="query-form" style="display:none;" aria-label="Sorgu formu">
      <label id="label1" for="input1">Değer 1:</label>
      <input type="text" id="input1" name="input1" required autocomplete="off" />
      <label id="label2" for="input2">Değer 2 (Opsiyonel):</label>
      <input type="text" id="input2" name="input2" autocomplete="off" placeholder="İkinci değer (gerekirse)" />
      <button type="submit" class="submit-btn" aria-label="Sorguyu çalıştır"><i class="fas fa-search"></i> Sorgula</button>
    </form>
    <div id="sms-bomber-form" style="display:none;">
      <div class="warning">
        <i class="fas fa-exclamation-triangle"></i> UYARI: SMS Bomber etik olmayan amaçlar için kullanılmamalıdır. Sadece kendi telefonunuza test amaçlı kullanın.
      </div>
      <form id="bomber-form">
        <label for="phone-number">Telefon Numarası:</label>
        <input type="tel" id="phone-number" name="phone" required placeholder="5XX XXX XX XX" pattern="5[0-9]{2} [0-9]{3} [0-9]{2} [0-9]{2}" />
        <label for="request-count">İstek Sayısı:</label>
        <input type="number" id="request-count" name="count" required min="1" max="100" value="10" />
        <label for="message">Mesaj (Opsiyonel):</label>
        <input type="text" id="message" name="message" placeholder="Varsayılan mesaj kullanılacak" />
        <button type="submit" class="submit-btn" id="start-bomber"><i class="fas fa-play"></i> Başlat</button>
      </form>
      <div class="sms-bomber-controls">
        <button id="stop-bomber" disabled><i class="fas fa-stop"></i> Durdur</button>
        <button id="sms-api-manager"><i class="fas fa-cog"></i> API Yönetimi</button>
      </div>
      <div class="bomber-status inactive" id="bomber-status">
        Durum: Hazır
      </div>
      <div class="result-container" id="bomber-result" style="display:none;"></div>
    </div>
    <div id="sms-api-management" style="display:none;">
      <h2>SMS API Yönetimi</h2>
      <div class="warning">
        <i class="fas fa-exclamation-triangle"></i> UYARI: SMS API'leri çalışma zamanında değiştirilebilir. Geçerli API'lerin çalıştığından emin olun.
      </div>
      <div id="api-list"></div>
      <form id="add-api-form">
        <h3>Yeni API Ekle</h3>
        <label for="api-name">API Adı:</label>
        <input type="text" id="api-name" name="name" required />
        <label for="api-url">API URL ({{phone}} ve {{message}} yer tutucularını içermeli):</label>
        <input type="text" id="api-url" name="url" required placeholder="https://api.example.com/sms?number={{phone}}&text={{message}}" />
        <button type="submit" class="submit-btn"><i class="fas fa-plus"></i> API Ekle</button>
      </form>
    </div>
    <div class="result-container" id="result-container" aria-live="polite" aria-atomic="true" style="display:none;"></div>
  </section>
</main>

<script>
  const hamburger = document.getElementById('hamburger');
  const nav = document.querySelector('nav');
  hamburger.addEventListener('click', () => {
    nav.classList.toggle('show');
    hamburger.classList.toggle('active');
    const expanded = hamburger.getAttribute('aria-expanded') === 'true' || false;
    hamburger.setAttribute('aria-expanded', !expanded);
  });
  hamburger.addEventListener('keydown', e => {
    if(e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      hamburger.click();
    }
  });

  const queryButtons = document.querySelectorAll('.query-btn');
  const form = document.getElementById('query-form');
  const smsBomberForm = document.getElementById('sms-bomber-form');
  const smsApiManagement = document.getElementById('sms-api-management');
  const label1 = document.getElementById('label1');
  const label2 = document.getElementById('label2');
  const input1 = document.getElementById('input1');
  const input2 = document.getElementById('input2');
  const resultContainer = document.getElementById('result-container');
  const homeContainer = document.getElementById('home-container');
  const bomberForm = document.getElementById('bomber-form');
  const bomberResult = document.getElementById('bomber-result');
  const bomberStatus = document.getElementById('bomber-status');
  const startBomberBtn = document.getElementById('start-bomber');
  const stopBomberBtn = document.getElementById('stop-bomber');
  const smsApiManagerBtn = document.getElementById('sms-api-manager');
  const apiList = document.getElementById('api-list');
  const addApiForm = document.getElementById('add-api-form');

  const queryLabels = {
    "home": ["", ""],
    "telegram": ["Kullanıcı Adı", ""],
    "isyeri": ["TC Kimlik No", ""],
    "hane": ["TC Kimlik No", ""],
    "baba": ["TC Kimlik No", ""],
    "anne": ["TC Kimlik No", ""],
    "ayak": ["TC Kimlik No", ""],
    "boy": ["TC Kimlik No", ""],
    "burc": ["TC Kimlik No", ""],
    "cm": ["TC Kimlik No", ""],
    "cocuk": ["TC Kimlik No", ""],
    "ehlt": ["TC Kimlik No", ""],
    "email_sorgu": ["Email Adresi", ""],
    "havadurumu": ["Şehir", ""],
    "imei": ["IMEI Numarası", ""],
    "operator": ["GSM Numarası", ""],
    "hikaye": ["TC Kimlik No", ""],
    "hanepro": ["TC Kimlik No", ""],
    "muhallev": ["TC Kimlik No", ""],
    "lgs": ["TC Kimlik No", ""],
    "plaka": ["Plaka", ""],
    "nude": ["", ""],
    "sertifika": ["TC Kimlik No", ""],
    "aracparca": ["Plaka", ""],
    "şehit": ["Ad Soyad", ""],
    "interpol": ["Ad Soyad", ""],
    "personel": ["TC Kimlik No", ""],
    "internet": ["TC Kimlik No", ""],
    "nvi": ["TC Kimlik No", ""],
    "nezcane": ["İl İlçe", ""],
    "basvuru": ["TC Kimlik No", ""],
    "diploma": ["TC Kimlik No", ""],
    "facebook": ["Telefon Numarası", ""],
    "vergi": ["TC Kimlik No", ""],
    "premadres": ["TC Kimlik No", ""],
    "sgkpro": ["TC Kimlik No", ""],
    "mhrs": ["TC Kimlik No", ""],
    "premad": ["Ad İl İlçe", ""],
    "fatura": ["TC Kimlik No", ""],
    "subdomain": ["URL", ""],
    "sexgörsel": ["Soru", ""],
    "meslek": ["TC Kimlik No", ""],
    "adsoyad": ["Ad", "Soyad"],
    "adsoyadil": ["Ad", "Soyad veya Soyad+İl (Opsiyonel)"],
    "tcpro": ["TC Kimlik No", ""],
    "tcgsm": ["TC Kimlik No", ""],
    "tapu": ["TC Kimlik No", ""],
    "sulale": ["TC Kimlik No", ""],
    "vesika": ["TC Kimlik No", ""],
    "allvesika": ["TC Kimlik No", ""],
    "okulsicil": ["TC Kimlik No", ""],
    "kizlik": ["TC Kimlik No", ""],
    "okulno": ["TC Kimlik No", ""],
    "isyeriyetkili": ["TC Kimlik No", ""],
    "gsmdetay": ["GSM Numarası", ""],
    "gsm": ["GSM Numarası", ""],
    "adres": ["TC Kimlik No", ""],
    "smsbomber": ["SMS Bomber", ""],
    "smsapi": ["SMS API Yönetimi", ""]
  };

  function updateFormFields(queryKey) {
    if(queryKey === "home") {
      homeContainer.style.display = "flex";
      form.style.display = "none";
      smsBomberForm.style.display = "none";
      smsApiManagement.style.display = "none";
      resultContainer.style.display = "none";
      return;
    }

    if(queryKey === "smsbomber") {
      homeContainer.style.display = "none";
      form.style.display = "none";
      smsBomberForm.style.display = "block";
      smsApiManagement.style.display = "none";
      resultContainer.style.display = "none";
      return;
    }

    if(queryKey === "smsapi") {
      homeContainer.style.display = "none";
      form.style.display = "none";
      smsBomberForm.style.display = "none";
      smsApiManagement.style.display = "block";
      resultContainer.style.display = "none";
      loadApiList();
      return;
    }

    const labels = queryLabels[queryKey] || ["Input1","Input2"];
    label1.textContent = labels[0];
    label2.textContent = labels[1];
    input1.value = "";
    input2.value = "";
    
    if(labels[1] === "") {
      label2.style.display = "none";
      input2.style.display = "none";
      input2.required = false;
    } else {
      label2.style.display = "block";
      input2.style.display = "block";
      input2.required = true;
      
      if(queryKey === "adsoyadil") {
        input2.placeholder = "Sadece soyad veya 'soyad il' şeklinde girin";
      } else if(queryKey === "şehit" || queryKey === "interpol") {
        input2.placeholder = "Ad Soyad (örn: Ahmet Yılmaz)";
      } else if(queryKey === "nezcane") {
        input2.placeholder = "İl İlçe (örn: İstanbul Kadıköy)";
      } else if(queryKey === "premad") {
        input2.placeholder = "Ad İl İlçe (örn: Mehmet İstanbul Üsküdar)";
      } else {
        input2.placeholder = "İkinci değer";
      }
    }
    
    resultContainer.textContent = "";
    resultContainer.style.display = "none";
    homeContainer.style.display = "none";
    smsBomberForm.style.display = "none";
    smsApiManagement.style.display = "none";
    form.style.display = "block";
    input1.focus();
  }

  let currentQuery = "home";
  updateFormFields(currentQuery);

  queryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      queryButtons.forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      currentQuery = btn.dataset.query;
      updateFormFields(currentQuery);
      if(window.innerWidth <= 850){
        nav.classList.remove('show');
        hamburger.classList.remove('active');
        hamburger.setAttribute('aria-expanded', false);
      }
    });
  });

  function createTableFromData(data) {
    if (!data) return "<p>Sonuç bulunamadı.</p>";

    if (Array.isArray(data)) {
      if (data.length === 0) return "<p>Sonuç bulunamadı.</p>";

      const allColumns = new Set();
      data.forEach(item => {
        Object.keys(item).forEach(key => allColumns.add(key));
      });
      const columns = Array.from(allColumns);

      let html = '<table class="result-table"><thead><tr>';

      columns.forEach(column => {
        html += `<th>${column.toUpperCase()}</th>`;
      });
      html += '</tr></thead><tbody>';

      data.forEach(row => {
        html += '<tr>';
        columns.forEach(column => {
          html += `<td>${row[column] || ''}</td>`;
        });
        html += '</tr>';
      });

      html += '</tbody></table>';
      return html;
    }

    if (typeof data === 'object') {
      let html = '<table class="result-table"><tbody>';
      for (const key in data) {
        if (data.hasOwnProperty(key)) {
          const value = typeof data[key] === 'object' ? JSON.stringify(data[key]) : data[key];
          html += `<tr><th>${key.toUpperCase()}</th><td>${value || ''}</td></tr>`;
        }
      }
      html += '</tbody></table>';
      return html;
    }

    return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    resultContainer.innerHTML = '<div style="padding:1rem;text-align:center;"><span class="loading"></span> Sorgulanıyor, lütfen bekleyin...</div>';
    resultContainer.style.display = "block";

    const val1 = input1.value.trim();
    const val2 = input2.value.trim();

    if(val1 === "" || (input2.required && val2 === "")) {
      resultContainer.innerHTML = '<div style="padding:1rem;color:#ff6b6b;font-weight:600;">Lütfen tüm zorunlu alanları doldurunuz.</div>';
      return;
    }

    fetch("/api/query", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        query: currentQuery,
        val1: val1,
        val2: val2
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('API hatası');
      }
      return response.json();
    })
    .then(data => {
      if (data.error) {
        resultContainer.innerHTML = `<div style="padding:1rem;color:#ff6b6b;font-weight:600;">Hata: ${data.error}</div>`;
      } else {
        resultContainer.innerHTML = createTableFromData(data.result);
      }
    })
    .catch(error => {
      resultContainer.innerHTML = `<div style="padding:1rem;color:#ff6b6b;font-weight:600;">İstek sırasında hata oluştu: ${error.message}</div>`;
    });
  });

  // SMS Bomber fonksiyonları
  let bomberInterval = null;
  let bomberActive = false;

  bomberForm.addEventListener('submit', e => {
    e.preventDefault();
    const phone = document.getElementById('phone-number').value.trim();
    const count = parseInt(document.getElementById('request-count').value);
    const message = document.getElementById('message').value.trim() || "Test mesajı";

    if(!phone) {
      alert("Lütfen telefon numarası girin.");
      return;
    }

    startBomberBtn.disabled = true;
    stopBomberBtn.disabled = false;
    bomberStatus.textContent = "Durum: Çalışıyor...";
    bomberStatus.className = "bomber-status active";
    bomberResult.style.display = "block";
    bomberResult.innerHTML = "<div style='padding:1rem;text-align:center;'><span class='loading'></span> SMS gönderiliyor...</div>";

    bomberActive = true;
    let sentCount = 0;
    let successCount = 0;
    let errorCount = 0;

    bomberInterval = setInterval(async () => {
      if(!bomberActive || sentCount >= count) {
        clearInterval(bomberInterval);
        startBomberBtn.disabled = false;
        stopBomberBtn.disabled = true;
        bomberStatus.textContent = "Durum: Tamamlandı";
        bomberStatus.className = "bomber-status inactive";
        bomberResult.innerHTML = `
          <div style="padding:1rem;">
            <h3>SMS Bomber Sonuçları</h3>
            <p>Toplam İstek: ${sentCount}</p>
            <p>Başarılı: ${successCount}</p>
            <p>Başarısız: ${errorCount}</p>
          </div>
        `;
        return;
      }

      sentCount++;

      try {
        const response = await fetch("/api/sms-bomber", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({phone, message})
        });

        const data = await response.json();
        if(data.success) {
          successCount++;
        } else {
          errorCount++;
        }

        bomberResult.innerHTML = `
          <div style="padding:1rem;">
            <h3>SMS Bomber Çalışıyor</h3>
            <p>Gönderilen: ${sentCount}/${count}</p>
            <p>Başarılı: ${successCount}</p>
            <p>Başarısız: ${errorCount}</p>
          </div>
        `;
      } catch (error) {
        errorCount++;
        bomberResult.innerHTML = `
          <div style="padding:1rem;">
            <h3>SMS Bomber Çalışıyor</h3>
            <p>Gönderilen: ${sentCount}/${count}</p>
            <p>Başarılı: ${successCount}</p>
            <p>Başarısız: ${errorCount}</p>
            <p style="color:#ff6b6b;">Son hata: ${error.message}</p>
          </div>
        `;
      }
    }, 1000);
  });

  stopBomberBtn.addEventListener('click', () => {
    bomberActive = false;
    clearInterval(bomberInterval);
    startBomberBtn.disabled = false;
    stopBomberBtn.disabled = true;
    bomberStatus.textContent = "Durum: Durduruldu";
    bomberStatus.className = "bomber-status inactive";
  });

  smsApiManagerBtn.addEventListener('click', () => {
    updateFormFields("smsapi");
  });

  // API yönetimi fonksiyonları
  function loadApiList() {
    fetch("/api/sms-apis")
      .then(response => response.json())
      .then(apis => {
        let html = "<h3>Mevcut API'ler</h3>";
        if(apis.length === 0) {
          html += "<p>Henüz API eklenmemiş.</p>";
        } else {
          html += "<ul style='list-style:none;padding:0;'>";
          apis.forEach((api, index) => {
            html += `
              <li style='padding:10px;border:1px solid #555;margin-bottom:10px;border-radius:6px;background:#4a4a4a;'>
                <strong style='color:#ccc;'>${api.name}</strong>: <span style='color:#aaa;'>${api.url}</span>
                <button style='margin-left:10px;padding:5px 10px;background:#e74c3c;color:white;border:none;border-radius:4px;cursor:pointer;' onclick='deleteApi(${index})'>Sil</button>
              </li>
            `;
          });
          html += "</ul>";
        }
        apiList.innerHTML = html;
      });
  }

  window.deleteApi = function(index) {
    if(confirm("Bu API'yi silmek istediğinize emin misiniz?")) {
      fetch("/api/sms-apis", {
        method: "DELETE",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({index})
      })
      .then(response => response.json())
      .then(data => {
        if(data.success) {
          loadApiList();
        } else {
          alert("API silinirken hata oluştu: " + data.error);
        }
      });
    }
  };

  addApiForm.addEventListener('submit', e => {
    e.preventDefault();
    const name = document.getElementById('api-name').value.trim();
    const url = document.getElementById('api-url').value.trim();

    if(!name || !url) {
      alert("Lütfen tüm alanları doldurun.");
      return;
    }

    if(!url.includes("{{phone}}") || !url.includes("{{message}}")) {
      alert("API URL'si {{phone}} ve {{message}} yer tutucularını içermelidir.");
      return;
    }

    fetch("/api/sms-apis", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({name, url})
    })
    .then(response => response.json())
    .then(data => {
      if(data.success) {
        document.getElementById('api-name').value = "";
        document.getElementById('api-url').value = "";
        loadApiList();
        alert("API başarıyla eklendi.");
      } else {
        alert("API eklenirken hata oluştu: " + data.error);
        }
    });
  });

  document.getElementById("logout-btn").addEventListener("click", () => {
    window.location.href = "/logout";
  });
</script>

</body>
</html>
"""

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("panel"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        users = load_users()
        if username in users and check_password_hash(users[username]["password"], password):
            session["user"] = username
            return redirect(url_for("panel"))
        else:
            error = "Kullanıcı adı veya şifre hatalı."
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not username or not password or not password2:
            error = "Tüm alanları doldurun."
        elif password != password2:
            error = "Şifreler eşleşmiyor."
        else:
            users = load_users()
            if username in users:
                error = "Bu kullanıcı adı zaten alınmış."
            else:
                users[username] = {
                    "password": generate_password_hash(password)
                }
                save_users(users)
                session["user"] = username
                return redirect(url_for("panel"))
    return render_template_string(REGISTER_HTML, error=error)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/panel")
@login_required
def panel():
    return render_template_string(PANEL_HTML)

@app.route("/api/query", methods=["POST"])
@login_required
def api_query():
    data = request.get_json()
    query = data.get("query")
    val1 = data.get("val1")
    val2 = data.get("val2")

    if query not in API_URLS:
        return jsonify({"error": "Geçersiz sorgu tipi."})

    url_func = API_URLS[query]

    try:
        if query == "nude":
            # Özel durum: nude sorgusu için ikinci parametre gerekmez
            url = url_func("", "")
        elif query in ["şehit", "interpol"]:
            # Ad Soyad sorguları
            if val1 and ' ' in val1:
                parts = val1.split(' ')
                ad = parts[0]
                soyad = ' '.join(parts[1:])
                url = url_func(f"{ad} {soyad}", val2)
            else:
                url = url_func(val1, val2)
        elif query == "nezcane":
            # İl İlçe sorgusu
            if val1 and ' ' in val1:
                parts = val1.split(' ')
                il = parts[0]
                ilce = ' '.join(parts[1:])
                url = url_func(f"{il} {ilce}", val2)
            else:
                url = url_func(val1, val2)
        elif query == "premad":
            # Ad İl İlçe sorgusu
            if val1 and ' ' in val1:
                parts = val1.split(' ')
                if len(parts) >= 3:
                    ad = parts[0]
                    il = parts[1]
                    ilce = ' '.join(parts[2:])
                    url = url_func(f"{ad} {il} {ilce}", val2)
                elif len(parts) == 2:
                    ad = parts[0]
                    il = parts[1]
                    url = url_func(f"{ad} {il}", val2)
                else:
                    url = url_func(val1, val2)
            else:
                url = url_func(val1, val2)
        else:
            url = url_func(val1, val2)

        r = requests.get(url, timeout=15)
        r.raise_for_status()

        try:
            result = r.json()

            if isinstance(result, list):
                return jsonify({"result": result})
            elif isinstance(result, dict) and ("data" in result or "results" in result):
                return jsonify({"result": result.get("data", result.get("results"))})
            else:
                return jsonify({"result": result})
        except ValueError:
            return jsonify({"result": r.text})
    except Exception as e:
        return jsonify({"error": f"API sorgusu başarısız: {str(e)}"})

# SMS Bomber API endpoint'leri
@app.route("/api/sms-bomber", methods=["POST"])
@login_required
def sms_bomber():
    data = request.get_json()
    phone = data.get("phone")
    message = data.get("message", "Test mesajı")

    if not phone:
                return jsonify({"success": False, "error": "Telefon numarası gerekli"})

    sms_apis = load_sms_apis()
    results = []

    for api in sms_apis:
        try:
            url = api["url"].replace("{{phone}}", phone).replace("{{message}}", message)
            response = requests.get(url, timeout=10)
            results.append({
                "api": api["name"],
                "status": response.status_code,
                "success": response.status_code == 200
            })
        except Exception as e:
            results.append({
                "api": api["name"],
                "error": str(e),
                "success": False
            })

    # Başarılı olan herhangi bir istek varsa başarılı dön
    success = any(result["success"] for result in results)
    return jsonify({"success": success, "results": results})

@app.route("/api/sms-apis", methods=["GET", "POST", "DELETE"])
@login_required
def manage_sms_apis():
    if request.method == "GET":
        apis = load_sms_apis()
        return jsonify(apis)

    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        url = data.get("url")

        if not name or not url:
            return jsonify({"success": False, "error": "Name and URL are required"})

        apis = load_sms_apis()
        apis.append({"name": name, "url": url})
        save_sms_apis(apis)

        return jsonify({"success": True})

    elif request.method == "DELETE":
        data = request.get_json()
        index = data.get("index")

        if index is None:
            return jsonify({"success": False, "error": "Index is required"})

        apis = load_sms_apis()
        if 0 <= index < len(apis):
            apis.pop(index)
            save_sms_apis(apis)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid index"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

