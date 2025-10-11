from flask import Flask, render_template_string, request, session, jsonify
import requests
import json
import random
from datetime import datetime, timedelta

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

# İstatistik verilerini saklamak için basit bir yapı
stats = {
    'active_users': 0,
    'registered_accounts': len(VALID_KEYS),
    'total_queries': 0,
    'successful_queries': 0,
    'failed_queries': 0,
    'query_history': []
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
    <title>CappyChecker2025</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
        .dashboard-content { color: var(--text-secondary); font-size: 16px; }
        .dashboard-content p { margin-bottom: 15px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: var(--secondary-color); padding: 25px; border-radius: 12px; text-align: center; border-left: 4px solid var(--accent-color); }
        .stat-card i { font-size: 32px; margin-bottom: 15px; color: var(--accent-color); }
        .stat-card h3 { font-size: 14px; color: var(--text-secondary); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .stat-card .value { font-size: 32px; font-weight: 700; color: var(--text-color); }
        .stat-card .change { font-size: 14px; margin-top: 5px; }
        .change.positive { color: #4CAF50; }
        .change.negative { color: #f44336; }
        .charts-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }
        .chart-card { background: var(--secondary-color); padding: 25px; border-radius: 12px; }
        .chart-card h3 { margin-bottom: 15px; color: var(--text-color); font-size: 18px; }
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
            .charts-container { grid-template-columns: 1fr; }
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
            <span>geliştirilme aşamasındadır!</span>
        </div>
        <ul class="menu">
            <li><a class="active" data-page="dashboard"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
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
        <!-- Dashboard -->
        <div class="section" id="dashboard">
            <h2>Dashboard</h2>
            <div class="dashboard-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <i class="fas fa-users"></i>
                        <h3>Aktif Kullanıcılar</h3>
                        <div class="value" id="activeUsers">0</div>
                        <div class="change positive" id="activeUsersChange">+0 bugün</div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-user-plus"></i>
                        <h3>Kayıtlı Hesaplar</h3>
                        <div class="value" id="registeredAccounts">0</div>
                        <div class="change positive" id="registeredAccountsChange">+0 bu ay</div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-search"></i>
                        <h3>Toplam Sorgu</h3>
                        <div class="value" id="totalQueries">0</div>
                        <div class="change positive" id="totalQueriesChange">+0 bugün</div>
                    </div>
                    <div class="stat-card">
                        <i class="fas fa-chart-line"></i>
                        <h3>Başarı Oranı</h3>
                        <div class="value" id="successRate">0%</div>
                        <div class="change positive" id="successRateChange">+0%</div>
                    </div>
                </div>
                
                <div class="charts-container">
                    <div class="chart-card">
                        <h3>Sorgu İstatistikleri</h3>
                        <canvas id="queryChart"></canvas>
                    </div>
                    <div class="chart-card">
                        <h3>Sorgu Türleri</h3>
                        <canvas id="queryTypeChart"></canvas>
                    </div>
                </div>
                
                <div style="margin-top: 30px;">
                    <h3 style="margin-bottom: 15px; color: var(--text-color);">Son Sorgular</h3>
                    <div class="results-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>Tarih</th>
                                    <th>Sorgu Türü</th>
                                    <th>Kullanıcı</th>
                                    <th>Sonuç</th>
                                    <th>Süre</th>
                                </tr>
                            </thead>
                            <tbody id="recentQueries">
                                <!-- Son sorgular buraya eklenecek -->
                            </tbody>
                        </table>
                    </div>
                </div>
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
            document.getElementById('dashboard').classList.add('hidden');
            document.getElementById('sorgu').classList.add('hidden');
            document.getElementById(pageId).classList.remove('hidden');
            
            if (pageId === 'dashboard') {
                updateDashboard();
            }
        }

        // Dashboard verilerini güncelle
        function updateDashboard() {
            // API'den istatistikleri al (şimdilik mock veri kullanıyoruz)
            const mockData = {
                active_users: {{ stats.active_users }},
                registered_accounts: {{ stats.registered_accounts }},
                total_queries: {{ stats.total_queries }},
                successful_queries: {{ stats.successful_queries }},
                failed_queries: {{ stats.failed_queries }},
                query_history: {{ stats.query_history|tojson }}
            };
            
            // İstatistikleri güncelle
            document.getElementById('activeUsers').textContent = mockData.active_users;
            document.getElementById('registeredAccounts').textContent = mockData.registered_accounts;
            document.getElementById('totalQueries').textContent = mockData.total_queries;
            
            const successRate = mockData.total_queries > 0 ? 
                Math.round((mockData.successful_queries / mockData.total_queries) * 100) : 0;
            document.getElementById('successRate').textContent = successRate + '%';
            
            // Grafikleri oluştur
            createCharts(mockData);
            updateRecentQueries(mockData.query_history);
        }
        
        // Grafikleri oluştur
        function createCharts(data) {
            // Sorgu istatistikleri grafiği
            const queryCtx = document.getElementById('queryChart').getContext('2d');
            new Chart(queryCtx, {
                type: 'line',
                data: {
                    labels: ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'],
                    datasets: [{
                        label: 'Başarılı Sorgular',
                        data: [12, 19, 8, 15, 12, 18, 14],
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Başarısız Sorgular',
                        data: [2, 3, 1, 2, 1, 2, 1],
                        borderColor: '#f44336',
                        backgroundColor: 'rgba(244, 67, 54, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '7 Günlük Sorgu Geçmişi'
                        }
                    }
                }
            });
            
            // Sorgu türleri grafiği
            const typeCtx = document.getElementById('queryTypeChart').getContext('2d');
            new Chart(typeCtx, {
                type: 'doughnut',
                data: {
                    labels: ['TC Sorgu', 'TC Pro', 'Ad Soyad', 'Ad Soyad Pro', 'Diğer'],
                    datasets: [{
                        data: [35, 25, 15, 10, 15],
                        backgroundColor: [
                            '#dc2626',
                            '#ef4444',
                            '#f87171',
                            '#fca5a5',
                            '#fecaca'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        }
        
        // Son sorguları güncelle
        function updateRecentQueries(queries) {
            const tbody = document.getElementById('recentQueries');
            if (queries.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Henüz sorgu yapılmamış</td></tr>';
                return;
            }
            
            tbody.innerHTML = queries.map(query => `
                <tr>
                    <td>${query.date}</td>
                    <td>${query.type}</td>
                    <td>${query.user}</td>
                    <td><span class="${query.success ? 'success' : 'error'}" style="padding: 5px 10px; border-radius: 4px; font-size: 12px;">
                        ${query.success ? 'Başarılı' : 'Başarısız'}
                    </span></td>
                    <td>${query.duration}ms</td>
                </tr>
            `).join('');
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
                    showPage('dashboard');
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
                console.error('Fetch Error:', err);
                document.getElementById('sonuclar').innerHTML = '<div class="error"><i class="fas fa-exclamation-triangle"></i> Hata: ' + err.message + '</div>';
            });
        });

        function displayResults(dataArray, sorguTipi) {
            let results = [];
            if (dataArray.VERI && Array.isArray(dataArray.VERI)) {
                results = dataArray.VERI;
            } else if (Array.isArray(dataArray)) {
                results = dataArray;
            } else if (typeof dataArray === 'object' && dataArray !== null) {
                results = [dataArray];
            } else {
                results = [];
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

        // İlk yüklemede dashboard'u göster
        showPage('dashboard');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'api_key' in session and session['api_key'] in VALID_KEYS:
        # Aktif kullanıcı sayısını güncelle (basit bir yaklaşım)
        stats['active_users'] = random.randint(5, 15)
        return render_template_string(MAIN_HTML, stats=stats)
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['POST'])
def login():
    api_key = request.form.get('api_key')
    if api_key in VALID_KEYS:
        session['api_key'] = api_key
        # İstatistikleri güncelle
        stats['active_users'] = random.randint(5, 15)
        return render_template_string(MAIN_HTML, stats=stats)
    return render_template_string(LOGIN_HTML, error='Geçersiz API anahtarı!')

@app.route('/sorgu', methods=['POST'])
def sorgu():
    if 'api_key' not in session or session['api_key'] not in VALID_KEYS:
        return jsonify({'error': 'Yetkisiz erişim!'})
    
    sorgu_tipi = request.form.get('sorgu_tipi')
    sorgu_degeri = request.form.get('sorgu_degeri', '').strip()
    
    # İstatistikleri güncelle
    stats['total_queries'] += 1
    
    # TC kimlik numarası gereken sorgular için validasyon
    if sorgu_tipi in ['tc', 'tcpro', 'tapu', 'tcgsm', 'adres', 'hane', 'aile', 'sulale']:
        if len(sorgu_degeri) != 11 or not sorgu_degeri.isdigit():
            stats['failed_queries'] += 1
            return jsonify({'error': 'TC kimlik numarası 11 haneli ve sadece rakamlardan oluşmalıdır.'})
    
    try:
        if sorgu_tipi in ['tc', 'tcpro', 'tapu', 'tcgsm', 'adres', 'hane', 'aile', 'sulale']:
            url = API_URLS[sorgu_tipi].format(tc=sorgu_degeri)
        elif sorgu_tipi == 'adsoyad':
            ad = request.form.get('ad', '').strip()
            soyad = request.form.get('soyad', '').strip()
            if not ad or not soyad:
                stats['failed_queries'] += 1
                return jsonify({'error': 'Ad ve soyad alanları boş olamaz.'})
            url = API_URLS[sorgu_tipi].format(ad=ad, soyad=soyad)
        elif sorgu_tipi == 'adsoyadpro':
            ad = request.form.get('ad', '').strip()
            soyad = request.form.get('soyad', '').strip()
            il = request.form.get('il', '').strip()
            ilce = request.form.get('ilce', '').strip()
            if not ad or not soyad:
                stats['failed_queries'] += 1
                return jsonify({'error': 'Ad ve soyad alanları boş olamaz.'})
            url = API_URLS[sorgu_tipi].format(ad=ad, soyad=soyad, il=il, ilce=ilce)
        elif sorgu_tipi == 'gsmtc':
            if not sorgu_degeri:
                stats['failed_queries'] += 1
                return jsonify({'error': 'GSM numarası boş olamaz.'})
            url = API_URLS[sorgu_tipi].format(gsm=sorgu_degeri)
        else:
            stats['failed_queries'] += 1
            return jsonify({'error': 'Geçersiz sorgu tipi!'})
        
        print(f"Requesting URL: {url}")
        
        # API isteği
        response = requests.get(url, timeout=30)
        print(f"Response Status Code: {response.status_code}")
        print(f"Raw Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Parsed JSON Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
                
                # Sorgu geçmişine ekle
                query_record = {
                    'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
                    'type': sorgu_tipi,
                    'user': session['api_key'][:3] + '***',  # Kullanıcı adını gizle
                    'success': True,
                    'duration': random.randint(100, 500)
                }
                stats['query_history'].insert(0, query_record)
                stats['query_history'] = stats['query_history'][:10]  # Son 10 kaydı tut
                
                stats['successful_queries'] += 1
                
                if not data:
                    return jsonify({'error': 'API boş yanıt döndü. Veri bulunamadı.'})
                return jsonify({'success': True, 'data': data})
            except ValueError as e:
                print(f"JSON Parse Error: {e}")
                stats['failed_queries'] += 1
                return jsonify({'error': 'API yanıtı JSON formatında değil.'})
        else:
            stats['failed_queries'] += 1
            return jsonify({'error': f'API hatası: {response.status_code} - {response.text}'})
    except requests.RequestException as e:
        print(f"Network Error: {str(e)}")
        stats['failed_queries'] += 1
        return jsonify({'error': f'Ağ hatası: {str(e)}'})
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        stats['failed_queries'] += 1
        return jsonify({'error': f'Sorgu hatası: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
