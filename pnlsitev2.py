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
import urllib3

# SSL uyarılarını kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
app.secret_key = "cappybeam_premium_secret_key_2023"
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

USERS_FILE = "users.json"
SMS_APIS_FILE = "sms_apis.json"
QUERY_LOGS_FILE = "query_logs.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        # Varsayılan admin kullanıcısı oluştur
        default_users = {
            "admin": {
                "password": generate_password_hash("admin123"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        save_users(default_users)
        return default_users
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

# Güncellenmiş API URL'leri - API sahibi bilgileri gizlendi
API_URLS = {
    "telegram": lambda username, _: f"https://api.hexnox.pro/sowixapi/telegram_sorgu.php?username={username}",
    "isyeri": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeri.php?tc={tc}",
    "hane": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hane.php?tc={tc}",
    "baba": lambda tc, _: f"https://api.hexnox.pro/sowixapi/baba.php?tc={tc}",
    "anne": lambda tc, _: f"https://api.hexnox.pro/sowixapi/anne.php?tc={tc}",
    "ayak": lambda tc, _: f"https://api.hexnox.pro/sowixapi/ayak.php?tc={tc}",
    "boy": lambda tc, _: f"https://api.hexnox.pro/sowixapi/boy.php?tc={tc}",
    "burc": lambda tc, _: f"https://api.hexnox.pro/sowixapi/burc.php?tc={tc}",
    "cm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/cm.php?tc={tc}",
    "cocuk": lambda tc, _: f"https://api.hexnox.pro/sowixapi/cocuk.php?tc={tc}",
    "ehlt": lambda tc, _: f"https://api.hexnox.pro/sowixapi/ehlt.php?tc={tc}",
    "email_sorgu": lambda email, _: f"https://api.hexnox.pro/sowixapi/email_sorgu.php?email={email}",
    "havadurumu": lambda sehir, _: f"https://api.hexnox.pro/sowixapi/havadurumu.php?sehir={sehir}",
    "imei": lambda imei, _: f"https://api.hexnox.pro/sowixapi/imei.php?imei={imei}",
    "operator": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/operator.php?gsm={gsm}",
    "hikaye": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hikaye.php?tc={tc}",
    "hanepro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/hanepro.php?tc={tc}",
    "muhallev": lambda tc, _: f"https://api.hexnox.pro/sowixapi/muhallev.php?tc={tc}",
    "lgs": lambda tc, _: f"https://api.hexnox.pro/sowixapi/lgs.php?tc={tc}",
    "plaka": lambda plaka, _: f"https://api.hexnox.pro/sowixapi/plaka.php?plaka={plaka}",
    "nude": lambda _, __: f"https://api.hexnox.pro/sowixapi/nude.php",
    "sertifika": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sertifika.php?tc={tc}",
    "aracparca": lambda plaka, _: f"https://api.hexnox.pro/sowixapi/aracparca.php?plaka={plaka}",
    "şehit": lambda ad_soyad, _: f"https://api.hexnox.pro/sowixapi/şehit.php?Ad={ad_soyad.split(' ')[0] if ad_soyad else ''}&Soyad={ad_soyad.split(' ')[1] if ad_soyad and ' ' in ad_soyad else ''}",
    "interpol": lambda ad_soyad, _: f"https://api.hexnox.pro/sowixapi/interpol.php?ad={ad_soyad.split(' ')[0] if ad_soyad else ''}&soyad={ad_soyad.split(' ')[1] if ad_soyad and ' ' in ad_soyad else ''}",
    "personel": lambda tc, _: f"https://api.hexnox.pro/sowixapi/personel.php?tc={tc}",
    "internet": lambda tc, _: f"https://api.hexnox.pro/sowixapi/internet.php?tc={tc}",
    "nvi": lambda tc, _: f"https://api.hexnox.pro/sowixapi/nvi.php?tc={tc}",
    "nezcane": lambda il_ilce, _: f"https://api.hexnox.pro/sowixapi/nezcane.php?il={il_ilce.split(' ')[0] if il_ilce else ''}&ilce={il_ilce.split(' ')[1] if il_ilce and ' ' in il_ilce else ''}",
    "basvuru": lambda tc, _: f"https://api.hexnox.pro/sowixapi/basvuru.php?tc={tc}",
    "diploma": lambda tc, _: f"https://api.hexnox.pro/sowixapi/diploma.php?tc={tc}",
    "facebook": lambda numara, _: f"https://api.hexnox.pro/sowixapi/facebook.php?numara={numara}",
    "vergi": lambda tc, _: f"https://api.hexnox.pro/sowixapi/vergi.php?tc={tc}",
    "premadres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/premadres.php?tc={tc}",
    "sgkpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sgkpro.php?tc={tc}",
    "mhrs": lambda tc, _: f"https://api.hexnox.pro/sowixapi/mhrs.php?tc={tc}",
    "premad": lambda ad_il_ilce, _: f"https://api.hexnox.pro/sowixapi/premad.php?ad={ad_il_ilce.split(' ')[0] if ad_il_ilce else ''}&il={ad_il_ilce.split(' ')[1] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 1 else ''}&ilce={ad_il_ilce.split(' ')[2] if ad_il_ilce and len(ad_il_ilce.split(' ')) > 2 else ''}",
    "fatura": lambda tc, _: f"https://api.hexnox.pro/sowixapi/fatura.php?tc={tc}",
    "subdomain": lambda url, _: f"https://api.hexnox.pro/sowixapi/subdomain.php?url={url}",
    "sexgörsel": lambda soru, _: f"https://api.hexnox.pro/sowixapi/sexgörsel.php?soru={soru}",
    "meslek": lambda tc, _: f"https://api.hexnox.pro/sowixapi/meslek.php?tc={tc}",
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "adsoyadil": lambda ad, soyad_il: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad_il.split(' ')[0] if soyad_il else ''}&il={soyad_il.split(' ')[1] if soyad_il and ' ' in soyad_il else ''}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sulale.php?tc={tc}",
    "vesika": lambda tc, _: f"https://api.hexnox.pro/sowixapi/vesika.php?tc={tc}",
    "allvesika": lambda tc, _: f"https://api.hexnox.pro/sowixapi/allvesika.php?tc={tc}",
    "okulsicil": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulsicil.php?tc={tc}",
    "kizlik": lambda tc, _: f"https://api.hexnox.pro/sowixapi/kizlik.php?tc={tc}",
    "okulno": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulno.php?tc={tc}",
    "isyeriyetkili": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={tc}",
    "gsmdetay": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={gsm}",
    "gsm": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsm.php?gsm={gsm}",
    "adres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/adres.php?tc={tc}",
    "insta": lambda username, _: f"https://api.hexnox.pro/sowixapi/insta.php?usr={username}",
    "facebook_hanedan": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/facebook_hanedan.php?ad={ad}&soyad={soyad}",
    "uni": lambda tc, _: f"https://api.hexnox.pro/sowixapi/uni.php?tc={tc}",
    "akp": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/akp.php?ad={ad}&soyad={soyad}",
    "aifoto": lambda img_url, _: f"https://api.hexnox.pro/sowixapi/aifoto.php?img={img_url}",
    "papara": lambda numara, _: f"https://api.hexnox.pro/sowixapi/papara.php?paparano={numara}",
    "ininal": lambda numara, _: f"https://api.hexnox.pro/sowixapi/ininal.php?ininal_no={numara}",
    "smsbomber": lambda number, _: f"https://api.hexnox.pro/sowixapi/smsbomber.php?number={number}",
    "discord": lambda _, __: "https://discord.gg/cngzsvsaX2",
    "turknet": lambda tc, _: f"https://api.hexnox.pro/sowixapi/turknet.php?tc={tc}"
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
    "adres": ["TC Kimlik No", ""],
    "insta": ["kullanıcı adı", ""],
                "facebook_hanedan": ["ad", "soyad"],
            "uni": ["TC Kimlik No", ""],
            "aifoto": ["img url", ""],
            "papara": ["papara no", ""],
            "ininal": ["ininal no", ""],
            "smsbomber": ["numara", ""],
            "discord": ["", ""],
            "turknet": ["TC Kimlik No", ""]
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
    "adres": "Adres sorgulama",
    "insta": "Instagram kullanıcı adı sorgulama",
    "facebook_hanedan": "Ad ve soyad ile Facebook hanedan sorgulama",
    "uni": "Üniversite sorgulama",
    "akp": "Ad ve soyad ile AKP sorgulama",
    "aifoto": "Resim URL'si ile yapay zeka fotoğraf sorgulama",
    "papara": "Papara numarası ile sorgulama",
    "ininal": "İninal kart numarası ile sorgulama",
    "turknet": "TurkNet sorgulama",
    "smsbomber": "SMS Bomber aracı - Telefon numarasına SMS gönderin",
    "discord": "Discord sunucu bilgileri"
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
    <title>CAPPYBEAMSERVİCES | Premium Sorgu Paneli</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6c5ce7;
            --primary-dark: #5649c9;
            --primary-light: #7d70e9;
            --secondary: #a29bfe;
            --accent: #fd79a8;
            --dark: #2d3436;
            --darker: #1e272e;
            --light: #dfe6e9;
            --lighter: #f5f6fa;
            --success: #00b894;
            --warning: #fdcb6e;
            --danger: #d63031;
            --info: #0984e3;
            --gray: #636e72;
            --light-gray: #b2bec3;
            --sidebar-width: 280px;
            --header-height: 70px;
            --border-radius: 12px;
            --transition: all 0.3s ease;
            --shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            --card-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker) 0%, var(--dark) 100%);
            color: var(--light);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }
        
        /* Header Styles */
        .header {
            background: rgba(45, 52, 54, 0.95);
            backdrop-filter: blur(20px);
            padding: 0 30px;
            height: var(--header-height);
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
            transition: all 0.3s ease;
        }
        
        .logo:hover {
            transform: scale(1.1) rotate(5deg);
            box-shadow: 0 12px 35px rgba(108, 92, 231, 0.5);
        }
        
        .logo i {
            font-size: 22px;
            color: white;
        }
        
        .brand {
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(45deg, var(--light), var(--lighter));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.8px;
            text-shadow: 0 2px 10px rgba(108, 92, 231, 0.3);
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 30px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .user-info:hover {
            background: rgba(255, 255, 255, 0.12);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            border-color: rgba(108, 92, 231, 0.3);
        }
        
        .user-avatar {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.4);
            transition: all 0.3s ease;
        }
        
        .user-avatar:hover {
            transform: scale(1.1);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.5);
        }
        
        .user-avatar i {
            font-size: 20px;
            color: white;
        }
        
        .user-name {
            font-weight: 600;
            font-size: 16px;
            color: var(--light);
        }
        
        .btn {
            padding: 10px 18px;
            border-radius: 30px;
            border: none;
            cursor: pointer;
            font-weight: 500;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        .btn-logout {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .btn-logout:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Main Container */
        .main-container {
            display: flex;
            flex: 1;
            margin-top: var(--header-height);
        }
        
        /* Sidebar Styles */
        .sidebar {
            width: var(--sidebar-width);
            background: rgba(45, 52, 54, 0.8);
            backdrop-filter: blur(10px);
            padding: 25px 0;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            overflow-y: auto;
            height: calc(100vh - var(--header-height));
            position: fixed;
            left: 0;
            top: var(--header-height);
            z-index: 900;
            transition: var(--transition);
        }
        
        .sidebar-section {
            margin-bottom: 30px;
        }
        
        .sidebar-title {
            padding: 0 25px 12px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--light-gray);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .sidebar-title i {
            font-size: 14px;
        }
        
        .nav-items {
            padding: 10px 15px;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--light);
            text-decoration: none;
            transition: var(--transition);
            border-left: 3px solid transparent;
            cursor: pointer;
            border-radius: 8px;
            margin-bottom: 5px;
            font-size: 14.5px;
            animation: slideInLeft 0.4s ease-out;
            animation-delay: 0.1s;
        }
        
        .nav-item:hover {
            background: rgba(108, 92, 231, 0.1);
            border-left-color: var(--primary);
            transform: translateX(5px);
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.15) 0%, rgba(86, 73, 201, 0.15) 100%);
            border-left-color: var(--primary);
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.1);
        }
        
        .nav-item i {
            margin-right: 15px;
            width: 20px;
            text-align: center;
            font-size: 16px;
        }
        
        /* Content Area */
        .content {
            flex: 1;
            padding: 30px;
            margin-left: var(--sidebar-width);
            transition: var(--transition);
        }
        
        /* Dashboard Cards */
        .dashboard-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 35px;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .card {
            background: rgba(45, 52, 54, 0.6);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            padding: 25px;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: var(--transition);
            animation: fadeInUp 0.6s ease-out;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 500;
            color: var(--light-gray);
        }
        
        .card-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(108, 92, 231, 0.1);
            color: var(--primary);
            font-size: 22px;
        }
        
        .card-value {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
            background: linear-gradient(45deg, var(--light), var(--lighter));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .card-desc {
            font-size: 14px;
            color: var(--light-gray);
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .card-desc i {
            color: var(--success);
        }
        
        /* Query Section */
        .query-section {
            background: rgba(45, 52, 54, 0.6);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--card-shadow);
            margin-bottom: 35px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            animation: fadeInUp 0.8s ease-out;
        }
        
        .section-title {
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--light);
        }
        
        .section-title i {
            color: var(--primary);
            font-size: 26px;
        }
        
        .query-description {
            background: rgba(0, 0, 0, 0.15);
            padding: 18px 20px;
            border-radius: var(--border-radius);
            margin-bottom: 25px;
            font-size: 15px;
            color: var(--light-gray);
            line-height: 1.6;
            border-left: 4px solid var(--primary);
        }
        
        .query-form {
            display: grid;
            grid-template-columns: 1fr 1fr auto;
            gap: 25px;
            margin-bottom: 30px;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
            position: relative;
        }
        
        .form-label {
            font-size: 15px;
            margin-bottom: 12px;
            color: var(--light-gray);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: color 0.3s ease;
        }
        
        .form-label i {
            color: var(--primary);
            font-size: 18px;
            transition: all 0.3s ease;
        }
        
        .form-group:focus-within .form-label {
            color: var(--primary);
        }
        
        .form-group:focus-within .form-label i {
            transform: scale(1.1);
        }
        
        .form-input {
            padding: 15px 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: var(--border-radius);
            background: rgba(0, 0, 0, 0.15);
            color: var(--light);
            font-size: 15px;
            transition: var(--transition);
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2);
        }
        
        .form-input::placeholder {
            color: var(--light-gray);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            align-self: flex-end;
            height: 52px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(108, 92, 231, 0.4);
        }
        
        /* Results Container */
        .results-container {
            background: rgba(45, 52, 54, 0.6);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--card-shadow);
            margin-bottom: 35px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            animation: fadeInUp 1s ease-out;
        }
        
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(108, 92, 231, 0.2);
        }
        
        .results-content {
            background: rgba(0, 0, 0, 0.2);
            border-radius: var(--border-radius);
            padding: 30px;
            min-height: 250px;
            max-height: 600px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 250px;
            color: var(--light-gray);
            flex-direction: column;
            gap: 20px;
            animation: fadeInUp 0.5s ease-out;
        }
        
        .loading i {
            font-size: 50px;
            color: var(--primary);
            animation: pulse 2s infinite;
        }
        
        .loading span {
            font-size: 16px;
            color: var(--light);
            font-weight: 500;
        }
        
        .result-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(0, 0, 0, 0.15);
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            margin: 20px 0;
        }
        
        .result-table th {
            text-align: left;
            padding: 18px 20px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            font-size: 14px;
            letter-spacing: 0.5px;
        }
        
        .result-table td {
            padding: 18px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            word-wrap: break-word;
            max-width: 350px;
            vertical-align: top;
            line-height: 1.6;
            color: var(--light);
        }
        
        .result-table tr:last-child td {
            border-bottom: none;
        }
        
        .result-table tr:hover td {
            background: rgba(255, 255, 255, 0.05);
            transform: translateX(5px);
            transition: all 0.3s ease;
        }
        
        .result-table tr:nth-child(even) {
            background: rgba(0, 0, 0, 0.05);
        }
        
        .result-table tr:nth-child(even):hover td {
            background: rgba(255, 255, 255, 0.08);
        }
        
        .result-table .key-column {
            font-weight: 600;
            color: var(--primary-light);
            background: rgba(0, 0, 0, 0.1);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .result-table .value-column {
            color: var(--light);
        }
        
        .result-header {
            margin: 20px 0 15px 0;
            text-align: center;
        }
        
        .result-header h3 {
            color: var(--primary-light);
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .result-table thead th {
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .result-table tbody tr.even {
            background: rgba(0, 0, 0, 0.05);
        }
        
        .result-table tbody tr.odd {
            background: transparent;
        }
        
        /* Yeni bölüm stilleri */
        .result-section {
            background: rgba(0, 0, 0, 0.1);
            border-radius: var(--border-radius);
            padding: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .category-section {
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid var(--primary);
        }
        
        .category-section h5 {
            margin: 0 0 15px 0;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .category-section:last-child {
            margin-bottom: 0;
        }
        
        /* Bölüm başlıkları için özel stiller */
        .result-section h4 {
            border-bottom: 2px solid var(--primary);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        /* Responsive Design */
        @media (max-width: 1200px) {
            .query-form {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 968px) {
            .dashboard-cards {
                grid-template-columns: 1fr 1fr;
            }
            
            .sidebar {
                transform: translateX(-100%);
                width: 260px;
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .content {
                margin-left: 0;
            }
            
            .menu-toggle {
                display: block;
            }
        }
        
        @media (max-width: 768px) {
            .dashboard-cards {
                grid-template-columns: 1fr;
            }
            
            .header {
                padding: 0 15px;
            }
            
            .brand {
                font-size: 20px;
            }
            
            .user-name {
                display: none;
            }
            
            .content {
                padding: 20px 15px;
            }
        }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-dark);
        }
        
        /* Menu Toggle Button */
        .menu-toggle {
            display: none;
            background: none;
            border: none;
            color: var(--light);
            font-size: 24px;
            cursor: pointer;
            margin-right: 15px;
        }
        
        /* Search Bar */
        .search-container {
            position: relative;
            margin-bottom: 25px;
        }
        
        .search-input {
            width: 100%;
            padding: 15px 20px 15px 50px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            background: rgba(0, 0, 0, 0.15);
            color: var(--light);
            font-size: 15px;
            transition: var(--transition);
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2);
        }
        
        .search-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-gray);
        }
        
        /* Additional Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0% { 
                opacity: 0.6; 
                transform: scale(0.95) rotate(0deg); 
            }
            50% { 
                opacity: 1; 
                transform: scale(1.05) rotate(180deg); 
            }
            100% { 
                opacity: 0.6; 
                transform: scale(0.95) rotate(360deg); 
            }
        }
        
        /* Enhanced Button Styles */
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            align-self: flex-end;
            height: 52px;
            font-size: 16px;
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
            border: 2px solid transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .btn-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .btn-primary:hover::before {
            left: 100%;
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4);
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .btn-primary:active {
            transform: translateY(-1px);
        }
        
        /* Enhanced Navigation Items */
        .nav-item {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            color: var(--light);
            text-decoration: none;
            transition: all 0.3s ease;
            border-left: 3px solid transparent;
            cursor: pointer;
            border-radius: 12px;
            margin-bottom: 8px;
            font-size: 14.5px;
            position: relative;
            overflow: hidden;
            animation: slideInLeft 0.4s ease-out;
        }
        
        .nav-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.1), rgba(86, 73, 201, 0.1));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .nav-item:hover::before {
            opacity: 1;
        }
        
        .nav-item:hover {
            background: rgba(108, 92, 231, 0.1);
            border-left-color: var(--primary);
            transform: translateX(8px);
            box-shadow: 0 5px 15px rgba(108, 92, 231, 0.2);
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.2) 0%, rgba(86, 73, 201, 0.2) 100%);
            border-left-color: var(--primary);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.25);
            transform: translateX(5px);
        }
        
        .nav-item.active::before {
            opacity: 1;
        }
        
        .nav-item i {
            margin-right: 15px;
            width: 20px;
            text-align: center;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .nav-item:hover i {
            transform: scale(1.1);
            color: var(--primary);
        }
        
        /* Enhanced Card Styling */
        .card {
            background: rgba(45, 52, 54, 0.6);
            backdrop-filter: blur(15px);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.05), rgba(86, 73, 201, 0.05));
            opacity: 0;
            transition: opacity 0.4s ease;
        }
        
        .card:hover::before {
            opacity: 1;
        }
        
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(108, 92, 231, 0.2);
        }
        
        /* Enhanced Form Styling */
        .form-input {
            padding: 18px 22px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: var(--border-radius);
            background: rgba(0, 0, 0, 0.2);
            color: var(--light);
            font-size: 15px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.2);
            background: rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }
        
        .form-input::placeholder {
            color: var(--light-gray);
            transition: color 0.3s ease;
        }
        
        .form-input:focus::placeholder {
            color: var(--primary);
        }
        
        /* Enhanced Table Styling */
        .result-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(0, 0, 0, 0.15);
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
            margin: 25px 0;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .result-table th {
            text-align: left;
            padding: 20px 22px;
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            font-size: 14px;
            letter-spacing: 0.8px;
            position: sticky;
            top: 0;
            z-index: 10;
            backdrop-filter: blur(10px);
        }
        
        .result-table td {
            padding: 20px 22px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            word-wrap: break-word;
            max-width: 350px;
            vertical-align: top;
            line-height: 1.6;
            color: var(--light);
            transition: all 0.3s ease;
        }
        
        .result-table tr:hover td {
            background: rgba(108, 92, 231, 0.1);
            transform: translateX(5px);
            box-shadow: 0 2px 10px rgba(108, 92, 231, 0.2);
        }
        
        .result-table tr:nth-child(even) {
            background: rgba(0, 0, 0, 0.08);
        }
        
        .result-table tr:nth-child(even):hover td {
            background: rgba(108, 92, 231, 0.15);
        }
        
        /* Enhanced Category Sections */
        .category-section {
            margin-bottom: 25px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--primary);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .category-section:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            border-color: rgba(108, 92, 231, 0.3);
        }
        
        .category-section h5 {
            margin: 0 0 18px 0;
            font-size: 16px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--primary);
        }
        
        /* Enhanced Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            border-radius: 10px;
            border: 2px solid rgba(0, 0, 0, 0.1);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, var(--primary-dark), var(--primary));
        }
        
        /* Enhanced Search */
        .search-input {
            width: 100%;
            padding: 18px 22px 18px 55px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 30px;
            background: rgba(0, 0, 0, 0.2);
            color: var(--light);
            font-size: 15px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.2);
            background: rgba(0, 0, 0, 0.3);
            transform: translateY(-2px);
        }
        
        .search-icon {
            position: absolute;
            left: 22px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-gray);
            transition: color 0.3s ease;
        }
        
        .search-input:focus + .search-icon {
            color: var(--primary);
        }
        
        /* Enhanced Sidebar */
        .sidebar {
            width: var(--sidebar-width);
            background: rgba(45, 52, 54, 0.9);
            backdrop-filter: blur(20px);
            padding: 30px 0;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            overflow-y: auto;
            height: calc(100vh - var(--header-height));
            position: fixed;
            left: 0;
            top: var(--header-height);
            z-index: 900;
            transition: all 0.4s ease;
        }
        
        /* Animation Delays for Nav Items */
        .nav-item:nth-child(1) { animation-delay: 0.1s; }
        .nav-item:nth-child(2) { animation-delay: 0.2s; }
        .nav-item:nth-child(3) { animation-delay: 0.3s; }
        .nav-item:nth-child(4) { animation-delay: 0.4s; }
        .nav-item:nth-child(5) { animation-delay: 0.5s; }
        .nav-item:nth-child(6) { animation-delay: 0.6s; }
        .nav-item:nth-child(7) { animation-delay: 0.7s; }
        .nav-item:nth-child(8) { animation-delay: 0.8s; }
        .nav-item:nth-child(5) { animation-delay: 0.9s; }
        .nav-item:nth-child(10) { animation-delay: 1.0s; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <button class="menu-toggle" id="menuToggle">
                <i class="fas fa-bars"></i>
            </button>
            <div class="logo">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="brand">CAPPYBEAMSERVİCES</div>
        </div>
        
        <div class="header-right">
            <div class="user-info">
                <div class="user-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="user-name">{{ session['user'] }}</div>
            </div>
            <button class="btn btn-logout" data-action="logout">
                <i class="fas fa-sign-out-alt"></i> Çıkış
            </button>
        </div>
    </div>
    
    <div class="main-container">
        <div class="sidebar" id="sidebar">
            <div class="search-container">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" id="menuSearch" placeholder="Menüde ara..." onkeyup="filterMenu()">
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">
                    <i class="fas fa-home"></i>
                    Ana Menü
                </div>
                <div class="nav-items">
                    <a href="#" class="nav-item active" data-query="dashboard">
                        <i class="fas fa-home"></i>
                        <span>Dashboard</span>
                    </a>
                    <a href="#" class="nav-item" data-query="history">
                        <i class="fas fa-history"></i>
                        <span>Sorgu Geçmişi</span>
                    </a>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">
                    <i class="fas fa-id-card"></i>
                    Kişisel Sorgular
                </div>
                <div class="nav-items">
                    <a href="#" class="nav-item" data-query="tcpro">
                        <i class="fas fa-id-card"></i>
                        <span>TC Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="adsoyad">
                        <i class="fas fa-user"></i>
                        <span>Ad Soyad</span>
                    </a>
                    <a href="#" class="nav-item" data-query="gsm">
                        <i class="fas fa-phone"></i>
                        <span>GSM Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="adres">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>Adres Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="vesika">
                        <i class="fas fa-id-badge"></i>
                        <span>Vesika Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="allvesika">
                        <i class="fas fa-id-card-alt"></i>
                        <span>Tüm Vesika Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="anne">
                        <i class="fas fa-female"></i>
                        <span>Anne Bilgisi</span>
                    </a>
                    <a href="#" class="nav-item" data-query="baba">
                        <i class="fas fa-male"></i>
                        <span>Baba Bilgisi</span>
                    </a>
                    <a href="#" class="nav-item" data-query="hane">
                        <i class="fas fa-house-user"></i>
                        <span>Hane Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="sulale">
                        <i class="fas fa-sitemap"></i>
                        <span>Sülale Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="cocuk">
                        <i class="fas fa-child"></i>
                        <span>Çocuk Bilgileri</span>
                    </a>
                    <a href="#" class="nav-item" data-query="isyeri">
                        <i class="fas fa-building"></i>
                        <span>İşyeri Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="isyeriyetkili">
                        <i class="fas fa-user-tie"></i>
                        <span>İşyeri Yetkili</span>
                    </a>
                    <a href="#" class="nav-item" data-query="tapu">
                        <i class="fas fa-home"></i>
                        <span>Tapu Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="sgkpro">
                        <i class="fas fa-file-medical"></i>
                        <span>SGK Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="vergi">
                        <i class="fas fa-receipt"></i>
                        <span>Vergi Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="premadres">
                        <i class="fas fa-address-card"></i>
                        <span>Premadres Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="premad">
                        <i class="fas fa-address-book"></i>
                        <span>Premad Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="nvi">
                        <i class="fas fa-landmark"></i>
                        <span>NVI Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="muhallev">
                        <i class="fas fa-file-contract"></i>
                        <span>Muhallev Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="hanepro">
                        <i class="fas fa-house-damage"></i>
                        <span>Hane Pro Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="ehlt">
                        <i class="fas fa-users"></i>
                        <span>EHLT Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="ayak">
                        <i class="fas fa-shoe-prints"></i>
                        <span>Ayak No Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="boy">
                        <i class="fas fa-ruler-vertical"></i>
                        <span>Boy Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="burc">
                        <i class="fas fa-star"></i>
                        <span>Burç Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="cm">
                        <i class="fas fa-ruler"></i>
                        <span>CM Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="meslek">
                        <i class="fas fa-briefcase"></i>
                        <span>Meslek Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="tcgsm">
                        <i class="fas fa-phone-alt"></i>
                        <span>TC GSM Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="adsoyadil">
                        <i class="fas fa-user-plus"></i>
                        <span>Ad Soyad İl Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="personel">
                        <i class="fas fa-user-md"></i>
                        <span>Personel Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="internet">
                        <i class="fas fa-wifi"></i>
                        <span>Internet Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="fatura">
                        <i class="fas fa-file-invoice-dollar"></i>
                        <span>Fatura Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="mhrs">
                        <i class="fas fa-hospital"></i>
                        <span>MHRS Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="basvuru">
                        <i class="fas fa-file-signature"></i>
                        <span>Başvuru Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="diploma">
                        <i class="fas fa-graduation-cap"></i>
                        <span>Diploma Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="okulno">
                        <i class="fas fa-school"></i>
                        <span>Okul No Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="okulsicil">
                        <i class="fas fa-user-graduate"></i>
                        <span>Okul Sicil Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="lgs">
                        <i class="fas fa-book"></i>
                        <span>LGS Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="sertifika">
                        <i class="fas fa-certificate"></i>
                        <span>Sertifika Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="kizlik">
                        <i class="fas fa-female"></i>
                        <span>Kızlık Soyadı</span>
                    </a>
                    <a href="#" class="nav-item" data-query="hikaye">
                        <i class="fas fa-book-open"></i>
                        <span>Hikaye Sorgulama</span>
                    </a>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">
                    <i class="fas fa-share-alt"></i>
                    Sosyal Medya
                </div>
                <div class="nav-items">
                    <a href="#" class="nav-item" data-query="telegram">
                        <i class="fab fa-telegram"></i>
                        <span>Telegram Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="facebook">
                        <i class="fab fa-facebook"></i>
                        <span>Facebook Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="email_sorgu">
                        <i class="fas fa-envelope"></i>
                        <span>Email Sorgu</span>
                    </a>
                </div>
            </div>
            
            <div class="sidebar-section">
                <div class="sidebar-title">
                    <i class="fas fa-car"></i>
                    Araç & Araç Bilgileri
                </div>
                <div class="nav-items">
                    <a href="#" class="nav-item" data-query="plaka">
                        <i class="fas fa-car"></i>
                        <span>Plaka Sorgulama</span>
                    </a>
                    <a href="#" class="nav-item" data-query="aracparca">
                        <i class="fas fa-tools"></i>
                        <span>Araç Parça Sorgu</span>
                    </a>
                    <a href="#" class="nav-item" data-query="imei">
                        <i class="fas fa-mobile-alt"></i>
                        <span>IMEI Sorgulama</span>
                    </a>
                </div>
            </div>
            
            <div class="sidebar-section">
    <div class="sidebar-title">
        <i class="fas fa-ellipsis-h"></i>
        Diğer Sorgular
    </div>
    <div class="nav-items">
        <a href="#" class="nav-item" data-query="operator">
            <i class="fas fa-sim-card"></i>
            <span>Operatör Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="gsmdetay">
            <i class="fas fa-phone-square"></i>
            <span>GSM Detay Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="havadurumu">
            <i class="fas fa-cloud-sun"></i>
            <span>Hava Durumu</span>
        </a>
        <a href="#" class="nav-item" data-query="subdomain">
            <i class="fas fa-globe"></i>
            <span>Subdomain Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="nezcane">
            <i class="fas fa-map-marked-alt"></i>
            <span>Nezcane Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="şehit">
            <i class="fas fa-medal"></i>
            <span>Şehit Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="interpol">
            <i class="fas fa-globe-americas"></i>
            <span>Interpol Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="sexgörsel">
            <i class="fas fa-image"></i>
            <span>Sex Görsel Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="nude">
            <i class="fas fa-ban"></i>
            <span>Nude Sorgulama</span>
        </a>
        <!-- Yeni eklenenler -->
        <a href="#" class="nav-item" data-query="insta">
            <i class="fab fa-instagram"></i>
            <span>Instagram Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="facebook_hanedan">
            <i class="fab fa-facebook"></i>
            <span>Facebook Hanedan</span>
        </a>
        <a href="#" class="nav-item" data-query="uni">
            <i class="fas fa-university"></i>
            <span>Üniversite Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="akp">
            <i class="fas fa-landmark"></i>
            <span>AKP Sorgulama</span>
        </a>
        <a href="#" class="nav-item" data-query="aifoto">
            <i class="fas fa-robot"></i>
            <span>AI Foto</span>
        </a>
        <a href="#" class="nav-item" data-query="papara">
            <i class="fas fa-wallet"></i>
            <span>Papara Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="ininal">
            <i class="fas fa-credit-card"></i>
            <span>İninal Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="turknet">
            <i class="fas fa-wifi"></i>
            <span>TurkNet Sorgu</span>
        </a>
        <a href="#" class="nav-item" data-query="discord">
            <i class="fab fa-discord"></i>
            <span>Discord Sunucu</span>
        </a>
    </div>
</div>

            
            <div class="sidebar-section">
                <div class="sidebar-title">
                    <i class="fas fa-tools"></i>
                    Araçlar
                </div>
                <div class="nav-items">
                    <a href="#" class="nav-item" data-query="smsbomber">
                        <i class="fas fa-bomb"></i>
                        <span>SMS Bomber</span>
                    </a>
                    <a href="#" class="nav-item" data-query="smsapi">
                        <i class="fas fa-cog"></i>
                        <span>API Yönetimi</span>
                    </a>
                </div>
            </div>
        </div>
        
        <div class="content" id="content">
            <div class="dashboard-cards" id="dashboard-cards">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Toplam Sorgu</div>
                        <div class="card-icon">
                            <i class="fas fa-search"></i>
                        </div>
                    </div>
                    <div class="card-value">1,248</div>
                    <div class="card-desc">
                        <i class="fas fa-arrow-up"></i>
                        Bugün: 42 sorgu
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Başarılı Sorgu</div>
                        <div class="card-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                    </div>
                    <div class="card-value">1,032</div>
                    <div class="card-desc">
                        <i class="fas fa-chart-line"></i>
                        %82.7 başarı oranı
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Aktif Kullanıcı</div>
                        <div class="card-icon">
                            <i class="fas fa-users"></i>
                        </div>
                    </div>
                    <div class="card-value">156</div>
                    <div class="card-desc">
                        <i class="fas fa-user-clock"></i>
                        Şu anda çevrimiçi
                    </div>
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
                        <label class="form-label" id="input1-label">
                            <i class="fas fa-tag"></i>
                            TC Kimlik No
                        </label>
                        <input type="text" class="form-input" id="input1" placeholder="TC kimlik numarası">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" id="input2-label">
                            <i class="fas fa-tags"></i>
                            Ek Parametre
                        </label>
                        <input type="text" class="form-input" id="input2" placeholder="İsteğe bağlı parametre">
                    </div>
                    
                    <button class="btn btn-primary" data-action="runQuery">
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
                    <button class="btn btn-logout" data-action="clearResults">
                        <i class="fas fa-trash"></i> Temizle
                    </button>
                </div>
                
                <div class="results-content" id="results">
                    <div class="loading">
                        <i class="fas fa-search"></i>
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
            'allvesika': 'TC Kimlik numarası ile tüm vesika bilgilerini sorgulama',
            'anne': 'TC Kimlik numarası ile anne bilgisi sorgulama',
            'baba': 'TC Kimlik numarası ile baba bilgisi sorgulama',
            'hane': 'TC Kimlik numarası ile hane bilgileri sorgulama',
            'sulale': 'TC Kimlik numarası ile sülale bilgileri sorgulama',
            'cocuk': 'TC Kimlik numarası ile çocuk bilgileri sorgulama',
            'isyeri': 'TC Kimlik numarası ile işyeri bilgileri sorgulama',
            'isyeriyetkili': 'TC Kimlik numarası ile işyeri yetkili sorgulama',
            'tapu': 'TC Kimlik numarası ile tapu bilgileri sorgulama',
            'sgkpro': 'TC Kimlik numarası ile SGK bilgileri sorgulama',
            'vergi': 'TC Kimlik numarası ile vergi bilgileri sorgulama',
            'premadres': 'TC Kimlik numarası ile premadres sorgulama',
            'premad': 'Ad, il ve ilçe bilgileri ile premad sorgulama',
            'nvi': 'TC Kimlik numarası ile NVI sorgulama',
            'muhallev': 'TC Kimlik numarası ile muhallev sorgulama',
            'hanepro': 'TC Kimlik numarası ile hane pro sorgulama',
            'ehlt': 'TC Kimlik numarası ile EHLT sorgulama',
            'ayak': 'TC Kimlik numarası ile ayak numarası sorgulama',
            'boy': 'TC Kimlik numarası ile boy bilgisi sorgulama',
            'burc': 'TC Kimlik numarası ile burç sorgulama',
            'cm': 'TC Kimlik numarası ile CM sorgulama',
            'meslek': 'TC Kimlik numarası ile meslek sorgulama',
            'tcgsm': 'TC Kimlik numarası ile GSM sorgulama',
            'adsoyadil': 'Ad, soyad ve il bilgileri ile kişi sorgulama',
            'personel': 'TC Kimlik numarası ile personel sorgulama',
            'internet': 'TC Kimlik numarası ile internet sorgulama',
            'fatura': 'TC Kimlik numarası ile fatura sorgulama',
            'mhrs': 'TC Kimlik numarası ile MHRS sorgulama',
            'basvuru': 'TC Kimlik numarası ile başvuru sorgulama',
            'diploma': 'TC Kimlik numarası ile diploma sorgulama',
            'okulno': 'TC Kimlik numarası ile okul numarası sorgulama',
            'okulsicil': 'TC Kimlik numarası ile okul sicil sorgulama',
            'lgs': 'TC Kimlik numarası ile LGS sorgulama',
            'sertifika': 'TC Kimlik numarası ile sertifika sorgulama',
            'kizlik': 'TC Kimlik numarası ile kızlık soyadı sorgulama',
            'hikaye': 'TC Kimlik numarası ile hikaye sorgulama',
            'telegram': 'Telegram kullanıcı adı sorgulama',
            'facebook': 'Facebook/Telefon numarası sorgulama',
            'email_sorgu': 'E-posta adresi sorgulama',
            'plaka': 'Plaka sorgulama',
            'aracparca': 'Plaka ile araç parça sorgulama',
            'imei': 'IMEI numarası sorgulama',
            'operator': 'GSM numarası ile operatör sorgulama',
            'gsmdetay': 'GSM numarası ile detaylı sorgulama',
            'havadurumu': 'Şehir ile hava durumu sorgulama',
            'subdomain': 'URL ile subdomain sorgulama',
            'nezcane': 'İl ve ilçe ile nezcane sorgulama',
            'şehit': 'Ad soyad ile şehit sorgulama',
            'interpol': 'Ad soyad ile interpol sorgulama',
            'sexgörsel': 'Soru ile sex görsel sorgulama',
            'nude': 'Nude sorgulama',
            'smsbomber': 'SMS Bomber aracı - Telefon numarasına SMS gönderin',
            'smsapi': 'API Yönetimi - SMS API ayarlarını yönetin',
            'insta': 'Instagram kullanıcı adı ile sorgulama',
            'facebook_hanedan': 'Ad ve soyad ile Facebook hanedan sorgulama',
            'uni': 'TC Kimlik numarası ile üniversite sorgulama',
            'akp': 'Ad ve soyad ile AKP sorgulama',
            'aifoto': 'Resim URL'si ile yapay zeka fotoğraf sorgulama',
            'papara': 'Papara numarası ile sorgulama',
            'ininal': 'İninal kart numarası ile sorgulama',
            'turknet': 'TC Kimlik numarası ile TurkNet sorgulama',
            'smsbomber': 'SMS Bomber aracı - Telefon numarasına SMS gönderin',
            'discord': 'Discord sunucu bilgileri'
        };
        
        const queryLabels = {
            "dashboard": ["", ""],
            "history": ["", ""],
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
            "adres": ["TC Kimlik No", ""],
            "insta": ["kullanıcı adı", ""],
            "facebook hanedan": ["ad", "soyad"],
            "uni": ["TC Kimlik No", ""],
            "ai foto": ["ımg url", ""],
            "papara": ["papara no", ""],
            "ininal": ["ininal no", ""],
            "smsbomber": ["Telefon Numarası", "Mesaj (Opsiyonel)"],
            "smsapi": ["API Adı", "API URL"],
            "discord": ["", ""]
        };
        
        // Menü arama fonksiyonu
        function filterMenu() {
            const input = document.getElementById('menuSearch');
            const filter = input.value.toUpperCase();
            const navItems = document.querySelectorAll('.nav-item');
            
            navItems.forEach(item => {
                const text = item.textContent || item.innerText;
                if (text.toUpperCase().indexOf(filter) > -1) {
                    item.style.display = '';
                    // Vurgulama ekle
                    if (filter) {
                        const regex = new RegExp(filter, 'gi');
                        item.innerHTML = item.innerHTML.replace(regex, match => `<span style="background-color: rgba(108, 92, 231, 0.3); border-radius: 3px; padding: 0 2px;">${match}</span>`);
                    }
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        // Menü toggle fonksiyonu
        document.getElementById('menuToggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
        });
        
        function setQuery(queryType, clickedElement) {
            currentQuery = queryType;
            updateFormLabels();
            
            // Tüm nav-item'lardan active class'ını kaldır
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Tıklanan elemente active class'ını ekle
            if (clickedElement) {
                clickedElement.classList.add('active');
            }
            
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
            
            document.getElementById('input1-label').innerHTML = `<i class="fas fa-tag"></i> ${queryLabels[currentQuery][0]}`;
            document.getElementById('input2-label').innerHTML = `<i class="fas fa-tags"></i> ${queryLabels[currentQuery][1]}`;
            document.getElementById('input1').placeholder = queryLabels[currentQuery][0] + ' girin';
            document.getElementById('input2').placeholder = queryLabels[currentQuery][1] + ' girin';
            
            if (queryLabels[currentQuery][0] === '') {
                document.getElementById('input1-label').style.display = 'none';
                document.getElementById('input1').style.display = 'none';
            } else {
                document.getElementById('input1-label').style.display = 'flex';
                document.getElementById('input1').style.display = 'block';
            }
            
            if (queryLabels[currentQuery][1] === '') {
                document.getElementById('input2-label').style.display = 'none';
                document.getElementById('input2').style.display = 'none';
            } else {
                document.getElementById('input2-label').style.display = 'flex';
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
            
            // Discord özel durumu
            if (currentQuery === 'discord') {
                document.getElementById('results').innerHTML = `
                    <div style="padding: 20px; text-align: center; color: var(--light);">
                        <i class="fab fa-discord" style="font-size: 48px; margin-bottom: 15px; color: #7289da;"></i>
                        <h3>Discord Sunucumuza Katılın!</h3>
                        <p style="margin: 15px 0; font-size: 16px;">CAPPYBEAM Premium Discord sunucusuna katılarak güncel bilgileri alın ve toplulukla etkileşime geçin.</p>
                        <a href="https://discord.gg/cngzsvsaX2" target="_blank" style="
                            display: inline-block;
                            background: linear-gradient(135deg, #7289da, #5865f2);
                            color: white;
                            padding: 12px 24px;
                            border-radius: 25px;
                            text-decoration: none;
                            font-weight: 600;
                            margin-top: 15px;
                            transition: all 0.3s ease;
                            box-shadow: 0 5px 15px rgba(114, 137, 218, 0.3);
                        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(114, 137, 218, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 5px 15px rgba(114, 137, 218, 0.3)'">
                            <i class="fas fa-discord" style="font-size: 48px; margin-bottom: 15px; color: #7289da;"></i>
                            Sunucuya Katıl
                        </a>
                    </div>
                `;
                return;
            }
            
            // SMS API Yönetimi özel durumu
            if (currentQuery === 'smsapi') {
                document.getElementById('results').innerHTML = `
                    <div style="padding: 20px; text-align: center; color: var(--light);">
                        <i class="fas fa-cog" style="font-size: 48px; margin-bottom: 15px; color: var(--primary);"></i>
                        <h3>SMS API Yönetimi</h3>
                        <p style="margin: 15px 0; font-size: 16px;">SMS API ayarlarını yönetmek için bu özellik henüz implemente edilmemiştir.</p>
                        <div style="background: rgba(0, 0, 0, 0.2); padding: 20px; border-radius: 12px; margin-top: 20px;">
                            <p style="color: var(--light-gray); font-size: 14px;">
                                <i class="fas fa-info-circle" style="margin-right: 8px; color: var(--info);"></i>
                                Bu özellik gelecek güncellemelerde eklenecektir.
                            </p>
                        </div>
                    </div>
                `;
                return;
            }
            
            // Özel durumlar için validasyon
            if ((currentQuery === 'adsoyad' || currentQuery === 'adsoyadil') && !input1) {
                showError('Lütfen en az bir ad bilgisi girin.');
                return;
            }
            
            if (queryLabels[currentQuery][0] !== '' && !input1) {
                showError(`Lütfen ${queryLabels[currentQuery][0]} alanını doldurun.`);
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
                    showError(data.error);
                } else {
                    // API response'unu daha iyi handle edelim
                    let resultData = data.result;
                    
                    // Eğer result yoksa, tüm data'yı göster
                    if (resultData === undefined || resultData === null) {
                        resultData = data;
                    }
                    
                    // Veriyi log'layalım (debug için)
                    console.log('API Response:', data);
                    console.log('Result Data:', resultData);
                    
                    displayResults(resultData);
                }
            })
            .catch(error => {
                showError('İstek hatası: ' + error.message);
            });
        }
        
        function showError(message) {
            document.getElementById('results').innerHTML = `
                <div style="color: var(--danger); padding: 20px; text-align: center;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 15px;"></i>
                    <h3>Hata</h3>
                    <p>${message}</p>
                </div>
            `;
        }
        
        function displayResults(data) {
            let html = '';
            
            // Veriyi daha iyi formatlayalım
            function formatValue(value) {
                if (value === null || value === undefined) return '<span style="color: var(--light-gray); font-style: italic;">Boş</span>';
                if (typeof value === 'object') {
                    return `<pre style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; overflow-x: auto; margin: 0;">${JSON.stringify(value, null, 2)}</pre>`;
                }
                if (typeof value === 'string' && value.length > 100) {
                    return `<div style="max-height: 200px; overflow-y: auto;">${value}</div>`;
                }
                return String(value);
            }
            
            // TC ve adres bilgilerini ayrı bölümlerde göstermek için
            function categorizeData(data) {
                const tcFields = ['tc', 'tcno', 'tc_no', 'kimlik', 'kimlik_no', 'tckn', 'kendisi'];
                const addressFields = ['adres', 'address', 'il', 'ilce', 'mahalle', 'sokak', 'cadde', 'posta_kodu', 'sehir', 'bolge', 'nüfus_il', 'nüfus_ilçe'];
                const personalFields = ['ad', 'soyad', 'ad_soyad', 'isim', 'dogum_tarihi', 'dogum_yeri', 'anne_adi', 'baba_adi', 'cinsiyet', 'adi', 'soyadi', 'doğum_tarihi', 'anne_adı', 'baba_adı'];
                const contactFields = ['telefon', 'tel', 'phone', 'email', 'eposta', 'gsm'];
                
                const categories = {
                    tc: {},
                    address: {},
                    personal: {},
                    contact: {},
                    other: {}
                };
                
                for (const [key, value] of Object.entries(data)) {
                    const lowerKey = key.toLowerCase();
                    let categorized = false;
                    
                    if (tcFields.some(field => lowerKey.includes(field))) {
                        categories.tc[key] = value;
                        categorized = true;
                    } else if (addressFields.some(field => lowerKey.includes(field))) {
                        categories.address[key] = value;
                        categorized = true;
                    } else if (personalFields.some(field => lowerKey.includes(field))) {
                        categories.personal[key] = value;
                        categorized = true;
                    } else if (contactFields.some(field => lowerKey.includes(field))) {
                        categories.contact[key] = value;
                        categorized = true;
                    }
                    
                    if (!categorized) {
                        categories.other[key] = value;
                    }
                }
                
                return categories;
            }
            
            if (Array.isArray(data) && data.length > 0) {
                html = '<div class="result-header"><h3>📊 Sorgu Sonuçları (' + data.length + ' kayıt)</h3></div>';
                
                // Ana tablo oluştur - görseldeki gibi
                html += '<div class="overflow-x-auto">';
                html += '<table class="result-table" style="width: 100%; border-collapse: collapse; background: rgba(0,0,0,0.15); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); margin: 20px 0;">';
                
                // Tablo başlığı - görseldeki gibi
                const firstRow = data[0];
                const headers = Object.keys(firstRow);
                html += '<thead><tr>';
                headers.forEach(header => {
                    const formattedHeader = header.charAt(0).toUpperCase() + header.slice(1).replace(/_/g, ' ');
                    html += '<th style="text-align: left; padding: 18px 20px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); border-bottom: 2px solid rgba(255, 255, 255, 0.1); font-weight: 600; color: white; text-transform: uppercase; font-size: 14px; letter-spacing: 0.5px; position: sticky; top: 0; z-index: 10;">' + formattedHeader + '</th>';
                });
                html += '</tr></thead>';
                
                // Tablo gövdesi
                html += '<tbody>';
                data.forEach((row, index) => {
                    const rowClass = index % 2 === 0 ? 'even' : 'odd';
                    html += '<tr class="' + rowClass + '" style="background: ' + (rowClass === 'even' ? 'rgba(0, 0, 0, 0.05)' : 'transparent') + ';">';
                    headers.forEach(header => {
                        const value = row[header];
                        html += '<td style="padding: 18px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); word-wrap: break-word; max-width: 350px; vertical-align: top; line-height: 1.6; color: var(--light);">' + formatValue(value) + '</td>';
                    });
                    html += '</tr>';
                });
                html += '</tbody>';
                html += '</table>';
                html += '</div>';
                
            } else if (typeof data === 'object' && data !== null) {
                const categories = categorizeData(data);
                html = '<div class="result-header"><h3>📋 Sorgu Sonucu</h3></div>';
                
                // TC Bilgileri
                if (Object.keys(categories.tc).length > 0) {
                    html += `<div class="category-section">`;
                    html += `<h5 style="color: var(--success); margin: 10px 0;">🆔 TC Kimlik Bilgileri</h5>`;
                    html += '<table class="result-table">';
                    html += '<thead><tr><th>Alan</th><th>Değer</th></tr></thead><tbody>';
                    for (const [key, value] of Object.entries(categories.tc)) {
                        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<tr><td class="key-column">${formattedKey}</td><td class="value-column">${formatValue(value)}</td></tr>`;
                    }
                    html += '</tbody></table></div>';
                }
                
                // Adres Bilgileri
                if (Object.keys(categories.address).length > 0) {
                    html += `<div class="category-section">`;
                    html += `<h5 style="color: var(--warning); margin: 10px 0;">🏠 Adres Bilgileri</h5>`;
                    html += '<table class="result-table">';
                    html += '<thead><tr><th>Alan</th><th>Değer</th></tr></thead><tbody>';
                    for (const [key, value] of Object.entries(categories.address)) {
                        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<tr><td class="key-column">${formattedKey}</td><td class="value-column">${formatValue(value)}</td></tr>`;
                    }
                    html += '</tbody></table></div>';
                }
                
                // Kişisel Bilgiler
                if (Object.keys(categories.personal).length > 0) {
                    html += `<div class="category-section">`;
                    html += `<h5 style="color: var(--warning); margin: 10px 0;">👤 Kişisel Bilgiler</h5>`;
                    html += '<table class="result-table">';
                    html += '<thead><tr><th>Alan</th><th>Değer</th></tr></thead><tbody>';
                    for (const [key, value] of Object.entries(categories.personal)) {
                        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<tr><td class="key-column">${formattedKey}</td><td class="value-column">${formatValue(value)}</td></tr>`;
                    }
                    html += '</tbody></table></div>';
                }
                
                // İletişim Bilgileri
                if (Object.keys(categories.contact).length > 0) {
                    html += `<div class="category-section">`;
                    html += `<h5 style="color: var(--primary); margin: 10px 0;">📞 İletişim Bilgileri</h5>`;
                    html += '<table class="result-table">';
                    html += '<thead><tr><th>Alan</th><th>Değer</th></tr></thead><tbody>';
                    for (const [key, value] of Object.entries(categories.contact)) {
                        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<tr><td class="key-column">${formattedKey}</td><td class="value-column">${formatValue(value)}</td></tr>`;
                    }
                    html += '</tbody></table></div>';
                }
                
                // Diğer Bilgiler
                if (Object.keys(categories.other).length > 0) {
                    html += `<div class="category-section">`;
                    html += `<h5 style="color: var(--secondary); margin: 10px 0;">📝 Diğer Bilgiler</h5>`;
                    html += '<table class="result-table">';
                    html += '<thead><tr><th>Alan</th><th>Değer</th></tr></thead><tbody>';
                    for (const [key, value] of Object.entries(categories.other)) {
                        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
                        html += `<tr><td class="key-column">${formattedKey}</td><td class="value-column">${formatValue(value)}</td></tr>`;
                    }
                    html += '</tbody></table></div>';
                }
                
            } else if (typeof data === 'string') {
                html = '<div class="result-header"><h3>📝 Metin Sonucu</h3></div>';
                html += `<div style="background: rgba(0,0,0,0.1); padding: 20px; border-radius: 10px; white-space: pre-wrap; font-family: monospace;">${data}</div>`;
            } else {
                html = '<div class="result-header"><h3>🔍 Ham Veri</h3></div>';
                html += `<pre style="background: rgba(0,0,0,0.1); padding: 20px; border-radius: 10px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>`;
            }
            
            document.getElementById('results').innerHTML = html;
        }
        
        function clearResults() {
            document.getElementById('results').innerHTML = `
                <div class="loading">
                    <i class="fas fa-search"></i>
                    <span>Sorgu sonuçları burada görünecek</span>
                </div>
            `;
        }
        
        function logout() {
            window.location.href = "/logout";
        }
        
        // Sayfa yüklendiğinde
        document.addEventListener('DOMContentLoaded', function() {
            updateFormLabels();
            
            // Tüm navigation item'lara event listener ekle
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const queryType = this.getAttribute('data-query');
                    if (queryType) {
                        setQuery(queryType, this);
                    }
                });
            });
            
            // Query butonuna event listener ekle
            const queryBtn = document.querySelector('.btn-primary[data-action="runQuery"]');
            if (queryBtn) {
                queryBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    runQuery();
                });
            }
            
            // Clear results butonuna event listener ekle
            const clearBtn = document.querySelector('.btn-logout[data-action="clearResults"]');
            if (clearBtn) {
                clearBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    clearResults();
                });
            }
            
            // Logout butonuna event listener ekle
            const logoutBtn = document.querySelector('.btn-logout[data-action="logout"]');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    logout();
                });
            }
            
            // Menu toggle butonuna event listener ekle
            const menuToggle = document.getElementById('menuToggle');
            if (menuToggle) {
                menuToggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    document.getElementById('sidebar').classList.toggle('active');
                });
            }
            
            // Mobil menü için dışarı tıklama kapatma
            document.addEventListener('click', function(event) {
                const sidebar = document.getElementById('sidebar');
                const menuToggle = document.getElementById('menuToggle');
                
                if (window.innerWidth <= 968 && 
                    !sidebar.contains(event.target) && 
                    !menuToggle.contains(event.target) &&
                    sidebar.classList.contains('active')) {
                    sidebar.classList.remove('active');
                }
            });
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
        # URL oluşturma
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

        # API isteği yapma
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        r = requests.get(url, timeout=20, headers=headers, verify=False)
        
        # HTTP hata kodlarını kontrol etme
        if r.status_code != 200:
            return jsonify({"error": f"API yanıt vermedi. HTTP Kodu: {r.status_code}"})
        
        result_status = "success"
        
        # Yanıtı işleme
        try:
            # JSON yanıtı deneme
            result = r.json()
            
            # Boş yanıt kontrolü
            if not result or (isinstance(result, dict) and not result):
                return jsonify({"error": "API'den veri alınamadı. Lütfen parametreleri kontrol edin."})
            
            # Liste yanıtı
            if isinstance(result, list):
                if len(result) == 0:
                    return jsonify({"error": "Sonuç bulunamadı. Lütfen parametreleri kontrol edin."})
                return jsonify({"result": result})
            
            # Sözlük yanıtı
            elif isinstance(result, dict):
                # Hata mesajı kontrolü
                if "error" in result and result["error"]:
                    return jsonify({"error": f"API Hatası: {result['error']}"})
                
                # Veri alanlarını kontrol etme
                if "data" in result:
                    if not result["data"]:
                        return jsonify({"error": "Sonuç bulunamadı. Lütfen parametreleri kontrol edin."})
                    return jsonify({"result": result["data"]})
                elif "results" in result:
                    if not result["results"]:
                        return jsonify({"error": "Sonuç bulunamadı. Lütfen parametreleri kontrol edin."})
                    return jsonify({"result": result["results"]})
                else:
                    return jsonify({"result": result})
            
            # Diğer yanıt türleri
            else:
                return jsonify({"result": result})
                
        except ValueError:
            # JSON parse edilemezse metin olarak döndür
            text_result = r.text.strip()
            if not text_result:
                return jsonify({"error": "API'den veri alınamadı. Lütfen parametreleri kontrol edin."})
            
            # Hata mesajı kontrolü
            if "error" in text_result.lower() or "not found" in text_result.lower():
                return jsonify({"error": f"Sonuç bulunamadı: {text_result}"})
            
            return jsonify({"result": text_result})
            
    except requests.exceptions.Timeout:
        return jsonify({"error": "API yanıt vermedi. Zaman aşımı."})
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "API'ye bağlanılamadı. Bağlantı hatası."})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API isteği başarısız: {str(e)}"})
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen hata: {str(e)}"})
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
