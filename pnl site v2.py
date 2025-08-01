
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_123')

# Kullanıcı veritabanını dosyadan yükle
def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            # JSON'dan gelen verileri düzenle
            users = {}
            for username, data in users_data.items():
                users[username] = {
                    'password': data['password'],
                    'is_admin': username == 'admin',  # İlk kullanıcı admin olsun
                    'is_vip': True,  # Tüm kullanıcılar VIP olsun
                    'email': f"{username}@example.com",
                    'created_at': "2024-01-01"
                }
            return users
    except FileNotFoundError:
        # Eğer dosya yoksa boş dict döndür
        return {}

def save_users(users):
    try:
        # Sadece password bilgilerini kaydet
        users_data = {}
        for username, data in users.items():
            users_data[username] = {'password': data['password']}
        
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Kullanıcı verileri kaydedilemedi: {e}")

# Kullanıcıları yükle
USERS = load_users()

# API URL'leri
API_URLS = {
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilce.php?ad={ad}&soyad={soyad}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sulale.php?tc={tc}",
    "okulno": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulno.php?tc={tc}",
    "isyeriyetkili": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={tc}",
    "gsmdetay": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={gsm}",
    "gsm": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsm.php?gsm={gsm}",
    "adres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/adres.php?tc={tc}",
    "adsoyadilice": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilce.php?ad={ad}&soyad={soyad}",
}

# Decorator'lar
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Giriş yapmalısınız!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def vip_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_vip'):
            flash('VIP üyelik gereklidir!', 'warning')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin yetkisi gerekli!', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# HTML Template'leri
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
        :root {
            --primary-color: #00d4ff;
            --secondary-color: #0099cc;
            --success-color: #00ff88;
            --warning-color: #ffaa00;
            --danger-color: #ff4757;
            --dark-bg: #0a0a0a;
            --dark-card: #1a1a1a;
            --dark-border: #333333;
            --text-primary: #ffffff;
            --text-secondary: #b0b0b0;
        }

        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0f0f0f 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text-primary);
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(255, 170, 0, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .card {
            border: none;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            backdrop-filter: blur(20px);
            background: rgba(26, 26, 26, 0.9);
            border: 1px solid var(--dark-border);
        }

        .btn-primary {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            border: none;
            border-radius: 25px;
            padding: 12px 30px;
            font-weight: 600;
            transition: all 0.3s ease;
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
            color: white;
        }

        .form-control, .form-select {
            border-radius: 15px;
            border: 2px solid var(--dark-border);
            padding: 12px 15px;
            transition: all 0.3s ease;
            background: rgba(26, 26, 26, 0.8);
            color: var(--text-primary);
        }

        .form-control:focus, .form-select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(0, 212, 255, 0.25);
            background: rgba(26, 26, 26, 0.9);
            color: var(--text-primary);
        }

        .form-control::placeholder {
            color: var(--text-secondary);
        }

        .navbar {
            background: rgba(26, 26, 26, 0.95) !important;
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--dark-border);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        .logo-container {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 8px 15px;
            border-radius: 25px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            transition: all 0.3s ease;
        }

        .logo-image {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid var(--primary-color);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.3));
        }

        .logo-text {
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color), #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
            letter-spacing: 1px;
        }

        .vip-badge {
            background: linear-gradient(45deg, #ffaa00, #ff8800);
            color: white;
            padding: 6px 15px;
            border-radius: 25px;
            font-size: 0.8rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(255, 170, 0, 0.3);
            border: 1px solid rgba(255, 170, 0, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .admin-badge {
            background: linear-gradient(45deg, #ff4757, #ff3742);
            color: white;
            padding: 6px 15px;
            border-radius: 25px;
            font-size: 0.8rem;
            font-weight: 700;
            box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
            border: 1px solid rgba(255, 71, 87, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .api-card {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        }

        .api-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 25px 50px rgba(0, 212, 255, 0.4);
        }

        .result-box {
            background: rgba(26, 26, 26, 0.8);
            border-radius: 15px;
            padding: 20px;
            border-left: 4px solid var(--primary-color);
            margin-top: 20px;
            border: 1px solid var(--dark-border);
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner-border {
            width: 3rem;
            height: 3rem;
            color: var(--primary-color);
        }

        .alert {
            border-radius: 15px;
            border: none;
        }

        .alert-success {
            background: rgba(0, 255, 136, 0.1);
            color: var(--success-color);
            border-left: 4px solid var(--success-color);
        }

        .alert-warning {
            background: rgba(255, 170, 0, 0.1);
            color: var(--warning-color);
            border-left: 4px solid var(--warning-color);
        }

        .alert-danger {
            background: rgba(255, 71, 87, 0.1);
            color: var(--danger-color);
            border-left: 4px solid var(--danger-color);
        }

        .alert-info {
            background: rgba(0, 212, 255, 0.1);
            color: var(--primary-color);
            border-left: 4px solid var(--primary-color);
        }

        .table {
            color: var(--text-primary);
        }

        .table-dark {
            background: rgba(26, 26, 26, 0.8);
        }

        .dropdown-menu {
            background: rgba(26, 26, 26, 0.95);
            border: 1px solid var(--dark-border);
            border-radius: 15px;
        }

        .dropdown-item {
            color: var(--text-primary);
        }

        .dropdown-item:hover {
            background: rgba(0, 212, 255, 0.1);
            color: var(--primary-color);
        }

        .bg-light {
            background: rgba(26, 26, 26, 0.8) !important;
            color: var(--text-primary);
        }

        .text-muted {
            color: var(--text-secondary) !important;
        }

        pre {
            background: rgba(26, 26, 26, 0.8);
            color: var(--text-primary);
            border-radius: 10px;
            border: 1px solid var(--dark-border);
        }

        .card-header {
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            border-radius: 20px 20px 0 0 !important;
            border: none;
        }

        .btn-outline-primary {
            border-color: var(--primary-color);
            color: var(--primary-color);
        }

        .btn-outline-primary:hover {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
        }

        .btn-outline-warning {
            border-color: var(--warning-color);
            color: var(--warning-color);
        }

        .btn-outline-warning:hover {
            background: var(--warning-color);
            border-color: var(--warning-color);
            color: white;
        }

        .btn-outline-info {
            border-color: var(--primary-color);
            color: var(--primary-color);
        }

        .btn-outline-info:hover {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    {% if session.logged_in %}
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <div class="logo-container">
                    <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo" class="logo-image">
                    <span class="logo-text">CappyBeamServicesChecks</span>
                </div>
            </a>

            <div class="navbar-nav ms-auto">
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-user-circle me-1"></i>{{ session.username }}
                        {% if session.is_vip %}<span class="vip-badge ms-1">VIP</span>{% endif %}
                        {% if session.is_admin %}<span class="admin-badge ms-1">ADMIN</span>{% endif %}
                    </a>
                    <ul class="dropdown-menu">
                        {% if session.is_admin %}
                        <li><a class="dropdown-item" href="{{ url_for('admin') }}">
                            <i class="fas fa-cog me-2"></i>Admin Panel
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        {% endif %}
                        <li><a class="dropdown-item" href="{{ url_for('logout') }}">
                            <i class="fas fa-sign-out-alt me-2"></i>Çıkış Yap
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>
    {% endif %}

    <!-- Main Content -->
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'danger' else 'success' if category == 'success' else 'warning' if category == 'warning' else 'info' }} alert-dismissible fade show" role="alert">
                        <i class="fas fa-{{ 'exclamation-triangle' if category == 'danger' else 'check-circle' if category == 'success' else 'exclamation-circle' if category == 'warning' else 'info-circle' }} me-2"></i>
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {{ content | safe }}
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    {{ scripts | safe }}
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<div class="row justify-content-center align-items-center min-vh-100">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <div class="mb-3">
                        <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid var(--primary-color); box-shadow: 0 0 25px rgba(0, 212, 255, 0.4);">
                    </div>
                    <h2 class="fw-bold text-white mb-2">CappyBeamServicesChecks</h2>
                    <p class="text-secondary">Hesabınıza giriş yapın</p>
                </div>

                <form method="POST" action="{{ url_for('login') }}">
                    <div class="mb-3">
                        <label for="username" class="form-label">
                            <i class="fas fa-user me-2"></i>Kullanıcı Adı
                        </label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="Kullanıcı adınızı girin" required>
                    </div>

                    <div class="mb-4">
                        <label for="password" class="form-label">
                            <i class="fas fa-lock me-2"></i>Şifre
                        </label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="Şifrenizi girin" required>
                    </div>

                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-sign-in-alt me-2"></i>Giriş Yap
                    </button>
                </form>

                <div class="text-center mt-4">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        users.json dosyasında kayıtlı herhangi bir kullanıcı ile giriş yapabilirsiniz
                    </small>
                </div>

                <hr class="my-4">

                <div class="text-center">
                    <p class="text-muted mb-3">Hesabınız yok mu?</p>
                    <a href="{{ url_for('register') }}" class="btn btn-outline-primary">
                        <i class="fas fa-user-plus me-2"></i>Kayıt Ol
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
'''

REGISTER_TEMPLATE = '''
<div class="row justify-content-center align-items-center min-vh-100">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <div class="mb-3">
                        <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo" style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid var(--primary-color); box-shadow: 0 0 25px rgba(0, 212, 255, 0.4);">
                    </div>
                    <h2 class="fw-bold text-white mb-2">CappyBeamServicesChecks</h2>
                    <p class="text-secondary">Yeni hesap oluşturun</p>
                </div>

                <form method="POST" action="{{ url_for('register') }}">
                    <div class="mb-3">
                        <label for="username" class="form-label">
                            <i class="fas fa-user me-2"></i>Kullanıcı Adı
                        </label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="Kullanıcı adınızı girin" required>
                    </div>

                    <div class="mb-3">
                        <label for="email" class="form-label">
                            <i class="fas fa-envelope me-2"></i>E-posta
                        </label>
                        <input type="email" class="form-control" id="email" name="email" placeholder="E-posta adresinizi girin" required>
                    </div>

                    <div class="mb-3">
                        <label for="password" class="form-label">
                            <i class="fas fa-lock me-2"></i>Şifre
                        </label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="Şifrenizi girin" required>
                    </div>

                    <div class="mb-4">
                        <label for="confirm_password" class="form-label">
                            <i class="fas fa-lock me-2"></i>Şifre Tekrar
                        </label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" placeholder="Şifrenizi tekrar girin" required>
                    </div>

                    <button type="submit" class="btn btn-primary w-100">
                        <i class="fas fa-user-plus me-2"></i>Kayıt Ol
                    </button>
                </form>

                <div class="text-center mt-4">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Zaten hesabınız var mı?
                    </small>
                    <br>
                    <a href="{{ url_for('login') }}" class="btn btn-outline-primary btn-sm mt-2">
                        <i class="fas fa-sign-in-alt me-2"></i>Giriş Yap
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
''' 

DASHBOARD_TEMPLATE = ''' 
<div class="row">
    <div class="col-12">
        <div class="card mb-4">
            <div class="card-body">
                <div class="d-flex align-items-center mb-3">
                    <div class="me-3">
                        <img src="https://www.coca-cola.com/content/dam/onexp/tr/tr/brands/cappy/global-cappy-logo.png" alt="Cappy Logo" style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid var(--primary-color); box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);">
                    </div>
                    <div>
                        <h3 class="mb-1">Hoş geldin, {{ username }}!</h3>
                        <div class="d-flex gap-2">
                            {% if is_vip %}
                            <span class="vip-badge">
                                <i class="fas fa-crown me-1"></i>VIP Üye
                            </span>
                            {% endif %}
                            {% if is_admin %}
                            <span class="admin-badge">
                                <i class="fas fa-shield-alt me-1"></i>Admin
                            </span>
                            {% endif %}
                        </div>
                    </div>
                </div>

                {% if is_vip %}
                <div class="alert alert-success">
                    <i class="fas fa-check-circle me-2"></i>
                    VIP üyeliğiniz aktif! Tüm API servislerine erişiminiz var.
                </div>
                {% else %}
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    VIP üyelik gereklidir. API servislerini kullanmak için admin ile iletişime geçin.
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

{% if is_vip %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fas fa-search me-2"></i>API Sorgulama
                </h5>
            </div>
            <div class="card-body">
                <form id="queryForm">
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="endpoint" class="form-label">
                                <i class="fas fa-cogs me-2"></i>API Servisi
                            </label>
                            <select class="form-select" id="endpoint" name="endpoint" required>
                                <option value="">Servis seçin...</option>
                                {% for endpoint in api_endpoints %}
                                <option value="{{ endpoint }}">{{ endpoint.upper() }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="param" class="form-label">
                                <i class="fas fa-key me-2"></i>Parametre
                            </label>
                            <input type="text" class="form-control" id="param" name="param" placeholder="Sorgu parametresini girin" required>
                            <div class="form-text">
                                <small id="paramHelp" class="text-muted"></small>
                            </div>
                        </div>
                        <div class="col-md-2 mb-3 d-flex align-items-end">
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-search me-2"></i>Sorgula
                            </button>
                        </div>
                    </div>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p class="mt-2 text-muted">Sorgu işleniyor...</p>
                </div>

                <div id="result" class="result-box" style="display: none;">
                    <h6 class="mb-3">
                        <i class="fas fa-chart-bar me-2"></i>Sorgu Sonucu
                    </h6>
                    <pre id="resultContent" class="bg-light p-3 rounded"></pre>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="fas fa-info-circle me-2"></i>API Servisleri
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-user me-2"></i>ADSOYAD</h6>
                            <p class="mb-2">Ad ve soyad ile sorgulama</p>
                            <small>Örnek: Ahmet Yılmaz</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-id-card me-2"></i>TCPRO</h6>
                            <p class="mb-2">TC kimlik numarası ile sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-mobile-alt me-2"></i>TCGSM</h6>
                            <p class="mb-2">TC ile GSM sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-home me-2"></i>TAPU</h6>
                            <p class="mb-2">TC ile tapu sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-users me-2"></i>SULALE</h6>
                            <p class="mb-2">TC ile sülale sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-graduation-cap me-2"></i>OKULNO</h6>
                            <p class="mb-2">TC ile okul numarası sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-building me-2"></i>ISYERIYETKILI</h6>
                            <p class="mb-2">TC ile işyeri yetkili sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-phone-alt me-2"></i>GSMDETAY</h6>
                            <p class="mb-2">GSM detaylı sorgulama</p>
                            <small>Örnek: 05551234567</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-mobile-alt me-2"></i>GSM</h6>
                            <p class="mb-2">GSM numarası ile sorgulama</p>
                            <small>Örnek: 05551234567</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-map-marker-alt me-2"></i>ADRES</h6>
                            <p class="mb-2">TC ile adres sorgulama</p>
                            <small>Örnek: 12345678901</small>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="api-card">
                            <h6><i class="fas fa-search me-2"></i>ADSOYADILICE</h6>
                            <p class="mb-2">Ad soyad ile il/ilçe sorgulama</p>
                            <small>Örnek: Ahmet Yılmaz</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
'''

ADMIN_TEMPLATE = '''
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="fas fa-cog me-2"></i>Admin Panel
                </h5>
            </div>
            <div class="card-body">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    Kullanıcı yönetimi ve sistem ayarları buradan yapılabilir.
                </div>

                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th><i class="fas fa-user me-2"></i>Kullanıcı Adı</th>
                                <th><i class="fas fa-envelope me-2"></i>E-posta</th>
                                <th><i class="fas fa-shield-alt me-2"></i>Admin</th>
                                <th><i class="fas fa-crown me-2"></i>VIP</th>
                                <th><i class="fas fa-cogs me-2"></i>İşlemler</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for username, user_data in users.items() %}
                            <tr>
                                <td>
                                    <strong>{{ username }}</strong>
                                    {% if username == session.username %}
                                    <span class="badge bg-primary ms-2">Siz</span>
                                    {% endif %}
                                </td>
                                <td>{{ user_data.email }}</td>
                                <td>
                                    {% if user_data.is_admin %}
                                    <span class="badge bg-danger">
                                        <i class="fas fa-check me-1"></i>Evet
                                    </span>
                                    {% else %}
                                    <span class="badge bg-secondary">
                                        <i class="fas fa-times me-1"></i>Hayır
                                    </span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if user_data.is_vip %}
                                    <span class="badge bg-warning text-dark">
                                        <i class="fas fa-crown me-1"></i>VIP
                                    </span>
                                    {% else %}
                                    <span class="badge bg-secondary">
                                        <i class="fas fa-times me-1"></i>Normal
                                    </span>
                                    {% endif %}
                                </td>
                                <td>
                                    {% if username != session.username %}
                                    <a href="{{ url_for('toggle_vip', username=username) }}" 
                                       class="btn btn-sm btn-outline-warning"
                                       onclick="return confirm('{{ username }} kullanıcısının VIP durumunu değiştirmek istediğinizden emin misiniz?')">
                                        <i class="fas fa-crown me-1"></i>VIP Toggle
                                    </a>
                                    {% else %}
                                    <span class="text-muted">Kendi hesabınız</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="mt-4">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6 class="card-title">
                                        <i class="fas fa-chart-bar me-2"></i>Sistem İstatistikleri
                                    </h6>
                                    <ul class="list-unstyled mb-0">
                                        <li><strong>Toplam Kullanıcı:</strong> {{ users|length }}</li>
                                        <li><strong>Admin Sayısı:</strong> {{ users.values() | selectattr('is_admin') | list | length }}</li>
                                        <li><strong>VIP Sayısı:</strong> {{ users.values() | selectattr('is_vip') | list | length }}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6 class="card-title">
                                        <i class="fas fa-tools me-2"></i>Hızlı İşlemler
                                    </h6>
                                    <div class="d-grid gap-2">
                                        <a href="{{ url_for('dashboard') }}" class="btn btn-outline-primary btn-sm">
                                            <i class="fas fa-arrow-left me-2"></i>Dashboard'a Dön
                                        </a>
                                        <button class="btn btn-outline-info btn-sm" onclick="location.reload()">
                                            <i class="fas fa-sync-alt me-2"></i>Sayfayı Yenile
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
'''

DASHBOARD_SCRIPTS = '''
<script>
$(document).ready(function() {
    // API endpoint seçildiğinde parametre yardımını göster
    $('#endpoint').change(function() {
        const endpoint = $(this).val();
        let helpText = '';

        switch(endpoint) {
            case 'adsoyad':
                helpText = 'Ad ve soyadı aralarında boşluk bırakarak girin';
                break;
            case 'tcpro':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'tcgsm':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'tapu':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'sulale':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'okulno':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'isyeriyetkili':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'gsmdetay':
                helpText = 'GSM numarasını girin (başında 0 olmadan)';
                break;
            case 'gsm':
                helpText = 'GSM numarasını girin (başında 0 olmadan)';
                break;
            case 'adres':
                helpText = 'TC kimlik numarasını girin (11 haneli)';
                break;
            case 'adsoyadilice':
                helpText = 'Ad ve soyadı aralarında boşluk bırakarak girin';
                break;
            default:
                helpText = '';
        }

        $('#paramHelp').text(helpText);
    });

    // Form submit
    $('#queryForm').submit(function(e) {
        e.preventDefault();

        const formData = {
            endpoint: $('#endpoint').val(),
            param: $('#param').val()
        };

        // Loading göster
        $('#loading').show();
        $('#result').hide();

        $.ajax({
            url: '/query',
            method: 'POST',
            data: formData,
            success: function(response) {
                $('#resultContent').text(JSON.stringify(response, null, 2));
                $('#result').show();
            },
            error: function(xhr) {
                let errorMsg = 'Bir hata oluştu';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                $('#resultContent').text('Hata: ' + errorMsg);
                $('#result').show();
            },
            complete: function() {
                $('#loading').hide();
            }
        });
    });
});
</script>
'''

# Route'lar
@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            session['is_admin'] = user.get('is_admin', False)
            session['is_vip'] = user.get('is_vip', False)
            flash('Başarıyla giriş yapıldı!', 'success')
            return redirect(url_for('dashboard'))
        flash('Geçersiz kullanıcı adı/şifre!', 'danger')
    return render_template_string(BASE_TEMPLATE, 
                                title='Giriş Yap - CappyBeamServicesChecks',
                                content=LOGIN_TEMPLATE,
                                scripts='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if username in USERS:
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'danger')
        elif password != confirm_password:
            flash('Şifreler eşleşmiyor!', 'danger')
        elif len(password) < 6:
            flash('Şifre en az 6 karakter olmalıdır!', 'danger')
        else:
            USERS[username] = {
                'password': generate_password_hash(password),
                'email': email,
                'is_admin': False,
                'is_vip': True,  # Yeni kullanıcılar VIP olsun
                'created_at': '2024-01-01'
            }
            # Kullanıcıları kaydet
            save_users(USERS)
            flash('Hesabınız başarıyla oluşturuldu! VIP erişiminiz aktif. Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))

    return render_template_string(BASE_TEMPLATE, 
                                title='Kayıt Ol - CappyBeamServicesChecks',
                                content=REGISTER_TEMPLATE,
                                scripts='')

@app.route('/dashboard')
@login_required
def dashboard():
    api_endpoints = list(API_URLS.keys())
    return render_template_string(BASE_TEMPLATE, 
                                title='Dashboard - CappyBeamServicesChecks',
                                content=DASHBOARD_TEMPLATE,
                                scripts=DASHBOARD_SCRIPTS,
                                username=session['username'],
                                is_vip=session.get('is_vip'),
                                is_admin=session.get('is_admin'),
                                api_endpoints=api_endpoints)

@app.route('/query', methods=['POST'])
@login_required
@vip_required
def query():
    endpoint = request.form['endpoint']
    param = request.form['param']

    if endpoint in ['adsoyad', 'adsoyadilice']:
        try:
            parts = param.strip().split()
            if len(parts) < 2:
                return jsonify({"error": "Ad ve soyad arasında boşluk olmalıdır"}), 400
            ad = parts[0]
            soyad = " ".join(parts[1:])  # Soyad birden fazla kelime olabilir
            url = API_URLS[endpoint](ad, soyad)
        except Exception as e:
            return jsonify({"error": f"Parametre hatası: {str(e)}"}), 400
    else:
        url = API_URLS[endpoint](param, None)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API isteği başarısız: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Genel hata: {str(e)}"}), 500

@app.route('/admin')
@login_required
@admin_required
def admin():
    return render_template_string(BASE_TEMPLATE, 
                                title='Admin Panel - CappyBeamServicesChecks',
                                content=ADMIN_TEMPLATE,
                                scripts='',
                                users=USERS)

@app.route('/toggle_vip/<username>')
@login_required
@admin_required
def toggle_vip(username):
    if username in USERS:
        USERS[username]['is_vip'] = not USERS[username].get('is_vip', False)
        save_users(USERS)
        flash(f"{username} VIP durumu güncellendi!", 'success')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış yapıldı.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Başlangıçta kullanıcı sayısını yazdır
    print(f"Yüklenen kullanıcı sayısı: {len(USERS)}")
    for username in USERS:
        print(f"- {username}")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
