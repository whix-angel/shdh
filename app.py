from flask import Flask, render_template_string, request, jsonify, session
import hashlib
import json
import os
import random
import string

app = Flask(__name__)
app.secret_key = 'секретный_ключ_замени_меня'

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "users": {
                "admin": {
                    "password": hashlib.sha256("K@z1n0_2025!".encode()).hexdigest(),
                    "balance": 99999,
                    "is_admin": True
                },
                "player1": {
                    "password": hashlib.sha256("1234".encode()).hexdigest(),
                    "balance": 1000,
                    "is_admin": False
                }
            },
            "tokens": {}
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🎰 Казино</title>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: linear-gradient(145deg, #0b3b22, #041a0e); min-height: 100vh; display: flex; justify-content: center; align-items: center; font-family: 'Segoe UI', system-ui, sans-serif; padding: 16px; }
        .container { max-width: 680px; width: 100%; background: #2c1b10; border-radius: 58px; padding: 20px 18px 30px; box-shadow: 0 20px 35px black; border-bottom: 6px solid #f7c56e; color: white; }
        h1 { text-align: center; margin: 0 0 20px; font-size: 2rem; background: linear-gradient(135deg, #FFDA88, #FFA82E); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .input-group { margin: 10px 0; }
        .input-group input { width: 100%; padding: 12px; border-radius: 30px; border: none; font-size: 1rem; background: #1f1a14; color: #ffeaaf; border: 1px solid #eab354; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; margin: 10px 0; color: #ffe1a0; }
        .checkbox-group input { width: 20px; height: 20px; accent-color: #f5bc5c; }
        .btn { background: #f5bc5c; border: none; padding: 12px 20px; border-radius: 40px; font-weight: bold; color: #1f1a14; cursor: pointer; font-size: 1rem; width: 100%; margin: 5px 0; }
        .btn-secondary { background: #4a3723; color: #ffeaaf; }
        .btn-danger { background: #aa3a2c; color: white; }
        .btn-success { background: #2c8a4a; color: white; }
        .btn-admin { background: #8a6e2c; color: white; }
        .btn-give-admin { background: #2c6a8a; color: white; }
        .btn-remove-admin { background: #8a4a2c; color: white; }
        .btn-telegram { background: #0088cc; color: white; display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 20px; border-radius: 40px; text-decoration: none; font-weight: bold; flex: 1; min-width: 80px; border: none; cursor: pointer; font-size: 1rem; }
        .btn-telegram:hover { background: #006699; }
        .row { display: flex; gap: 10px; }
        .row .btn { flex: 1; }
        .reels { display: flex; justify-content: center; gap: 20px; margin: 20px 0; }
        .reel { width: 100px; height: 120px; background: #fef3df; border-radius: 28px; display: flex; align-items: center; justify-content: center; font-size: 4rem; font-weight: bold; box-shadow: inset 0 0 0 4px #f1cf94, 0 8px 0 #5a3f22; }
        .balance { text-align: center; font-size: 1.5rem; margin: 10px 0; color: #ffd966; }
        .message { text-align: center; padding: 10px; border-radius: 20px; margin: 10px 0; background: #00000055; }
        .admin-panel { background: #1f1912; border-radius: 30px; padding: 15px; margin-top: 20px; }
        .admin-panel h3 { color: #ffd58c; }
        .admin-panel input { width: 100%; padding: 8px; border-radius: 20px; border: none; background: #2e2820; color: #ffeaac; margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #444; }
        th { color: #ffd58c; }
        .nav { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
        .nav .btn, .nav .btn-telegram { flex: 1; min-width: 80px; }
        .hidden { display: none; }
        .label { color: #ffe1a0; }
        .small { font-size: 0.8rem; color: #888; }
    </style>
</head>
<body>
<div class="container" id="app">
    {% if not session.user %}
    <h1>🎰 ВХОД</h1>
    <div class="input-group"><input type="text" id="login_username" placeholder="Никнейм"></div>
    <div class="input-group"><input type="password" id="login_password" placeholder="Пароль"></div>
    <div class="checkbox-group">
        <input type="checkbox" id="remember_me">
        <label for="remember_me">🔒 Запомнить меня (на неделю)</label>
    </div>
    <button class="btn" onclick="login()">ВОЙТИ</button>
    <div id="login_message" class="message"></div>
    <div class="small" style="text-align:center; margin-top:10px;">Только для приглашённых игроков</div>
    {% else %}
    <h1>🎰 СЛОТЫ</h1>
    <div class="balance" id="balanceDisplay">💰 {{ user.balance }} ₽</div>
    <div style="display:flex; gap:10px; justify-content:center; margin:10px 0;">
        <input type="number" id="betInput" value="50" min="10" style="width:100px; padding:8px; border-radius:20px; border:none; background:#2e2820; color:#ffeaac; text-align:center;">
        <button class="btn" onclick="spin()" id="spinBtn" style="width:auto;">🌀 КРУТИТЬ</button>
    </div>
    <div class="reels">
        <div class="reel" id="reel1">🍒</div>
        <div class="reel" id="reel2">🍒</div>
        <div class="reel" id="reel3">🍒</div>
    </div>
    <div id="winMessage" class="message">💰 Сделай ставку и крути!</div>

    <div class="nav">
        <button class="btn btn-secondary" onclick="showPage('game')">🎰 Игра</button>
        <button class="btn btn-secondary" onclick="showPage('rating')">🏆 Рейтинг</button>
        {% if is_admin %}
        <button class="btn btn-secondary" onclick="showPage('admin')">⚙️ Админ</button>
        {% endif %}
        <a href="https://t.me/random_kpuc" target="_blank" class="btn-telegram">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
            Связь с разработчиком
        </a>
        <button class="btn btn-danger" onclick="logout()">🚪 Выйти</button>
    </div>

    <div id="page_rating" class="hidden">
        <h3>🏆 ТОП ИГРОКОВ</h3>
        <div id="ratingTable"></div>
        <button class="btn btn-secondary" onclick="loadRating()">🔄 Обновить</button>
    </div>

    <div id="page_admin" class="hidden">
        <div class="admin-panel">
            <h3>⚙️ АДМИН-ПАНЕЛЬ</h3>
            <h4>➕ СОЗДАТЬ ИГРОКА</h4>
            <div class="input-group"><input type="text" id="new_username" placeholder="Никнейм"></div>
            <div class="input-group"><input type="text" id="new_password" placeholder="Пароль"></div>
            <button class="btn btn-success" onclick="adminCreateUser()">➕ СОЗДАТЬ</button>
            <hr style="border-color:#555; margin:15px 0;">
            <h4>👑 УПРАВЛЕНИЕ АДМИНАМИ</h4>
            <div class="input-group"><input type="text" id="admin_target" placeholder="Никнейм игрока"></div>
            <div class="row">
                <button class="btn btn-give-admin" onclick="adminGiveAdmin()">👑 ВЫДАТЬ АДМИНА</button>
                <button class="btn btn-remove-admin" onclick="adminRemoveAdmin()">❌ ЗАБРАТЬ АДМИНА</button>
            </div>
            <hr style="border-color:#555; margin:15px 0;">
            <h4>💰 УПРАВЛЕНИЕ БАЛАНСОМ</h4>
            <div class="row">
                <button class="btn btn-success" onclick="adminGiveMoney()">➕ ВЫДАТЬ</button>
                <button class="btn btn-danger" onclick="adminTakeMoney()">➖ ЗАБРАТЬ</button>
            </div>
            <div class="row">
                <button class="btn btn-admin" onclick="adminSetJackpot()">🔥 ДЖЕКПОТ 7777</button>
            </div>
            <div class="row">
                <button class="btn btn-secondary" onclick="adminResetFair()">🎲 ЧЕСТНЫЕ ШАНСЫ</button>
                <button class="btn btn-danger" onclick="adminDeleteUser()">🗑️ УДАЛИТЬ</button>
            </div>
            <div id="admin_message" class="message"></div>
        </div>
    </div>
    {% endif %}
</div>

<script>
    async function api(url, data) {
        const r = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
        return await r.json();
    }

    async function login() {
        const u = document.getElementById('login_username').value.trim();
        const p = document.getElementById('login_password').value;
        const remember = document.getElementById('remember_me').checked;
        if(!u||!p) return;
        const res = await api('/login', {username:u, password:p, remember:remember});
        const msg = document.getElementById('login_message');
        if(res.success){ location.reload(); }
        else { msg.innerText = res.message; msg.style.color = '#ff6666'; }
    }

    async function logout(){ await api('/logout'); location.reload(); }

    function showPage(page){
        document.querySelectorAll('[id^="page_"]').forEach(el => el.classList.add('hidden'));
        document.getElementById('page_'+page).classList.remove('hidden');
    }

    const symbols = ['🍒','🍋','💎','7️⃣'];
    let isSpinning = false;

    async function spin() {
        if(isSpinning) return;
        let bet = parseInt(document.getElementById('betInput').value) || 50;
        if(bet<10) bet=10;
        document.getElementById('betInput').value = bet;
        isSpinning = true;
        document.getElementById('spinBtn').disabled = true;
        document.getElementById('winMessage').innerText = '🎡 КРУТИМ...';

        const res = await api('/spin', {bet:bet});
        if(!res.success){ document.getElementById('winMessage').innerText = res.message; isSpinning=false; document.getElementById('spinBtn').disabled=false; return; }

        const result = res.result;
        for(let i=0; i<12; i++){
            document.getElementById('reel1').innerText = symbols[Math.floor(Math.random()*symbols.length)];
            document.getElementById('reel2').innerText = symbols[Math.floor(Math.random()*symbols.length)];
            document.getElementById('reel3').innerText = symbols[Math.floor(Math.random()*symbols.length)];
            await new Promise(r=>setTimeout(r, 40));
        }
        document.getElementById('reel1').innerText = result[0];
        document.getElementById('reel2').innerText = result[1];
        document.getElementById('reel3').innerText = result[2];

        document.getElementById('balanceDisplay').innerHTML = `💰 ${res.new_balance} ₽`;
        const msg = document.getElementById('winMessage');
        if(res.win > 0){
            if(result.join('') === '7️⃣7️⃣7️⃣') msg.innerText = `🔥🔥 ДЖЕКПОТ! +${res.win} ₽ 🔥🔥`;
            else msg.innerText = `✨ ПОБЕДА! ${result.join('')} → +${res.win} ₽ ✨`;
            msg.style.color = '#ffd98c';
        } else {
            msg.innerText = `😞 ПРОИГРЫШ :( ${result.join('')} | -${bet} ₽`;
            msg.style.color = '#ff6666';
        }
        isSpinning = false;
        document.getElementById('spinBtn').disabled = false;
    }

    async function loadRating(){
        const res = await api('/rating');
        let html = '<table><tr><th>#</th><th>Ник</th><th>💰 Баланс</th></tr>';
        res.forEach((u,i) => {
            html += `<tr><td>${i+1}</td><td>${u.username}</td><td>${u.balance} ₽</td></tr>`;
        });
        html += '</table>';
        document.getElementById('ratingTable').innerHTML = html;
    }

    async function adminCreateUser(){
        const u = document.getElementById('new_username').value.trim();
        const p = document.getElementById('new_password').value.trim();
        if(!u||!p){ document.getElementById('admin_message').innerText = '❌ Заполните оба поля'; return; }
        const res = await api('/admin/create_user', {username:u, password:p});
        document.getElementById('admin_message').innerText = res.message;
        if(res.success){ document.getElementById('new_username').value = ''; document.getElementById('new_password').value = ''; }
    }

    async function adminDeleteUser(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target){ document.getElementById('admin_message').innerText = '❌ Введите никнейм'; return; }
        if(!confirm(`Удалить игрока ${target}?`)) return;
        const res = await api('/admin/delete_user', {target:target});
        document.getElementById('admin_message').innerText = res.message;
    }

    async function adminGiveMoney(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target) return;
        const res = await api('/admin/give', {target:target, amount:500});
        document.getElementById('admin_message').innerText = res.message;
    }
    async function adminTakeMoney(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target) return;
        const res = await api('/admin/take', {target:target, amount:500});
        document.getElementById('admin_message').innerText = res.message;
    }
    async function adminSetJackpot(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target) return;
        const res = await api('/admin/jackpot', {target:target});
        document.getElementById('admin_message').innerText = res.message;
    }
    async function adminResetFair(){
        const res = await api('/admin/reset_fair');
        document.getElementById('admin_message').innerText = res.message;
    }

    async function adminGiveAdmin(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target){ document.getElementById('admin_message').innerText = '❌ Введите никнейм'; return; }
        const res = await api('/admin/give_admin', {target:target});
        document.getElementById('admin_message').innerText = res.message;
    }

    async function adminRemoveAdmin(){
        const target = document.getElementById('admin_target').value.trim();
        if(!target){ document.getElementById('admin_message').innerText = '❌ Введите никнейм'; return; }
        if(target === 'admin' && !confirm('Точно забрать права у главного админа?')) return;
        const res = await api('/admin/remove_admin', {target:target});
        document.getElementById('admin_message').innerText = res.message;
    }

    document.addEventListener('DOMContentLoaded', function(){
        if(document.getElementById('page_rating')) loadRating();
    });
</script>
</body>
</html>
'''

def is_admin(username):
    data = load_data()
    return username in data['users'] and data['users'][username].get('is_admin', False)

@app.route('/', methods=['GET'])
def index():
    data = load_data()
    user = session.get('user')
    is_admin_flag = False
    if user and user in data['users']:
        is_admin_flag = data['users'][user].get('is_admin', False)
    return render_template_string(HTML_TEMPLATE,
                                   user={'username': user, 'balance': data['users'][user]['balance']} if user and user in data['users'] else None,
                                   is_admin=is_admin_flag)

@app.route('/login', methods=['POST'])
def login():
    data = load_data()
    req = request.json
    username = req.get('username')
    password = req.get('password')
    remember = req.get('remember', False)

    if username not in data['users']:
        return jsonify({'success': False, 'message': '❌ Неверный логин или пароль'})

    user = data['users'][username]
    if user['password'] != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'success': False, 'message': '❌ Неверный логин или пароль'})

    session['user'] = username

    if remember:
        token = generate_token()
        data['tokens'][token] = username
        save_data(data)
        return jsonify({'success': True, 'token': token})

    return jsonify({'success': True})

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/spin', methods=['POST'])
def spin():
    data = load_data()
    if 'user' not in session or session['user'] not in data['users']:
        return jsonify({'success': False, 'message': 'Войдите в систему'})

    username = session['user']
    bet = request.json.get('bet', 50)
    if bet < 10:
        bet = 10

    balance = data['users'][username]['balance']
    if balance < bet:
        return jsonify({'success': False, 'message': 'Недостаточно средств'})

    probs = {'loss': 83, 'win2': 8, 'win3': 5, 'win5': 3, 'jack': 1}
    r = random.random() * 100
    if r < probs['loss']:
        combo = 'LOSS'
    elif r < probs['loss'] + probs['win2']:
        combo = '🍒🍒🍒'
    elif r < probs['loss'] + probs['win2'] + probs['win3']:
        combo = '🍋🍋🍋'
    elif r < probs['loss'] + probs['win2'] + probs['win3'] + probs['win5']:
        combo = '💎💎💎'
    else:
        combo = '7️⃣7️⃣7️⃣'

    payouts = {'🍒🍒🍒': 2, '🍋🍋🍋': 3, '💎💎💎': 5, '7️⃣7️⃣7️⃣': 25}
    symbols = ['🍒', '🍋', '💎', '7️⃣']

    if combo == 'LOSS':
        for _ in range(20):
            s = [random.choice(symbols) for _ in range(3)]
            if s[0] + s[1] + s[2] not in payouts:
                break
        result = s
        win = 0
        new_balance = balance - bet
    else:
        sym = combo[0]
        result = [sym, sym, sym]
        win = bet * payouts[combo]
        new_balance = balance - bet + win

    data['users'][username]['balance'] = new_balance
    save_data(data)

    return jsonify({'success': True, 'result': result, 'win': win, 'new_balance': new_balance})

@app.route('/rating', methods=['POST'])
def rating():
    data = load_data()
    users = [{'username': u, 'balance': data['users'][u]['balance']} for u in data['users']]
    users.sort(key=lambda x: x['balance'], reverse=True)
    return jsonify(users[:100])

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if 'user' not in session or not is_admin(session['user']):
        return jsonify({'message': '❌ Нет прав'})
    req = request.json
    username = req.get('username')
    password = req.get('password')
    if not username or not password:
        return jsonify({'message': '❌ Заполните оба поля'})

    data = load_data()
    if username in data['users']:
        return jsonify({'message': '❌ Игрок уже существует'})

    data['users'][username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'balance': 1000,
        'is_admin': False
    }
    save_data(data)
    return jsonify({'success': True, '
