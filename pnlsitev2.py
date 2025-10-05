from flask import Flask, render_template_string, request, session, jsonify
import requests
import json

app = Flask(__name__)
app.secret_key = 'cappychecker2025_secret_key_2025'

VALID_KEYS = ['cappy2025', 'admin123', 'checkerkey']

API_URLS = {
    'tc': 'https://apiservices.alwaysdata.net/diger/tc.php?tc={tc}',
    'tcpro': 'https://apiservices.alwaysdata.net/diger/tcpro.php?tc={tc}',
    'adsoyad': 'https://apiservices.alwaysdata.net/diger/adsoyad.php?ad={ad}&soyad={soyad}',
    'adsoyadpro': 'https://apiservices.alwaysdata.net/diger/adsoyadpro.php?ad={ad}&soyad={soyad}&il={il}&ilce={ilce}',
    'tapu': 'https://apiservices.alwaysdata.net/diger/tapu.php?tc={tc}',
    'tcgsm': 'https://apiservices.alwaysdata.net/diger/tcgsm.php?tc={tc}',
    'gsmtc': 'https://apiservices.alwaysdata.net/diger/gsmtc.php?gsm={gsm}',
    'adres': 'https://apiservices.alwaysdata.net/diger/adres.php?tc={tc}',
    'hane': 'https://apiservices.alwaysdata.net/diger/hane.php?tc={tc}',
    'aile': 'https://apiservices.alwaysdata.net/diger/aile.php?tc={tc}',
    'sulale': 'https://apiservices.alwaysdata.net/diger/sulale.php?tc={tc}'
}

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CappyChecker2025 | Giriş</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        :root {
            --primary-color: #0f0f0f; --secondary-color: #1a1a1a; --accent-color: #dc2626;
            --accent-gradient: linear-gradient(135deg, #dc2626, #ef4444); --text-color: #f0f0f0;
            --text-secondary: #a0a0a0; --border-color: #2a2a2a; --card-bg: rgba(30, 30, 30, 0.7);
            --glow: 0 0 15px rgba(220, 38, 38, 0.3);
        }
        body {
            background-color: var(--primary-color); color: var(--text-color); line-height: 1.7;
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
            background-image: radial-gradient(circle at 10% 20%, rgba(220, 38, 38, 0.05) 0%, transparent 20%),
                            radial-gradient(circle at 90% 60%, rgba(239, 68, 68, 0.05) 0%, transparent 20%);
        }
        .login-container {
            background: var(--card-bg); padding: 40px; border-radius: 16px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(10px); 
            border: 1px solid rgba(255,255,255,0.05); width: 90%; max-width: 400px; text-align: center;
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo-img { width: 100px; height: 100px; border-radius: 50%; margin: 0 auto 15px; overflow: hidden; }
        .logo-img img { width: 100%; height: 100%; object-fit: cover; }
        .logo h1 { background: var(--accent-gradient); -webkit-background-clip: text; background-clip: text; color: transparent; font-size: 24px; font-weight: 800; }
        .logo span { color: var(--text-color); font-size: 14px; margin-top: 5px; opacity: 0.8; }
        .form-group { margin-bottom: 20px; text-align: left; }
        .form-group label { display: block; margin-bottom: 8px; color: var(--text-color); font-weight: 500; }
        .form-group input { width: 100%; padding: 12px 15px; background: var(--primary-color); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-color); font-size: 16px; }
        .btn { padding: 12px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; background: var(--accent-gradient); color: white; font-size: 16px; }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .error { color: #ff6b6b; margin-top: 10px; font-size: 14px; }
        .turnstile-container { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <div class="logo-img">
                <img src="https://www.pngfind.com/pngs/m/332-3329196_haha-facebook-facebook-haha-icon-png-transparent-png.png" alt="CappyChecker2025 Logo">
            </div>
            <h1>CappyChecker2025</h1>
            <span>geliştirilme aşamasındadır!</span>
        </div>
        <form method="POST" action="/login" id="loginForm">
            <div class="form-group">
                <label for="api_key"><i class="fas fa-key"></i> API Anahtarı</label>
                <input type="password" id="api_key" name="api_key" placeholder="API anahtarınızı girin" required>
            </div>
            
            <div class="turnstile-container">
                <div class="cf-turnstile" data-sitekey="1x00000000000000000000AA" data-theme="dark" data-callback="enableLogin"></div>
            </div>
            
            {% if error %}
            <div class="error"><i class="fas fa-exclamation-triangle"></i> {{ error }}</div>
            {% endif %}
            
            <button type="submit" class="btn" id="loginBtn" disabled>
                <i class="fas fa-sign-in-alt"></i> Giriş Yap
            </button>
        </form>
    </div>

    <script>
        function enableLogin() {
            document.getElementById('loginBtn').disabled = false;
        }
    </script>
</body>
</html>
'''

MAIN_HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CappyChecker2025 | TC Sorgu Sistemi</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Poppins', sans-serif; }
        :root {
            --primary-color: #0f0f0f; --secondary-color: #1a1a1a; --accent-color: #dc2626;
            --accent-gradient: linear-gradient(135deg, #dc2626, #ef4444); --text-color: #f0f0f0;
            --text-secondary: #a0a0a0; --border-color: #2a2a2a; --card-bg: rgba(30, 30, 30, 0.7);
            --glow: 0 0 15px rgba(220, 38, 38, 0.3);
        }
        body {
            background-color: var(--primary-color); color: var(--text-color); line-height: 1.7;
            display: flex; min-height: 100vh; 
            background-image: radial-gradient(circle at 10% 20%, rgba(220, 38, 38, 0.05) 0%, transparent 20%),
                            radial-gradient(circle at 90% 60%, rgba(239, 68, 68, 0.05) 0%, transparent 20%);
        }
        .sidebar {
            width: 280px; background-color: rgba(20, 20, 20, 0.9); padding: 30px 20px;
            position: fixed; height: 100vh; overflow-y: auto; border-right: 1px solid var(--border-color);
            backdrop-filter: blur(10px); z-index: 100;
        }
        .logo { text-align: center; margin-bottom: 40px; padding-bottom: 25px; border-bottom: 1px solid var(--border-color); }
        .logo-img { width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 15px; overflow: hidden; }
        .logo-img img { width: 100%; height: 100%; object-fit: cover; }
        .logo h1 { background: var(--accent-gradient); -webkit-background-clip: text; background-clip: text; color: transparent; font-size: 24px; font-weight: 800; }
        .logo span { color: var(--text-color); font-size: 14px; margin-top: 5px; opacity: 0.8; }
        .menu { list-style: none; margin-bottom: 30px; }
        .menu li { margin-bottom: 12px; }
        .menu a { display: flex; align-items: center; padding: 14px 18px; color: var(--text-color); text-decoration: none; border-radius: 10px; transition: all 0.3s ease; font-weight: 500; cursor: pointer; }
        .menu a i { margin-right: 12px; font-size: 18px; width: 24px; text-align: center; }
        .menu a:hover { background: rgba(220, 38, 38, 0.1); color: var(--accent-color); transform: translateX(5px); }
        .menu a.active { background: var(--accent-gradient); color: white; box-shadow: var(--glow); }
        .main-content { flex: 1; margin-left: 280px; padding: 40px; }
        .section { margin-bottom: 50px; background: var(--card-bg); padding: 35px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }
        .section h2 { background: var(--accent-gradient); -webkit-background-clip: text; background-clip: text; color: transparent; margin-bottom: 20px; font-size: 28px; font-weight: 700; }
        .anasayfa-content { color: var(--text-secondary); font-size: 16px; }
        .anasayfa-content p { margin-bottom: 15px; }
        .sorgu-form { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: var(--text-color); font-weight: 500; }
        .form-group input, .form-group select { width: 100%; padding: 12px 15px; background: var(--primary-color); border: 1px solid var(--border-color); border-radius: 8px; color: var(--text-color); font-size: 16px; }
        .btn { padding: 12px 25px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; background: var(--accent-gradient); color: white; font-size: 16px; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .results-container { max-height: 600px; overflow-y: auto; margin-top: 20px; }
        .results-table { width: 100%; border-collapse: collapse; background: var(--secondary-color); border-radius: 8px; overflow: hidden; font-size: 14px; }
        .results-table th { background: var(--accent-gradient); color: white; padding: 12px 8px; text-align: left; font-weight: 600; position: sticky; top: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .results-table td { padding: 10px 8px; border-bottom: 1px solid var(--border-color); color: var(--text-color); font-size: 13px; }
        .results-table tr:hover { background: rgba(255,255,255,0.05); }
        .loading { text-align: center; padding: 20px; color: var(--text-secondary); }
        .error { background: rgba(255,107,107,0.1); color: #ff6b6b; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #ff6b6b; }
        .success { background: rgba(76,175,80,0.1); color: #4CAF50; padding: 15px; border-radius: 8px; margin-top: 20px; border-left: 4px solid #4CAF50; }
        .hidden { display: none; }
        .search-info { background: rgba(255,193,7,0.1); color: #FFC107; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #FFC107; }
        @media (max-width: 768px) {
            .sidebar { width: 100%; height: auto; position: relative; }
            .main-content { margin-left: 0; }
            body { flex-direction: column; }
            .sorgu-form { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <div class="logo-img">
                <img src="https://www.pngfind.com/pngs/m/332-3329196_haha-facebook-facebook-haha-icon-png-transparent-png.png" alt="CappyChecker2025 Logo">
            </div>
            <h1>CappyChecker2025</h1>
            <span>TC Sorgu Sistemi</span>
        </div>
        <ul class="menu">
            <li><a class="active" data-page="anasayfa"><i class="fas fa-home"></i> Ana Sayfa</a></li>
            <li><a data-sorgu="tc" data-page="sorgu"><i class="fas fa-id-card"></i> TC Sorgu</a></li>
            <li><a data-sorgu="tcpro" data-page="sorgu"><i class="fas fa-id-card-alt"></i> TC Pro Sorgu</a></li>
            <li><a data-sorgu="adsoyad" data-page="sorgu"><i class="fas fa-user"></i> Ad Soyad Sorgu</a></li>
            <li><a data-sorgu="adsoyadpro" data-page="sorgu"><i class="fas fa-users"></i> Ad Soyad Pro</a></li>
            <li><a data-sorgu="tapu" data-page="sorgu"><i class="fas fa-home"></i> Tapu Sorgu</a></li>
            <li><a data-sorgu="tcgsm" data-page="sorgu"><i class="fas fa-phone"></i> TC GSM Sorgu</a></li>
            <li><a data-sorgu="gsmtc" data-page="sorgu"><i class="fas fa-mobile-alt"></i> GSM TC Sorgu</a></li>
            <li><a data-sorgu="adres" data-page="sorgu"><i class="fas fa-map-marker-alt"></i> Adres Sorgu</a></li>
            <li><a data-sorgu="hane" data-page="sorgu"><i class="fas fa-house-user"></i> Hane Sorgu</a></li>
            <li><a data-sorgu="aile" data-page="sorgu"><i class="fas fa-heart"></i> Aile Sorgu</a></li>
            <li><a data-sorgu="sulale" data-page="sorgu"><i class="fas fa-sitemap"></i> Sülale Sorgu</a></li>
        </ul>
    </div>

    <div class="main-content">
        <!-- Ana Sayfa -->
        <div class="section" id="anasayfa">
            <h2>Hoş Geldiniz</h2>
            <div class="anasayfa-content">
                <p><strong>CappyChecker2025 TC Sorgu Sistemi'ne hoş geldiniz!</strong></p>
                <p>Bu sistem, güvenli ve hızlı bir şekilde TC kimlik numarası sorgulama işlemleri yapmanızı sağlar.</p>
                <p><strong>Özellikler:</strong></p>
                <ul>
                    <li>TC Kimlik Sorgulama</li>
                    <li>Ad-Soyad Sorgulama</li>
                    <li>GSM Numarası Sorgulama</li>
                    <li>Adres ve Tapu Bilgileri</li>
                    <li>Aile ve Sülale Bilgileri</li>
                    <li>Güvenli Cloudflare Doğrulama</li>
                    <li>1000+ satırlık büyük veri setleri</li>
                </ul>
                <p><strong>Kullanım:</strong> Sol menüden sorgu tipini seçin, gerekli bilgileri girin ve sorgulama yapın.</p>
                <p><em>Not: Tüm sorgular güvenli API'ler üzerinden gerçekleştirilmektedir.</em></p>
            </div>
        </div>

        <!-- Sorgu Sayfası -->
        <div class="section hidden" id="sorgu">
            <h2 id="sorgu-baslik">TC Sorgu</h2>
            
            <div class="search-info" id="searchInfo" style="display: none;">
                <i class="fas fa-info-circle"></i> <span id="infoText"></span>
            </div>
            
            <form id="sorguForm" class="sorgu-form">
                <input type="hidden" id="sorguTipi" name="sorgu_tipi" value="tc">
                
                <div class="form-group" id="tcGroup">
                    <label for="tc"><i class="fas fa-id-card"></i> TC Kimlik No</label>
                    <input type="text" id="tc" name="sorgu_degeri" placeholder="TC kimlik numarasını girin" maxlength="11">
                </div>
                
                <div class="form-group" id="adGroup" style="display:none">
                    <label for="ad"><i class="fas fa-user"></i> Ad</label>
                    <input type="text" id="ad" name="ad" placeholder="Adınızı girin">
                </div>
                
                <div class="form-group" id="soyadGroup" style="display:none">
                    <label for="soyad"><i class="fas fa-user"></i> Soyad</label>
                    <input type="text" id="soyad" name="soyad" placeholder="Soyadınızı girin">
                </div>
                
                <div class="form-group" id="ilGroup" style="display:none">
                    <label for="il"><i class="fas fa-city"></i> İl</label>
                    <input type="text" id="il" name="il" placeholder="İl girin">
                </div>
                
                <div class="form-group" id="ilceGroup" style="display:none">
                    <label for="ilce"><i class="fas fa-building"></i> İlçe</label>
                    <input type="text" id="ilce" name="ilce" placeholder="İlçe girin">
                </div>
                
                <div class="form-group" id="gsmGroup" style="display:none">
                    <label for="gsm"><i class="fas fa-phone"></i> GSM No</label>
                    <input type="text" id="gsm" name="sorgu_degeri" placeholder="GSM numarasını girin">
                </div>
                
                <div class="form-group" style="grid-column:1/-1">
                    <div class="cf-turnstile" data-sitekey="1x00000000000000000000AA" data-theme="dark"></div>
                </div>
                
                <div class="form-group" style="grid-column:1/-1;text-align:center">
                    <button type="submit" class="btn"><i class="fas fa-search"></i> Sorgula</button>
                </div>
            </form>
            
            <div id="sonuclar"></div>
        </div>
    </div>

    <script>
        // Sayfa yönlendirme
        function showPage(pageId) {
            document.getElementById('anasayfa').classList.add('hidden');
            document.getElementById('sorgu').classList.add('hidden');
            document.getElementById(pageId).classList.remove('hidden');
        }

        // Menü tıklama
        document.querySelectorAll('.menu a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.menu a').forEach(item => item.classList.remove('active'));
                this.classList.add('active');
                
                const page = this.getAttribute('data-page');
                if (page === 'sorgu') {
                    const sorguTipi = this.getAttribute('data-sorgu');
                    document.getElementById('sorguTipi').value = sorguTipi;
                    document.getElementById('sorgu-baslik').textContent = this.textContent.trim();
                    updateFormFields(sorguTipi);
                    showPage('sorgu');
                } else {
                    showPage('anasayfa');
                }
            });
        });

        function updateFormFields(sorguTipi) {
            // Tüm alanları gizle
            document.getElementById('tcGroup').style.display = 'none';
            document.getElementById('adGroup').style.display = 'none';
            document.getElementById('soyadGroup').style.display = 'none';
            document.getElementById('ilGroup').style.display = 'none';
            document.getElementById('ilceGroup').style.display = 'none';
            document.getElementById('gsmGroup').style.display = 'none';
            document.getElementById('searchInfo').style.display = 'none';
            
            // Bilgi metnini güncelle
            let infoText = '';
            
            if(['tc','tcpro','tapu','tcgsm','adres','hane','aile','sulale'].includes(sorguTipi)) {
                document.getElementById('tcGroup').style.display = 'block';
                infoText = 'TC kimlik numarası ile sorgulama yapılıyor. 11 haneli numarayı giriniz.';
            } else if(sorguTipi === 'adsoyad') {
                document.getElementById('adGroup').style.display = 'block';
                document.getElementById('soyadGroup').style.display = 'block';
                infoText = 'Ad ve soyad bilgileri ile sorgulama yapılıyor. Örnek: "Ahmet Yılmaz"';
            } else if(sorguTipi === 'adsoyadpro') {
                document.getElementById('adGroup').style.display = 'block';
                document.getElementById('soyadGroup').style.display = 'block';
                document.getElementById('ilGroup').style.display = 'block';
                document.getElementById('ilceGroup').style.display = 'block';
                infoText = 'Ad, soyad, il ve ilçe bilgileri ile detaylı sorgulama yapılıyor.';
            } else if(sorguTipi === 'gsmtc') {
                document.getElementById('gsmGroup').style.display = 'block';
                infoText = 'GSM numarası ile TC kimlik sorgulama yapılıyor.';
            }
            
            // Bilgi metnini göster
            if (infoText) {
                document.getElementById('infoText').textContent = infoText;
                document.getElementById('searchInfo').style.display = 'block';
            }
        }

        // Sorgu formu
        document.getElementById('sorguForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const sorguTipi = document.getElementById('sorguTipi').value;
            
            // Yükleme göster
            document.getElementById('sonuclar').innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i> Sorgu yapılıyor... 
                    <div style="margin-top: 10px; font-size: 14px;">Büyük veri seti yükleniyor, lütfen bekleyin...</div>
                </div>
            `;
            
            fetch('/sorgu', { method: 'POST', body: formData })
            .then(r => {
                if (!r.ok) {
                    throw new Error(`HTTP error! status: ${r.status}`);
                }
                return r.json();
            })
            .then(data => {
    console.log("Ham API Yanıtı:", data);
    const rawData = data.data?.Veri || data.VERI || data.result || data.data || data || [];

    console.log("Çözümlenmiş Veri:", rawData);

    if (data.success && Array.isArray(rawData)) {
        displayResults(rawData, sorguTipi);
    } else {
        document.getElementById('sonuclar').innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i> Veri alınamadı veya sonuç boş.
            </div>`;
    }
})
            .catch(err => {
                console.error('Fetch Error:', err); // Hata logu
                document.getElementById('sonuclar').innerHTML = '<div class="error"><i class="fas fa-exclamation-triangle"></i> Hata: ' + err.message + '</div>';
            });
        });

       function displayResults(dataArray, sorguTipi) {
    let results = [];
    if (dataArray.VERI && Array.isArray(dataArray.VERI)) {
        results = dataArray.VERI; // API 'VERI' dizisi döndürüyorsa
    } else if (Array.isArray(dataArray)) {
        results = dataArray; // Doğrudan dizi döndürüyorsa
    } else if (typeof dataArray === 'object' && dataArray !== null) {
        results = [dataArray]; // Tek bir obje döndürüyorsa diziye çevir
    } else {
        results = []; // Geçersiz veya boş veri
    }

    const resultCount = results.length;
    let html = `<div class="success"><i class="fas fa-check-circle"></i> Sorgu başarılı! Sonuçlar aşağıda listelenmiştir.</div>`;
    html += `<div class="search-info"><i class="fas fa-database"></i> Toplam <strong>${resultCount}</strong> kayıt bulundu</div>`;

    if (resultCount > 0) {
        html += `
            <div class="results-container">
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>TC</th>
                            <th>Adı</th>
                            <th>Soyadı</th>
                            <th>Doğum Tarihi</th>
                            <th>Nüfus İl</th>
                            <th>Nüfus İlçe</th>
                            <th>Anne Adı</th>
                            <th>Anne TC</th>
                            <th>Baba Adı</th>
                            <th>Baba TC</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map(item => `
                            <tr>
                                <td>${item.TCKN || item.TC || item.tckimlikno || '-'}</td>
                                <td>${item.Adi || item.ADI || item.ad || item.isim || '-'}</td>
                                <td>${item.Soyadi || item.SOYADI || item.soyad || item.soyisim || '-'}</td>
                                <td>${item.DogumTarihi || item.DOGUM_TARIHI || item.dogumtarihi || '-'}</td>
                                <td>${item.NufusIl || item.NUFUS_IL || item.il || item.sehir || '-'}</td>
                                <td>${item.NufusIlce || item.NUFUS_ILCE || item.ilce || '-'}</td>
                                <td>${item.AnneAdi || item.ANNE_ADI || item.anneadi || '-'}</td>
                                <td>${item.AnneTCKN || item.ANNE_TC || item.annetc || '-'}</td>
                                <td>${item.BabaAdi || item.BABA_ADI || item.babaadi || '-'}</td>
                                <td>${item.BabaTCKN || item.BABA_TC || item.babatc || '-'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } else {
        html += '<div class="error">Sonuç bulunamadı</div>';
    }

    document.getElementById("sonuclar").innerHTML = html;
}

        function getHeadersForQueryType(sorguTipi) {
            const headerMap = {
                'tc': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'NÜFUS İL', 'NÜFUS İLÇE', 'ANNE ADI', 'ANNE TC', 'BABA ADI'],
                'tcpro': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'NÜFUS İL', 'NÜFUS İLÇE', 'ANNE ADI', 'ANNE TC', 'BABA ADI'],
                'adsoyad': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'NÜFUS İL', 'NÜFUS İLÇE', 'ANNE ADI', 'ANNE TC', 'BABA ADI'],
                'adsoyadpro': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'NÜFUS İL', 'NÜFUS İLÇE', 'ANNE ADI', 'ANNE TC', 'BABA ADI'],
                'tapu': ['TC', 'ADA', 'PARSEL', 'MAHALLE', 'İL', 'İLÇE', 'TAPU TÜRÜ'],
                'tcgsm': ['TC', 'GSM', 'OPERATÖR', 'ADI', 'SOYADI'],
                'gsmtc': ['GSM', 'TC', 'OPERATÖR', 'ADI', 'SOYADI'],
                'adres': ['TC', 'ADRES', 'İL', 'İLÇE', 'MAHALLE', 'POSTA KODU'],
                'hane': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'AKRABA TC', 'AKRABA ADI', 'YAKINLIK'],
                'aile': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'ANNE ADI', 'BABA ADI', 'KARDEŞ SAYISI'],
                'sulale': ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI', 'SÜLALE ADI', 'SÜLALE BÜYÜĞÜ']
            };
            return headerMap[sorguTipi] || ['TC', 'ADI', 'SOYADI', 'DOĞUM TARIHI'];
        }

        function getValuesForQueryType(item, sorguTipi) {
            // API yanıtından değerleri esnek bir şekilde al
            const tc = item.TC || item.tc || item.TCKimlikNo || item.tckimlikno || '-';
            const adi = item.ADI || item.adi || item.AD || item.ad || item.isim || '-';
            const soyadi = item.SOYADI || item.soyadi || item.SOYAD || item.soyad || item.soyisim || '-';
            const dogumTarihi = item.DOGUM_TARIHI || item.dogum_tarihi || item.DOGUMTARIHI || item.dogumtarihi || '-';
            const nufusIl = item.NUFUS_IL || item.nufus_il || item.IL || item.il || item.sehir || '-';
            const nufusIlce = item.NUFUS_ILCE || item.nufus_ilce || item.ILCE || item.ilce || '-';
            const anneAdi = item.ANNE_ADI || item.anne_adi || item.ANNEADI || item.anneadi || '-';
            const anneTc = item.ANNE_TC || item.anne_tc || item.ANNETC || item.annetc || '-';
            const babaAdi = item.BABA_ADI || item.baba_adi || item.BABAADI || item.babaadi || '-';
            const gsm = item.GSM || item.gsm || item.TELEFON || item.telefon || '-';
            const operator = item.OPERATOR || item.operator || item.OPERATÖR || item.operator || '-';
            const adres = item.ADRES || item.adres || item.ADDRESS || item.address || '-';
            const postaKodu = item.POSTA_KODU || item.posta_kodu || item.POSTAKODU || item.postakodu || '-';
            const ada = item.ADA || item.ada || item.ADA_NO || item.ada_no || '-';
            const parsel = item.PARSEL || item.parsel || item.PARSEL_NO || item.parsel_no || '-';
            const mahalle = item.MAHALLE || item.mahalle || item.MAHALLE_ADI || item.mahalle_adi || '-';
            const tapuTuru = item.TAPU_TURU || item.tapu_turu || item.TAPUTURU || item.taputuru || '-';
            const akrabaTc = item.AKRABA_TC || item.akraba_tc || item.AKRABATC || item.akrabatc || '-';
            const akrabaAdi = item.AKRABA_ADI || item.akraba_adi || item.AKRABAAD || item.akrabaad || '-';
            const yakinlik = item.YAKINLIK || item.yakinlik || '-';
            const kardesSayisi = item.KARDES_SAYISI || item.kardes_sayisi || item.KARDESSAYISI || item.kardessayisi || '-';
            const sulaleAdi = item.SULALE_ADI || item.sulale_adi || item.SULALEADI || item.sulaleadi || '-';
            const sulaleBuyugu = item.SULALE_BUYUGU || item.sulale_buyugu || item.SULALEBUYUGU || item.sulalebuyugu || '-';

            const valueMap = {
                'tc': [tc, adi, soyadi, dogumTarihi, nufusIl, nufusIlce, anneAdi, anneTc, babaAdi],
                'tcpro': [tc, adi, soyadi, dogumTarihi, nufusIl, nufusIlce, anneAdi, anneTc, babaAdi],
                'adsoyad': [tc, adi, soyadi, dogumTarihi, nufusIl, nufusIlce, anneAdi, anneTc, babaAdi],
                'adsoyadpro': [tc, adi, soyadi, dogumTarihi, nufusIl, nufusIlce, anneAdi, anneTc, babaAdi],
                'tapu': [tc, ada, parsel, mahalle, nufusIl, nufusIlce, tapuTuru],
                'tcgsm': [tc, gsm, operator, adi, soyadi],
                'gsmtc': [gsm, tc, operator, adi, soyadi],
                'adres': [tc, adres, nufusIl, nufusIlce, mahalle, postaKodu],
                'hane': [tc, adi, soyadi, dogumTarihi, akrabaTc, akrabaAdi, yakinlik],
                'aile': [tc, adi, soyadi, dogumTarihi, anneAdi, babaAdi, kardesSayisi],
                'sulale': [tc, adi, soyadi, dogumTarihi, sulaleAdi, sulaleBuyugu]
            };
            
            return valueMap[sorguTipi] || [tc, adi, soyadi, dogumTarihi];
        }

        // İlk yüklemede ana sayfayı göster
        showPage('anasayfa');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'api_key' in session and session['api_key'] in VALID_KEYS:
        return render_template_string(MAIN_HTML)
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    api_key = request.form.get('api_key')
    if api_key in VALID_KEYS:
        session['api_key'] = api_key
        return render_template_string(MAIN_HTML)
    return render_template_string(LOGIN_HTML, error='Geçersiz API anahtarı!')

@app.route('/sorgu', methods=['POST'])
def sorgu():
    if 'api_key' not in session or session['api_key'] not in VALID_KEYS:
        return jsonify({'error': 'Yetkisiz erişim!'})
    
    sorgu_tipi = request.form.get('sorgu_tipi')
    sorgu_degeri = request.form.get('sorgu_degeri', '').strip()
    
    # TC kimlik numarası gereken sorgular için validasyon
    if sorgu_tipi in ['tc', 'tcpro', 'tapu', 'tcgsm', 'adres', 'hane', 'aile', 'sulale']:
        if len(sorgu_degeri) != 11 or not sorgu_degeri.isdigit():
            return jsonify({'error': 'TC kimlik numarası 11 haneli ve sadece rakamlardan oluşmalıdır.'})
    
    try:
        if sorgu_tipi in ['tc', 'tcpro', 'tapu', 'tcgsm', 'adres', 'hane', 'aile', 'sulale']:
            url = API_URLS[sorgu_tipi] + sorgu_degeri
        elif sorgu_tipi == 'adsoyad':
            ad = request.form.get('ad', '').strip()
            soyad = request.form.get('soyad', '').strip()
            if not ad or not soyad:
                return jsonify({'error': 'Ad ve soyad alanları boş olamaz.'})
            url = API_URLS[sorgu_tipi].format(ad=ad, soyad=soyad)
        elif sorgu_tipi == 'adsoyadpro':
            ad = request.form.get('ad', '').strip()
            soyad = request.form.get('soyad', '').strip()
            il = request.form.get('il', '').strip()
            ilce = request.form.get('ilce', '').strip()
            if not ad or not soyad:
                return jsonify({'error': 'Ad ve soyad alanları boş olamaz.'})
            url = API_URLS[sorgu_tipi].format(ad=ad, soyad=soyad, il=il, ilce=ilce)
        elif sorgu_tipi == 'gsmtc':
            if not sorgu_degeri:
                return jsonify({'error': 'GSM numarası boş olamaz.'})
            url = API_URLS[sorgu_tipi] + sorgu_degeri
        else:
            return jsonify({'error': 'Geçersiz sorgu tipi!'})
        
        print(f"Requesting URL: {url}")  # Hangi URL'ye istek atıldığını logla
        
        # API isteği ve detaylı loglama
        response = requests.get(url, timeout=30)
        print(f"Response Status Code: {response.status_code}")
        print(f"Raw Response Text: {response.text}")  # Ham yanıtı logla
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Parsed JSON Data: {json.dumps(data, ensure_ascii=False, indent=2)}")  # JSON'u okunabilir şekilde logla
                if not data:
                    return jsonify({'error': 'API boş yanıt döndü. Veri bulunamadı.'})
                return jsonify({'success': True, 'data': data})
            except ValueError as e:
                print(f"JSON Parse Error: {e}")
                return jsonify({'error': 'API yanıtı JSON formatında değil.'})
        else:
            return jsonify({'error': f'API hatası: {response.status_code} - {response.text}'})
    except requests.RequestException as e:
        print(f"Network Error: {str(e)}")
        return jsonify({'error': f'Ağ hatası: {str(e)}'})
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return jsonify({'error': f'Sorgu hatası: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
