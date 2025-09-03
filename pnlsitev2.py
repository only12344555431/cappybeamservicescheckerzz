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
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "cappybeam_premium_secret_key_2023"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

USERS_FILE = "users.json"
SMS_APIS_FILE = "sms_apis.json"
QUERY_LOGS_FILE = "query_logs.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_sms_apis():
    if not os.path.exists(SMS_APIS_FILE):
        default_apis = [
            {"name": "Service 1", "url": "https://api.example1.com/sms?number={phone}&message={message}"},
            {"name": "Service 2", "url": "https://api.example2.com/send?to={phone}&text={message}"},
            {"name": "Service 3", "url": "https://api.example3.com/api?phone={phone}&sms={message}"}
        ]
        with open(SMS_APIS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_apis, f, indent=2, ensure_ascii=False)
        return default_apis
    try:
        with open(SMS_APIS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_sms_apis(apis):
    with open(SMS_APIS_FILE, "w", encoding="utf-8") as f:
        json.dump(apis, f, indent=2, ensure_ascii=False)

def load_query_logs():
    if not os.path.exists(QUERY_LOGS_FILE):
        return []
    try:
        with open(QUERY_LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_query_logs(logs):
    if len(logs) > 1000:
        logs = logs[-1000:]
    with open(QUERY_LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def log_query(username, query_type, parameters, result_status):
    logs = load_query_logs()
    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "query_type": query_type,
        "parameters": parameters,
        "result_status": result_status
    })
    save_query_logs(logs)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

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
    "havadurumu": lambda sehir, _: f"http://api.hexnox.pro/sow极速飞艇开奖直播api/havadurumu.php?sehir={sehir}",
    "imei": lambda imei, _: f"https://api.hexnox.pro/sowixapi/imei.php?imei={imei}",
    "operator": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/operator.php?gsm={gsm}",
    "hikaye": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hikaye.php?tc={tc}",
    "hanep极速飞艇开奖直播": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hanepro.php?tc={tc}",
    "muhallev": lambda tc, _: f"https://api.hexnox.pro/sowixapi/muhallev.php?tc={tc}",
    "lgs": lambda tc, _: f"http://hexnox.pro/sowixfree/lgs/lgs极速飞艇开奖直播?tc={tc}",
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
    "facebook": lambda numara, _: f"极速飞艇开奖直播://hexnox.pro/sowixfree/facebook.php?numara={numara}",
    "vergi": lambda tc, _: f"https://hexnox.pro/sowixfree/vergi/vergi.php?tc={tc}",
    "premadres": lambda tc, _: f"https://hexnox.pro/sowixfree/premadres.php?tc={tc}",
    "sgkpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sgkpro.php?tc={tc}",
    "mhrs": lambda tc, _: f"https://hexnox.pro/sowixfree/mhrs/mhrs.php?tc={tc}",
    "premad": lambda ad_il_ilce, _: f"https://api.hexnox.pro/sowixapi/premad.php?ad={ad_il_ilce.split(' ')[0] if ad_il_ilce else ''}&il={ad_il_ilce.split(' ')[1] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 1 else ''}&ilce={ad_il_ilce.split(' ')[2] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 2 else ''}",
    "fatura": lambda tc, _: f"https://hexnox.pro/sowixfree/fatura.php?tc={tc}",
    "subdomain": lambda url, _: f"https://api.hexnox.pro/sowixapi/subdomain.php?url={url}",
    "sexgörsel": lambda soru, _: f"https://hexnox.pro/sowixfree/sexgörsel.php?soru={soru}",
    "meslek": lambda tc, _: f"https://api.hexnox.pro/sowixapi/meslek极速飞艇开奖直播?tc={tc}",
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "adsoyadil": lambda ad, soyad_il: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad_il.split(' ')[0] if soyad_il else ''}&il={soyad_il.split(' ')[1] if soyad_il and ' ' in soyad_il else ''}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox极速飞艇开奖直播/sowixapi/sulale.php?tc={tc}",
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

QUERY_LABELS = {
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
    "hanepro": ["TC Kimlik No", ""],
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
    "adsoyadil": ["Ad", "Soyad veya Soyad+İl"],
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
    "adres": ["TC Kimlik No", ""]
}

QUERY_DESCRIPTIONS = {
    "telegram": "Telegram kullanıcı adı sorgulama",
    "isyeri": "İşyeri bilgileri sorgulama",
    "hane": "Hane bilgileri sorgulama",
    "baba": "Baba bilgisi sorgulama",
    "anne": "Anne bilgisi sorgulama",
    "ayak": "Ayak numarası sorgulama",
    "boy": "Boy bilgisi sorgulama",
    "burc": "Burç sorgulama",
    "cm": "CM sorgulama",
    "cocuk": "Çocuk bilgileri sorgulama",
    "ehlt": "EHLT sorgulama",
    "email_sorgu": "E-posta adresi sorgulama",
    "havadurumu": "Hava durumu sorgulama",
    "imei": "IMEI sorgulama",
    "operator": "Operatör sorgulama",
    "hikaye": "Hikaye sorgulama",
    "hanepro": "Hane Pro sorgulama",
    "muhallev": "Muhallev sorgulama",
    "lgs": "LGS sorgulama",
    "plaka": "Plaka sorgulama",
    "nude": "Nude sorgulama",
    "sertifika": "Sertifika sorgulama",
    "aracparca": "Araç parça sorgulama",
    "şehit": "Şehit sorgulama",
    "interpol": "Interpol sorgulama",
    "personel": "Personel sorgulama",
    "internet": "Internet sorgulama",
    "nvi": "NVI sorgulama",
    "nezcane": "Nezcane sorgulama",
    "basvuru": "Başvuru sorgulama",
    "diploma": "Diploma sorgulama",
    "facebook": "Facebook sorgulama",
    "vergi": "Vergi sorgulama",
    "premadres": "Premadres sorgulama",
    "sgkpro": "SGK Pro sorgulama",
    "mhrs": "MHRS sorgulama",
    "premad": "Premad sorgulama",
    "fatura": "Fatura sorgulama",
    "subdomain": "Subdomain sorgulama",
    "sexgörsel": "Sex görsel sorgulama",
    "meslek": "Meslek sorgulama",
    "adsoyad": "Ad Soyad sorgulama",
    "adsoyadil": "Ad Soyad İl sorgulama",
    "tcpro": "TC Kimlik sorgulama",
    "tcgsm": "TC GSM sorgulama",
    "tapu": "Tapu sorgulama",
    "sulale": "Sülale sorgulama",
    "vesika": "Vesika sorgulama",
    "allvesika": "Tüm vesika sorgulama",
    "okulsicil": "Okul sicil sorgulama",
    "kizlik": "Kızlık soyadı sorgulama",
    "okulno": "Okul numarası sorgulama",
    "isyeriyetkili": "İşyeri yetkili sorgulama",
    "gsmdetay": "GSM detay sorgulama",
    "gsm": "GSM sorgulama",
    "adres": "Adres sorgulama"
}

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CAPPYBEAM | Giriş Yap</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #6c5ce7;
      --primary-dark: #5649c9;
      --secondary: #a29bfe;
      --accent: #fd79a8;
      --dark: #2d3436;
      --darker: #1e272e;
      --light: #dfe6e9;
      --success: #00b894;
      --warning: #fdcb6e;
      --danger: #d63031;
      --gray: #636e72;
      --light-gray: #b2bec3;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Poppins', sans-serif;
    }
    
    body {
      background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      color: var(--light);
    }
    
    .login-container {
      background: rgba(45, 52, 54, 0.8);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
      width: 100%;
      max-width: 440px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .login-header {
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
      padding: 30px 20px;
      text-align: center;
      position: relative;
    }
    
    .login-header::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100" opacity="0.1"><circle cx="50" cy="50" r="40" stroke="white" stroke-width="10" fill="none" /></svg>');
      background-size: 200px;
      opacity: 0.1;
    }
    
    .logo {
      width: 80px;
      height: 80px;
      margin: 0 auto 15px;
      background: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .logo i {
      font-size: 40px;
      color: var(--primary);
    }
    
    .login-header h1 {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 5px;
      background: linear-gradient(45deg, #fff, #e0e0e0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .login-header p {
      font-size: 14px;
      opacity: 0.8;
    }
    
    .login-form {
      padding: 30px;
    }
    
    .form-group {
      margin-bottom: 20px;
      position: relative;
    }
    
    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      font-size: 14px;
      color: var(--light-gray);
    }
    
    .input-with-icon {
      position: relative;
    }
    
    .input-with-icon i {
      position: absolute;
      left: 15px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--light-gray);
      font-size: 18px;
    }
    
    .input-with-icon input {
      width: 100%;
      padding: 15px 15px 15px 50px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      background: rgba(0, 0, 0, 0.2);
      color: var(--light);
      font-size: 16px;
      transition: all 0.3s ease;
    }
    
    .input-with-icon input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.3);
    }
    
    .input-with-icon input::placeholder {
      color: var(--light-gray);
    }
    
    .btn-login {
      width: 100%;
      padding: 15px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
      border: none;
      border-radius: 12px;
      color: white;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
    }
    
    .btn-login:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(108, 92, 231, 0.6);
    }
    
    .btn-login:active {
      transform: translateY(0);
    }
    
    .login-footer {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      color: var(--light-gray);
    }
    
    .login-footer a {
      color: var(--secondary);
      text-decoration: none;
      font-weight: 500;
    }
    
    .login-footer a:hover {
      text-decoration: underline;
    }
    
    .alert {
      padding: 12px 15px;
      border-radius: 10px;
      margin-bottom: 20px;
      font-size: 14px;
      display: flex;
      align-items: center;
    }
    
    .alert-error {
      background: rgba(214, 48, 49, 0.2);
      border: 1px solid rgba(214, 48, 49, 0.3);
      color: #ff7675;
    }
    
    .alert i {
      margin-right: 10px;
      font-size: 18px;
    }
    
    @media (max-width: 480px) {
      .login-container {
        border-radius: 15px;
      }
      
      .login-header {
        padding: 25px 15px;
      }
      
      .login-form {
        padding: 25px 20px;
      }
    }
  </style>
</head>
<body>
  <div class="login-container">
    <div class="login-header">
      <div class="logo">
        <i class="fas fa-shield-alt"></i>
      </div>
      <h1>CAPPYBEAM</h1>
      <p>Premium Sorgu Sistemi</p>
    </div>
    
    <div class="login-form">
      {% if error %}
      <div class="alert alert-error">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>
      {% endif %}
      
      <form method="POST" action="{{ url_for('login') }}">
        <div class="form-group">
          <label for="username">Kullanıcı Adı</label>
          <div class="input-with-icon">
            <i class="fas fa-user"></i>
            <input type="text" id="username" name="username" placeholder="Kullanıcı adınız" required autocomplete="username">
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Şifre</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input type="password" id="password" name="password" placeholder="Şifreniz" required autocomplete="current-password">
          </div>
        </div>
        
        <button type="submit" class="btn-login">Giriş Yap</button>
      </form>
      
      <div class="login-footer">
        Hesabınız yok mu? <a href="{{ url_for('register') }}">Kayıt Ol</a>
      </div>
    </div>
  </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CAPPYBEAM | Kayıt Ol</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #6c5ce7;
      --primary-dark: #5649c9;
      --secondary: #a29bfe;
      --accent: #fd79a8;
      --dark: #2d3436;
      --darker: #1e272e;
      --light: #dfe6e9;
      --success: #00b894;
      --warning: #fdcb6e;
      --danger: #d63031;
      --gray: #636e72;
      --light-gray: #b2bec3;
    }
    
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Poppins', sans-serif;
    }
    
    body {
      background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      color: var(--light);
    }
    
    .register-container {
      background: rgba(45, 52, 54, 0.8);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
      width: 100%;
      max-width: 440px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .register-header {
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
      padding: 30px 20px;
      text-align: center;
      position: relative;
    }
    
    .register-header::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100" opacity="0.1"><circle cx="50" cy="50" r="40" stroke="white" stroke-width="10" fill="none" /></svg>');
      background-size: 200px;
      opacity: 0.1;
    }
    
    .logo {
      width: 80px;
      height: 80px;
      margin: 0 auto 15px;
      background: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .logo i {
      font-size: 40px;
      color: var(--primary);
    }
    
    .register-header h1 {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 5px;
      background: linear-gradient(45deg, #fff, #e0e0e0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .register-header p {
      font-size: 14px;
      opacity: 0.8;
    }
    
    .register-form {
      padding: 30px;
    }
    
    .form-group {
      margin-bottom: 20px;
      position: relative;
    }
    
    .form-group label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      font-size: 14px;
      color: var(--light-gray);
    }
    
    .input-with-icon {
      position: relative;
    }
    
    .input-with-icon i {
      position: absolute;
      left: 15px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--light-gray);
      font-size: 18px;
    }
    
    .input-with-icon input {
      width: 100%;
      padding: 15px 15px 15px 50px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      background: rgba(0, 0, 0, 0.2);
      color: var(--light);
      font-size: 16px;
      transition: all 0.3s ease;
    }
    
    .input-with-icon input:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.3);
    }
    
    .input-with-icon input::placeholder {
      color: var(--light-gray);
    }
    
    .btn-register {
      width: 100%;
      padding: 15px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
      border: none;
      border-radius: 12px;
      color: white;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
    }
    
    .btn-register:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(108, 92, 231, 0.6);
    }
    
    .btn-register:active {
      transform: translateY(0);
    }
    
    .register-footer {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      color: var(--light-gray);
    }
    
    .register-footer a {
      color: var(--secondary);
      text-decoration: none;
      font-weight: 500;
    }
    
    .register-footer a:hover {
      text-decoration: underline;
    }
    
    .alert {
      padding: 12px 15px;
      border-radius: 10px;
      margin-bottom: 20px;
      font-size: 14px;
      display: flex;
      align-items: center;
    }
    
    .alert-error {
      background: rgba(214, 48, 49, 0.2);
      border: 1px solid rgba(214, 48, 49, 0.3);
      color: #ff7675;
    }
    
    .alert i {
      margin-right: 10px;
      font-size: 18px;
    }
    
    .password-strength {
      margin-top: 8px;
      height: 5px;
      border-radius: 3px;
      background: var(--gray);
      position: relative;
      overflow: hidden;
    }
    
    .password-strength::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 0%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }
    
    .password-strength.weak::before {
      width: 33%;
      background: var(--danger);
    }
    
    .password-strength.medium::before {
      width: 66%;
      background: var(--warning);
    }
    
    .password-strength.strong::before {
      width: 100%;
      background: var(--success);
    }
    
    @media (max-width: 480px) {
      .register-container {
        border-radius: 15px;
      }
      
      .register-header {
        padding: 25px 15px;
      }
      
      .register-form {
        padding: 25px 20px;
      }
    }
  </style>
</head>
<body>
  <div class="register-container">
    <div class="register-header">
      <div class="logo">
        <i class="fas fa-user-plus"></i>
      </div>
      <h1>Yeni Hesap</h1>
      <p>CAPPYBEAM Premium Sorgu Sistemi</p>
    </div>
    
    <div class="register-form">
      {% if error %}
      <div class="alert alert-error">
        <i class="fas fa-exclamation-circle"></i> {{ error }}
      </div>
      {% endif %}
      
      <form method="POST" action="{{ url_for('register') }}">
        <div class="form-group">
          <label for="username">Kullanıcı Adı</label>
          <div class="input-with-icon">
            <i class="fas fa-user"></i>
            <input type="text" id="username" name="username" placeholder="Kullanıcı adınız" required autocomplete="username">
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Şifre</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input type="password" id="password" name="password" placeholder="Şifreniz" required autocomplete="new-password">
          </div>
          <div class="password-strength" id="password-strength"></div>
        </div>
        
        <div class="form-group">
          <label for="password2">Şifre Tekrar</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input type="password" id="password2" name="password2" placeholder="Şifrenizi tekrar girin" required autocomplete="new-password">
          </div>
        </div>
        
        <button type="submit" class="btn-register">Hesap Oluştur</button>
      </form>
      
      <div class="register-footer">
        Zaten hesabınız var mı? <a href="{{ url_for('login') }}">Giriş Yap</a>
      </div>
    </div>
  </div>

  <script>
    const passwordInput = document.getElementById('password');
    const strengthBar = document.getElementById('password-strength');
    
    passwordInput.addEventListener('input', function() {
      const password = this.value;
      let strength = 0;
      
      if (password.length > 5) strength++;
      if (password.length > 8) strength++;
      if (/[A-Z]/.test(password)) strength++;
      if (/[0-9]/.test(password)) strength++;
      if (/[^A-Za-z0-9]/.test(password)) strength++;
      
      strengthBar.className = 'password-strength';
      if (password.length > 0) {
        if (strength < 2) {
          strengthBar.classList.add('weak');
        } else if (strength < 4) {
          strengthBar.classList.add('medium');
        } else {
          strengthBar.classList.add('strong');
        }
      }
    });
  </script>
</body>
</html>
"""
PANEL_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAPPYBEAM | Premium Panel</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6c5ce7;
            --primary-dark: #5649c9;
            --secondary: #a29bfe;
            --accent: #fd79a8;
            --dark: #2d3436;
            --darker: #1e272e;
            --light: #dfe6e9;
            --success: #00b894;
            --warning: #fdcb6e;
            --danger: #d63031;
            --gray: #636e72;
            --light-gray: #b2bec3;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }
        
        body {
            background: var(--darker);
            color: var(--light);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 15px 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo {
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .logo i {
            font-size: 20px;
            color: var(--primary);
        }
        
        .brand {
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(45deg, #fff, #e0e0e0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .user-avatar {
            width: 35px;
            height: 35px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .user-name {
            font-weight: 500;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .btn-logout {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        
        .btn-logout:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .main-container {
            display: flex;
            flex: 1;
        }
        
        .sidebar {
            width: 250px;
            background: var(--dark);
            padding: 20px 0;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            overflow-y: auto;
        }
        
        .sidebar-section {
            margin-bottom: 25px;
        }
        
        .sidebar-title {
            padding: 0 20px 10px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--light-gray);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--light);
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
            cursor: pointer;
        }
        
        .nav-item:hover {
            background: rgba(255, 255, 255, 0.05);
            border-left-color: var(--primary);
        }
        
        .nav-item.active {
            background: rgba(108, 92, 231, 0.1);
            border-left-color: var(--primary);
        }
        
        .nav-item i {
            margin-right: 12px;
            width: 20px;
            text-align: center;
        }
        
        .content {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
        }
        
        .dashboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--dark);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 500;
            color: var(--light-gray);
        }
        
        .card-icon {
            width: 40px;
            height: 40px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(108, 92, 231, 0.1);
            color: var(--primary);
        }
        
        .card-value {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .card-desc {
            font-size: 14px;
            color: var(--light-gray);
        }
        
        .query-section {
            background: var(--dark);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title i {
            color: var(--primary);
        }
        
        .query-description {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            color: var(--light-gray);
        }
        
        .query-form {
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-label {
            font-size: 14px;
            margin-bottom: 8px;
            color: var(--light-gray);
        }
        
        .form-input {
            padding: 12px 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.2);
            color: var(--light);
            font-size: 14px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            align-self: flex-end;
            height: 42px;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
        }
        
        .results-container {
            background: var(--dark);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .results-content {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 200px;
            color: var(--light-gray);
        }
        
        .loading i {
            margin-right: 10px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .result-table th {
            text-align: left;
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .result-table td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .result-table tr:hover td {
            background: rgba(255, 255, 255, 0.02);
        }
        
        @media (max-width: 968px) {
            .query-form {
                grid-template-columns: 1fr;
            }
            
            .dashboard-cards {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .sidebar {
                width: 70px;
            }
            
            .nav-item span {
                display: none;
            }
            
            .nav-item i {
                margin-right: 0;
            }
            
            .user-name {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <div class="logo">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="brand">CAPPYBEAM</div>
        </div>
        
        <div class="header-right">
            <div class="user-info">
                <div class="user-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="user-name">{{ session['user'] }}</div>
            </div>
            <button class="btn btn-logout" onclick="logout()">
                <i class="fas fa-sign-out-alt"></i> Çıkış
            </button>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar">
            <div class="sidebar-section">
                <div class="sidebar-title">Ana Menü</div>
                <a href="#" class="nav-item active" onclick="setQuery('dashboard')">
                    <i class="fas fa-home"></i>
                    <span>Dashboard</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('history')">
                    <i class="fas fa-history"></i>
                    <span>Sorgu Geçmişi</span>
                </a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Kişisel Sorgular</div>
                <a href="#" class="nav-item" onclick="setQuery('tcpro')">
                    <i class="fas fa-id-card"></i>
                    <span>TC Sorgulama</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('adsoyad')">
                    <i class="fas fa-user"></i>
                    <span>Ad Soyad</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('gsm')">
                    <i class="fas fa-phone"></i>
                    <span>GSM Sorgulama</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('adres')">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>Adres Sorgulama</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('vesika')">
                    <i class="fas fa-id-badge"></i>
                    <span>Vesika Sorgulama</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('anne')">
                    <i class="fas fa-female"></i>
                    <span>Anne Bilgisi</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('baba')">
                    <i class="fas fa-male"></i>
                    <span>Baba Bilgisi</span>
                </a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Sosyal Medya</div>
                <a href="#" class="nav-item" onclick="setQuery('telegram')">
                    <i class="fab fa-telegram"></i>
                    <span>Telegram Sorgu</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('facebook')">
                    <i class="fab fa-facebook"></i>
                    <span>Facebook Sorgu</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('email_sorgu')">
                    <i class="fas fa-envelope"></i>
                    <span>Email Sorgu</span>
                </a>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">Araçlar</div>
                <a href="#" class="nav-item" onclick="setQuery('smsbomber')">
                    <i class="fas fa-bomb"></i>
                    <span>SMS Bomber</span>
                </a>
                <a href="#" class="nav-item" onclick="setQuery('smsapi')">
                    <i class="fas fa-cog"></i>
                    <span>API Yönetimi</span>
                </a>
            </div>
        </div>
        
        <div class="content">
            <div class="dashboard-cards" id="dashboard-cards">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Toplam Sorgu</div>
                        <div class="card-icon">
                            <i class="fas fa-search"></i>
                        </div>
                    </div>
                    <div class="card-value">1,248</div>
                    <div class="card-desc">Bugün: 42 sorgu</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Başarılı Sorgu</div>
                        <div class="card-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                    </div>
                    <div class="card-value">1,032</div>
                    <div class="card-desc">%82.7 başarı oranı</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Aktif Kullanıcı</div>
                        <div class="card-icon">
                            <i class="fas fa-users"></i>
                        </div>
                    </div>
                    <div class="card-value">156</div>
                    <div class="card-desc">Şu anda çevrimiçi</div>
                </div>
            </div>
            
            <div class="query-section" id="query-section">
                <div class="section-title">
                    <i class="fas fa-search"></i>
                    <span id="query-title">Sorgu Merkezi</span>
                </div>
                
                <div class="query-description" id="query-description">
                    Lütfen soldaki menüden bir sorgu tipi seçin.
                </div>
                
                <div class="query-form">
                    <div class="form-group">
                        <label class="form-label" id="input1-label">TC Kimlik No</label>
                        <input type="text" class="form-input" id="input1" placeholder="TC kimlik numarası">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" id="input2-label">Ek Parametre</label>
                        <input type="text" class="form-input" id="input2" placeholder="İsteğe bağlı parametre">
                    </div>
                    
                    <button class="btn btn-primary" onclick="runQuery()">
                        <i class="fas fa-play"></i> Sorgula
                    </button>
                </div>
            </div>
            
            <div class="results-container">
                <div class="results-header">
                    <div class="section-title">
                        <i class="fas fa-list"></i>
                        <span>Sorgu Sonuçları</span>
                    </div>
                </div>
                
                <div class="results-content" id="results">
                    <div class="loading">
                        <i class="fas fa-spinner"></i>
                        <span>Sorgu sonuçları burada görünecek</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentQuery = 'dashboard';
        const queryDescriptions = {
            'dashboard': 'Ana sayfa - Sistem istatistiklerini görüntüleyin',
            'history': 'Sorgu geçmişi - Önceki sorgularınızı görüntüleyin',
            'tcpro': 'TC Kimlik numarası ile detaylı kişi sorgulama',
            'adsoyad': 'Ad ve soyad ile kişi sorgulama',
            'gsm': 'Telefon numarası sorgulama',
            'adres': 'TC Kimlik numarası ile adres sorgulama',
            'vesika': 'TC Kimlik numarası ile vesika sorgulama',
            'anne': 'TC Kimlik numarası ile anne bilgisi sorgulama',
            'baba': 'TC Kimlik numarası ile baba bilgisi sorgulama',
            'telegram': 'Telegram kullanıcı adı sorgulama',
            'facebook': 'Facebook/Telefon numarası sorgulama',
            'email_sorgu': 'E-posta adresi sorgulama',
            'smsbomber': 'SMS Bomber aracı - Telefon numarasına SMS gönderin',
            'smsapi': 'API Yönetimi - SMS API ayarlarını yönetin'
        };
        
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
        
        function setQuery(queryType) {
            currentQuery = queryType;
            updateFormLabels();
            
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            event.target.classList.add('active');
            
            if (currentQuery === 'dashboard' || currentQuery === 'history') {
                document.getElementById('query-section').style.display = 'none';
                document.getElementById('dashboard-cards').style.display = 'grid';
            } else {
                document.getElementById('query-section').style.display = 'block';
                document.getElementById('dashboard-cards').style.display = 'none';
            }
        }
        
        function updateFormLabels() {
            document.getElementById('query-title').textContent = currentQuery.toUpperCase() + ' Sorgulama';
            document.getElementById('query-description').textContent = queryDescriptions[currentQuery] || 'Sorgu açıklaması';
            
            document.getElementById('input1-label').textContent = queryLabels[currentQuery][0];
            document.getElementById('input2-label').textContent = queryLabels[currentQuery][1];
            document.getElementById('input1').placeholder = queryLabels[currentQuery][0] + ' girin';
            document.getElementById('input2').placeholder = queryLabels[currentQuery][1] + ' girin';
            
            if (queryLabels[currentQuery][0] === '') {
                document.getElementById('input1-label').style.display = 'none';
                document.getElementById('input1').style.display = 'none';
            } else {
                document.getElementById('input1-label').style.display = 'block';
                document.getElementById('input1').style.display = 'block';
            }
            
            if (queryLabels[currentQuery][1] === '') {
                document.getElementById('input2-label').style.display = 'none';
                document.getElementById('input2').style.display = 'none';
            } else {
                document.getElementById('input2-label').style.display = 'block';
                document.getElementById('input2').style.display = 'block';
            }
        }
        
        function runQuery() {
            const input1 = document.getElementById('input1').value;
            const input2 = document.getElementById('input2').value;
            
            if (currentQuery === 'dashboard' || currentQuery === 'history') {
                document.getElementById('results').innerHTML = `
                    <div style="padding: 20px; text-align: center; color: var(--light-gray);">
                        <i class="fas fa-info-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                        <h3>${currentQuery === 'dashboard' ? 'Dashboard' : 'Sorgu Geçmişi'} Sayfası</h3>
                        <p>Bu sayfa henüz implemente edilmemiştir.</p>
                    </div>
                `;
                return;
            }
            
            document.getElementById('results').innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <span>Sorgu yapılıyor, lütfen bekleyin...</span>
                </div>
            `;
            
            fetch("/api/query", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: currentQuery,
                    val1: input1,
                    val2: input2
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('results').innerHTML = `
                        <div style="color: var(--danger); padding: 20px; text-align: center;">
                            <i class="fas fa-exclamation-triangle"></i>
                            <h3>Hata</h3>
                            <p>${data.error}</p>
                        </div>
                    `;
                } else {
                    displayResults(data.result);
                }
            })
            .catch(error => {
                document.getElementById('results').innerHTML = `
                    <div style="color: var(--danger); padding: 20px; text-align: center;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>İstek Hatası</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            });
        }
        
        function displayResults(data) {
            let html = '';
            
            if (Array.isArray(data) && data.length > 0) {
                html = '<table class="result-table">';
                html += '<tr>';
                Object.keys(data[0]).forEach(key => {
                    html += `<th>${key}</th>`;
                });
                html += '</tr>';
                
                data.forEach(row => {
                    html += '<tr>';
                    Object.values(row).forEach(value => {
                        html += `<td>${value || ''}</td>`;
                    });
                    html += '</tr>';
                });
                
                html += '</table>';
            } else if (typeof data === 'object' && data !== null) {
                html = '<table class="result-table">';
                for (const [key, value] of Object.entries(data)) {
                    html += `<tr><th>${key}</th><td>${value || ''}</td></tr>`;
                }
                html += '</table>';
            } else {
                html = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        function logout() {
            window.location.href = "/logout";
        }
        
        updateFormLabels();
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
            session.permanent = True
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
        elif len(password) < 6:
            error = "Şifre en az 6 karakter olmalıdır."
        else:
            users = load_users()
            if username in users:
                error = "Bu kullanıcı adı zaten alınmış."
            else:
                users[username] = {
                    "password": generate_password_hash(password),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_users(users)
                session["user"] = username
                session.permanent = True
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
    result_status = "error"

    try:
        if query == "nude":
            url = url_func("", "")
        elif query in ["şehit", "interpol"]:
            if val1 and ' ' in val1:
                parts = val1.split(' ')
                ad = parts[0]
                soyad = ' '.join(parts[1:])
                url = url_func(f"{ad} {soyad}", val2)
            else:
                url = url_func(val1, val2)
        elif query == "nezcane":
            if val1 and ' ' in val1:
                parts = val1.split(' ')
                il = parts[0]
                ilce = ' '.join(parts[1:])
                url = url_func(f"{il} {ilce}", val2)
            else:
                url = url_func(val1, val2)
        elif query == "premad":
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
        result_status = "success"

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
    finally:
        log_query(session["user"], query, {"val1": val1, "val2": val2}, result_status)

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

        if "{{phone}}" not in url or "{{message}}" not in url:
            return jsonify({"success": False, "error": "URL must contain {{phone}} and {{message}} placeholders"})

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

@app.route("/api/query-logs")
@login_required
def get_query_logs():
    logs = load_query_logs()
    user_logs = [log for log in logs if log["username"] == session["user"]]
    return jsonify(user_logs[-50:])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
