import os
import subprocess
import urllib.request
import json

cache = {}

def colored(text, color):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    return f"{colors[color]}{text}{colors['reset']}"

def add_to_cache(key, value):
    cache[key] = value
    save_cache()

def remove_from_cache(key):
    cache.pop(key, None)
    save_cache()

def load_cache():
    try:
        with open('/root/CheckAtx/cache.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache():
    with open('/root/CheckAtx/cache.json', 'w') as file:
        json.dump(cache, file)

def get_public_ip():
    try:
        url = "https://ipinfo.io"
        response = urllib.request.urlopen(url)
        if response.status == 200:
            data = json.loads(response.read().decode("utf-8"))
            return data.get('ip', None)
    except Exception as e:
        print(colored(f"Não foi possível obter o endereço IP público: {str(e)}", "red"))
        return None

def check_process(process_name):
    try:
        result = subprocess.check_output(["ps", "aux"]).decode()
        return process_name in result
    except subprocess.CalledProcessError as e:
        print(colored(f"Erro ao verificar o processo: {e}", "red"))
    return False

script_name = "/root/UlekCheckUser/checkatx.py"

def show_menu():
    os.system('clear')
    ip = get_public_ip()
    status = colored("Ativo", "green") if check_process(script_name) else colored("Parado", "red")
    port = cache.get("port", None)
    link = f'http://{ip}:{port}/check' if port else "Defina a porta primeiro."

    start_stop = colored("1 - Parar checkuser", "red") if check_process(script_name) else colored("1 - Iniciar checkuser", "green")

    print(f"{colored('╔═════════════════════════════════════════╗', 'blue')}")
    print(f"║        Menu Principal                   ║")
    print(f"║ Status: {status}")
    print(f"║")
    print(f"║ Link: {link}")
    print(f"║")
    print(f"║ Opções:")
    print(f"║ {colored(start_stop, 'yellow')}")
    print(f"║ {colored('0 - Sair do menu', 'yellow')}")
    print(f"{colored('╚═════════════════════════════════════════╝', 'blue')}")

def main_menu():
    while True:
        show_menu()
        option = input("Digite a opção: ")
        if option == "1":
            if check_process(script_name):
                try:
                    subprocess.run(f'pkill -9 -f "{script_name}"', shell=True)
                except subprocess.CalledProcessError:
                    print(colored("Erro ao parar o Checkuser", "red"))
                remove_from_cache("port")
            else:
                add_to_cache('port', input("Digite a porta que deseja usar: "))
                os.system('clear')
                os.system(f'nohup python3 {script_name} --port {cache["port"]} & ')
                print(colored("Checkuser iniciado com sucesso", "green"))
            input("\nPressione a tecla Enter para voltar ao menu\n")
        elif option == "0":
            sys.exit(0)
        else:
            os.system('clear')
            print(colored("Selecionou uma opção inválida, tente novamente!", "red"))
            input("Pressione a tecla Enter para voltar ao menu")

if __name__ == "__main__":
    cache = load_cache()
    main_menu()
