from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import json
import base64

app = Flask(__name__)
app.secret_key = "cappybeam_secret_key_1234"

# API endpointleri
API_URLS = {
    "adsoyad": lambda ad, soyad: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}",
    "adsoyadil": lambda ad, soyad_il: f"https://api.hexnox.pro/sowixapi/adsoyadilice.php?ad={ad}&soyad={soyad}&il={il}={soyad_il.split(' ')[0] if soyad_il else ''}&il={soyad_il.split(' ')[1] if soyad_il and ' ' in soyad_il else ''}",
    "tcpro": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcpro.php?tc={tc}",
    "tcgsm": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tcgsm.php?tc={tc}",
    "tapu": lambda tc, _: f"https://api.hexnox.pro/sowixapi/tapu.php?tc={tc}",
    "sulale": lambda tc, _: f"https://api.hexnox.pro/sowixapi/sulale.php?tc={tc}",
    "okulno": lambda tc, _: f"https://api.hexnox.pro/sowixapi/okulno.php?tc={tc}",
    "isyeriyetkili": lambda tc, _: f"https://api.hexnox.pro/sowixapi/isyeriyetkili.php?tc={tc}",
    "gsmdetay": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsmdetay.php?gsm={gsm}",
    "gsm": lambda gsm, _: f"https://api.hexnox.pro/sowixapi/gsm.php?gsm={gsm}",
    "adres": lambda tc, _: f"https://api.hexnox.pro/sowixapi/adres.php?tc={tc}",
}

USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# LOGO BASE64 (örnek, ufak bir icon gibi)
LOGO_BASE64 = (
    "file:///C:/Users/maymu/OneDrive/Desktop/CappyBeamServicesiz.png"
)

# ---------- TEMPLATE ----------

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CappyBeamServices - Giriş</title>
<style>
  body {
    margin:0; background:#121212; color:#eee; font-family: Arial, sans-serif;
    display:flex; justify-content:center; align-items:center; height:100vh;
  }
  .login-box {
    background:#1f1f1f; padding:30px 40px; border-radius:10px;
    box-shadow: 0 0 15px #66aaffaa;
    width:320px;
    text-align:center;
  }
  h1 {
    color:#66aaff;
    margin-bottom:20px;
    font-size:26px;
    letter-spacing:2px;
    display:flex; justify-content:center; align-items:center;
  }
  h1 img {
    width:24px; height:24px; margin-right:8px;
  }
  input[type=text], input[type=password] {
    width:100%; padding:10px; margin:12px 0; border:none; border-radius:5px;
    font-size:16px;
    background:#2b2b2b; color:#eee;
  }
  button {
    width:100%; padding:10px; background:#66aaff; border:none;
    border-radius:5px; font-weight:700; font-size:18px; color:#121212;
    cursor:pointer; transition: background 0.3s ease;
  }
  button:hover {
    background:#5599dd;
  }
  .error {
    color:#ff5555; margin-top:10px; font-weight:700;
  }
  a {
    color:#66aaff; font-size:14px; text-decoration:none;
    display:block; margin-top:15px;
  }
  a:hover {
    text-decoration:underline;
  }
</style>
</head>
<body>
  <div class="login-box">
    <h1><img src="file:///C:/Users/maymu/OneDrive/Desktop/CappyBeamServicesiz.png,{{logo}}" alt="logo" /> CappyBeamServices</h1>
    <form method="POST" action="{{ url_for('login_page') }}">
      <input type="text" name="username" placeholder="Kullanıcı Adı" required />
      <input type="password" name="password" placeholder="Şifre" required />
      <button type="submit">Giriş Yap</button>
    </form>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <a href="{{ url_for('register_page') }}">Kayıt Ol</a>
  </div>
</body>
</html>
"""

REGISTER_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CappyBeamServices - Kayıt Ol</title>
<style>
  body {
    margin:0; background:#121212; color:#eee; font-family: Arial, sans-serif;
    display:flex; justify-content:center; align-items:center; height:100vh;
  }
  .register-box {
    background:#1f1f1f; padding:30px 40px; border-radius:10px;
    box-shadow: 0 0 15px #66aaffaa;
    width:320px;
    text-align:center;
  }
  h1 {
    color:#66aaff;
    margin-bottom:20px;
    font-size:26px;
    letter-spacing:2px;
    display:flex; justify-content:center; align-items:center;
  }
  h1 img {
    width:24px; height:24px; margin-right:8px;
  }
  input[type=text], input[type=password] {
    width:100%; padding:10px; margin:12px 0; border:none; border-radius:5px;
    font-size:16px;
    background:#2b2b2b; color:#eee;
  }
  button {
    width:100%; padding:10px; background:#66aaff; border:none;
    border-radius:5px; font-weight:700; font-size:18px; color:#121212;
    cursor:pointer; transition: background 0.3s ease;
  }
  button:hover {
    background:#5599dd;
  }
  .error {
    color:#ff5555; margin-top:10px; font-weight:700;
  }
  a {
    color:#66aaff; font-size:14px; text-decoration:none;
    display:block; margin-top:15px;
  }
  a:hover {
    text-decoration:underline;
  }
</style>
</head>
<body>
  <div class="register-box">
    <h1><img src="file:///C:/Users/maymu/OneDrive/Desktop/CappyBeamServicesiz.png,{{logo}}" alt="logo" /> CappyBeamServices</h1>
    <form method="POST" action="{{ url_for('register_page') }}">
      <input type="text" name="username" placeholder="Kullanıcı Adı" required />
      <input type="password" name="password" placeholder="Şifre (min 4 karakter)" required />
      <button type="submit">Kayıt Ol</button>
    </form>
    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}
    <a href="{{ url_for('login_page') }}">Giriş Yap</a>
  </div>
</body>
</html>
"""

MAIN_PAGE = """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>CappyBeamServices</title>
<style>
  /* Genel düzen */
  body {
    margin: 0;
    background: #121212;
    color: #eee;
    font-family: Arial, sans-serif;
  }
  /* Header ve logo */
  header {
    background: #1f1f1f;
    height: 50px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    font-weight: bold;
    font-size: 18px;
    letter-spacing: 2px;
    color: #66aaff;
  }
  header img {
    height: 30px;
    margin-right: 10px;
  }
  /* Layout */
  #container {
    display: flex;
    height: calc(100vh - 50px);
  }
  /* Sidebar menu */
  #sidebar {
    background: #1f1f1f;
    width: 230px;
    min-width: 230px;
    transition: width 0.3s ease;
    overflow-y: auto;
    flex-shrink: 0;
  }
  #sidebar.open {
    width: 60px;
  }
  #sidebar nav button {
    display: flex;
    align-items: center;
    width: 100%;
    background: none;
    border: none;
    color: #eee;
    padding: 12px 15px;
    text-align: left;
    cursor: pointer;
    font-size: 14px;
    border-left: 4px solid transparent;
    transition: background 0.2s, border-color 0.2s;
  }
  #sidebar nav button:hover,
  #sidebar nav button.active {
    background: #66aaff;
    color: #121212;
    border-left-color: #5599dd;
  }
  #sidebar nav button span {
    margin-left: 10px;
  }
  #sidebar nav #menu-logo {
    font-weight: 900;
    font-size: 16px;
    padding: 15px 15px 10px 15px;
    color: #66aaff;
    white-space: nowrap;
  }
  /* Burger menü (mobil için) */
  #burger {
    display: none;
    position: absolute;
    top: 10px;
    left: 10px;
    width: 30px;
    height: 25px;
    flex-direction: column;
    justify-content: space-between;
    cursor: pointer;
  }
  #burger div {
    width: 100%;
    height: 4px;
    background: #66aaff;
    border-radius: 2px;
  }
  @media (max-width: 768px) {
    #sidebar {
      position: fixed;
      left: -230px;
      height: 100vh;
      z-index: 10;
      width: 230px;
    }
    #sidebar.open {
      left: 0;
    }
    #burger {
      display: flex;
    }
    #container {
      flex-direction: column;
      height: auto;
    }
  }
  /* İçerik */
  #content {
    flex-grow: 1;
    padding: 20px;
    overflow-y: auto;
  }
  /* Sectionlar gizli */
  section {
    display: none;
  }
  section.active {
    display: block;
  }
  /* Form alanları */
  form input[type=text] {
    width: 220px;
    max-width: 100%;
    padding: 8px;
    margin-right: 10px;
    border-radius: 5px;
    border: none;
    font-size: 15px;
    background: #2b2b2b;
    color: #eee;
  }
  form button.submit-btn {
    padding: 9px 18px;
    font-weight: 700;
    background: #66aaff;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    color: #121212;
    font-size: 15px;
    transition: background 0.3s ease;
  }
  form button.submit-btn:hover {
    background: #5599dd;
  }
  /* Sonuç kutuları */
  .result-box {
    margin-top: 12px;
    background: #222;
    padding: 15px;
    border-radius: 8px;
    max-height: 350px;
    overflow-y: auto;
    font-size: 14px;
  }
  /* Listeleme stili */
  ul, li {
    list-style: none;
    padding-left: 0;
    margin: 3px 0;
  }
  ul ul {
    padding-left: 15px;
    border-left: 1px solid #444;
  }
  /* Küçük logo sidebar üstte */
  #sidebar-logo {
    display: flex;
    align-items: center;
    padding: 15px;
    justify-content: center;
  }
  #sidebar-logo img {
    height: 28px;
  }
  /* Hoşgeldin sayfası */
  #hosgeldin {
    text-align: center;
    font-size: 18px;
    margin-top: 120px;
    color: #999;
  }
</style>
</head>
<body>
<header>
  <img src="file:///C:/Users/maymu/OneDrive/Desktop/CappyBeamServicesiz.png,{{logo}}" alt="Logo" />
  <div>CappyBeamServices</div>
</header>

<div id="burger" onclick="toggleMenu()">
  <div></div><div></div><div></div>
</div>

<div id="container">
  <aside id="sidebar">
    <div id="sidebar-logo"><img src="file:///C:/Users/maymu/OneDrive/Desktop/CappyBeamServicesiz.png,{{logo}}" alt="Logo" /></div>
    <nav>
      <button id="btn-hosgeldin" onclick="showSection('hosgeldin')" class="active">Hoşgeldin</button>
      <button id="btn-tcpro" onclick="showSection('tcpro')">TC Pro Sorgu</button>
      <button id="btn-adsoyadilice" onclick="showSection('adsoyadilice')">Ad Soyad İl İlçe</button>
      <button id="btn-tcgsm" onclick="showSection('tcgsm')">TC GSM Sorgu</button>
      <button id="btn-tapu" onclick="showSection('tapu')">Tapu Sorgu</button>
      <button id="btn-sulale" onclick="showSection('sulale')">Sülale Sorgu</button>
      <button id="btn-okulno" onclick="showSection('okulno')">Okul No Sorgu</button>
      <button id="btn-isyeriyetkili" onclick="showSection('isyeriyetkili')">İşyeri Yetkili Sorgu</button>
      <button id="btn-gsmdetay" onclick="showSection('gsmdetay')">GSM Detay Sorgu</button>
      <button id="btn-gsm" onclick="showSection('gsm')">GSM Sorgu</button>
      <button id="btn-adres" onclick="showSection('adres')">Adres Sorgu</button>
      <form method="POST" action="{{ url_for('logout') }}" style="margin:15px;">
        <button type="submit" style="width:100%; background:#ff5555; color:#fff; border:none; padding:10px; border-radius:6px; font-weight:bold; cursor:pointer;">Çıkış Yap</button>
      </form>
    </nav>
  </aside>
  
  <main id="content">
    <section id="hosgeldin" class="active">
      <h2>Hoşgeldiniz</h2>
      <p>CAPPYBEAMSERVİCES'E HOŞGELDİNİZ SORGULARINIZI GÜVENLİ BİR ŞEKİLDE YAPABİLİRSİNİZ.</p>
      <p>Başarılar!</p>
    </section>

    <!-- TC Pro -->
    <section id="tcpro">
      <h2>TC Pro Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('tcpro');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="tcpro-result" class="result-box"></div>
    </section>

    <!-- Ad Soyad İl İlçe -->
    <section id="adsoyadilice">
      <h2>Ad Soyad İl İlçe Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('adsoyadilice');">
        <input type="text" name="ad" placeholder="Ad" required />
        <input type="text" name="soyad" placeholder="Soyad" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="adsoyadilice-result" class="result-box"></div>
    </section>

    <!-- TC GSM -->
    <section id="tcgsm">
      <h2>TC GSM Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('tcgsm');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="tcgsm-result" class="result-box"></div>
    </section>

    <!-- Tapu -->
    <section id="tapu">
      <h2>Tapu Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('tapu');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="tapu-result" class="result-box"></div>
    </section>

    <!-- Sülale -->
    <section id="sulale">
      <h2>Sülale Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('sulale');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="sulale-result" class="result-box"></div>
    </section>

    <!-- Okul No -->
    <section id="okulno">
      <h2>Okul No Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('okulno');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="okulno-result" class="result-box"></div>
    </section>

    <!-- İşyeri Yetkili -->
    <section id="isyeriyetkili">
      <h2>İşyeri Yetkili Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('isyeriyetkili');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="isyeriyetkili-result" class="result-box"></div>
    </section>

    <!-- GSM Detay -->
    <section id="gsmdetay">
      <h2>GSM Detay Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('gsmdetay');">
        <input type="text" name="gsm" placeholder="GSM Numarası" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="gsmdetay-result" class="result-box"></div>
    </section>

    <!-- GSM -->
    <section id="gsm">
      <h2>GSM Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('gsm');">
        <input type="text" name="gsm" placeholder="GSM Numarası" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="gsm-result" class="result-box"></div>
    </section>

    <!-- Adres -->
    <section id="adres">
      <h2>Adres Sorgu</h2>
      <form onsubmit="event.preventDefault(); submitForm('adres');">
        <input type="text" name="tc" placeholder="TC Kimlik No" maxlength="11" required />
        <button class="submit-btn" type="submit">Sorgula</button>
      </form>
      <div id="adres-result" class="result-box"></div>
    </section>
  </main>
</div>

<script>
  // Menü toggle (burger)
  const sidebar = document.getElementById("sidebar");
  const burger = document.getElementById("burger");
  function toggleMenu() {
    sidebar.classList.toggle("open");
  }
  burger.onclick = toggleMenu;

  // Menü butonları ile sayfa değiştirme
  const buttons = document.querySelectorAll("#sidebar nav button");
  const sections = document.querySelectorAll("#content section");

  function showSection(id){
    sections.forEach(s => {
      s.classList.remove("active");
      s.style.display = "none";
    });
    buttons.forEach(b=>{
      b.classList.remove("active");
    });
    document.getElementById(id).style.display = "block";
    document.getElementById(id).classList.add("active");

    // Aktif butonu işaretle
    document.querySelector(`#btn-${id}`).classList.add("active");

    if(window.innerWidth <= 768){
      sidebar.classList.remove("open");
    }
  }

  // Başlangıçta hoşgeldin sayfası göster
  showSection("hosgeldin");

  // JSON verisini güzel HTML listeye dönüştürür (sadece data kısmı gösterilir)
  function renderData(data) {
    if (data === null) return "null";
    if (typeof data !== 'object') return data;

    if (Array.isArray(data)) {
      let html = "<ul>";
      data.forEach(item => {
        html += `<li>${renderData(item)}</li>`;
      });
      html += "</ul>";
      return html;
    }

    let html = "<ul>";
    for (const key in data) {
      if (!data.hasOwnProperty(key)) continue;
      if(key === "api_ismi" || key === "author" || key === "success" || key === "telegram") continue; // Bunları gösterme
      let val = data[key];
      if(val === null) val = "null";
      else if(typeof val === "object"){
        html += `<li><b>${key}:</b> ${renderData(val)}</li>`;
      } else {
        html += `<li><b>${key}:</b> ${val}</li>`;
      }
    }
    html += "</ul>";
    return html;
  }

  // Form gönderimi ve API çağrısı
  async function submitForm(apiName){
    const form = document.querySelector(`#${apiName} form`);
    const resultDiv = document.getElementById(`${apiName}-result`);
    resultDiv.innerHTML = "Yükleniyor...";

    let url = `/api/${apiName}`;
    let params = {};
    const formData = new FormData(form);
    for(const [key,value] of formData.entries()){
      params[key] = value.trim();
    }

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(params)
      });
      // API bazen JSON değil string dönebilir, önce JSON dene, olmazsa string döndür.
      let data;
      try {
        data = await res.json();
      } catch {
        data = await res.text();
      }

      if(data.error){
        resultDiv.innerHTML = "<b>Hata:</b> " + data.error;
        return;
      }

      if(typeof data === "string"){
        resultDiv.innerHTML = data;
        return;
      }

      resultDiv.innerHTML = renderData(data);

    } catch(e){
      resultDiv.innerHTML = "<b>Hata:</b> Bağlantı hatası";
    }
  }
</script>
</body>
</html>
"""

# ------------- Flask ROUTES -------------------

@app.route("/", methods=["GET"])
def home():
    if "user" in session:
        return redirect(url_for("panel"))
    else:
        return redirect(url_for("login_page"))

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "user" in session:
        return redirect(url_for("panel"))
    error = None
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and check_password_hash(users[username]["password"], password):
            session["user"] = username
            return redirect(url_for("panel"))
        else:
            error = "Kullanıcı adı veya şifre yanlış."
    return render_template_string(LOGIN_PAGE, logo=LOGO_BASE64, error=error)

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if "user" in session:
        return redirect(url_for("panel"))
    error = None
    if request.method == "POST":
        users = load_users()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        if len(password) < 4:
            error = "Şifre en az 4 karakter olmalı."
        elif username in users:
            error = "Kullanıcı adı zaten kayıtlı."
        else:
            users[username] = {"password": generate_password_hash(password)}
            save_users(users)
            return redirect(url_for("login_page"))
    return render_template_string(REGISTER_PAGE, logo=LOGO_BASE64, error=error)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

@app.route("/panel")
def panel():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template_string(MAIN_PAGE, logo=LOGO_BASE64)

# API Proxy: Sunucudan api.hexnox pro ya istek yapıp cevabı döndürür
@app.route("/api/<api_name>", methods=["POST"])
def api_proxy(api_name):
    if "user" not in session:
        return jsonify({"error": "Giriş yapmalısınız."})

    if api_name not in API_ENDPOINTS:
        return jsonify({"error": "Geçersiz API adı."})

    data = request.get_json()
    url = API_ENDPOINTS[api_name]

    # parametreleri uygun şekilde ekle
    try:
        if api_name == "adsoyadilice":
            ad = data.get("ad", "").strip()
            soyad = data.get("soyad", "").strip()
            if not ad or not soyad:
                return jsonify({"error": "Ad ve soyad boş olamaz."})
            url = url.format(ad=ad, soyad=soyad)
        elif api_name in ["gsmdetay", "gsm"]:
            gsm = data.get("gsm", "").strip()
            if not gsm:
                return jsonify({"error": "GSM boş olamaz."})
            url += gsm
        else:
            tc = data.get("tc", "").strip()
            if not tc:
                return jsonify({"error": "TC boş olamaz."})
            url += tc

        # API çağrısı
        resp = requests.get(url, timeout=10)
        # Json dönüşü sağlamaya çalış
        try:
            response_data = resp.json()
        except:
            response_data = resp.text

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": "API çağrısında hata oluştu."})

if __name__ == "__main__":
    app.run(debug=True)
