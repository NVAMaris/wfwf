import time
import threading
import requests
from flask import Flask

# --- CẤU HÌNH BOT ---
TELEGRAM_BOT_TOKEN = "TOKEN_BOT_CỦA_BẠN"
TELEGRAM_CHAT_ID = "CHAT_ID_CỦA_BẠN"
SERVER_API_URL = "URL_API_SERVER_GAME" # Đường dẫn API lấy server bạn đã tìm được

known_servers = set()
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot đang chạy 24/7!"

def send_telegram_alert(server_name, server_id):
    message = f"🚨 **CÓ SERVER MỚI!** 🚨\n\n🎮 Tên: {server_name}\n🆔 ID: {server_id}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

def background_bot_loop():
    global known_servers
    print("🤖 Luồng săn server bắt đầu chạy ngầm...")
    while True:
        try:
            response = requests.get(SERVER_API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                server_list = data.get("data", {}).get("servers", [])
                
                if not known_servers and server_list:
                    known_servers = {str(s.get("id") or s.get("server_id")) for s in server_list}
                    print(f"Khởi tạo thành công {len(known_servers)} server.")
                else:
                    for s in server_list:
                        s_id = str(s.get("id") or s.get("server_id"))
                        s_name = s.get("name") or s.get("server_name", f"Server {s_id}")
                        if s_id not in known_servers:
                            send_telegram_alert(s_name, s_id)
                            known_servers.add(s_id)
        except Exception as e:
            print(f"Lỗi kiểm tra API: {e}")
        
        # Nghỉ 60 giây quét lại một lần
        time.sleep(60)

if __name__ == "__main__":
    # Chạy bot ở một luồng riêng biệt (background thread)
    t = threading.Thread(target=background_bot_loop)
    t.daemon = True
    t.start()
    
    # Chạy Flask web server (Render yêu cầu mở cổng HTTP)
    app.run(host="0.0.0.0", port=10000)
