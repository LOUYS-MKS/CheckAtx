import os
import argparse
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from datetime import datetime

def connected_users(username):
    ps_output = os.popen(f'ps -u {username} | grep sshd | wc -l').read().strip()
    return ps_output

def user_limit(username):
    users_db_path = '/root/usuarios.db'

    if os.path.isfile(users_db_path):
        with open(users_db_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2 and parts[0] == username:
                    return parts[1]
    return "000"

def get_account_info(username):
    try:
        chage_output = subprocess.check_output(["chage", "-l", username]).decode("utf-8")
        co_date_str = next((line.split(":")[-1].strip() for line in chage_output.splitlines() if "Account expires" in line), None)
        co_date = datetime.strptime(co_date_str, "%b %d, %Y") if co_date_str else None
        return co_date
    except subprocess.CalledProcessError:
        return None

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/check?user='):
            start_index = self.path.find('/check?user=') + len('/check?user=')
            username = self.path[start_index:]

            user_info = {
                "username": username,
                "cont_conexao": connected_users(username),
                "data_expiracao": get_account_info(username).strftime("%d/%m/%Y") if get_account_info(username) else "N/A",
                "dias_expiracao": str((get_account_info(username) - datetime.now()).days) if get_account_info(username) else "N/A",
                "limite_user": user_limit(username)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(user_info).encode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--port', type=int, default=6000, help="Server port (default: 6000)")
    args = parser.parse_args()
    port = args.port
    server = HTTPServer(('0.0.0.0', port), CustomHandler)
    print(f"Server started on port {port}")
    server.serve_forever()
