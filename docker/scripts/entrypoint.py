import os
import socket
import subprocess
import sys
import time

def wait_for_db():
    if os.getenv("USE_POSTGRES") == "True":
        host = os.getenv("DB_HOST", "db")
        port = int(os.getenv("DB_PORT", 5432))
        
        while True:
            try: #Teste de conexão
                with socket.create_connection((host, port), timeout=1):
                    break
            except (socket.error, socket.timeout):
                time.sleep(1)

def run_django_commands():
    subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=True)
    
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=True)

if __name__ == "__main__":
    wait_for_db()
    run_django_commands()
    
    # O comando final (Gunicorn) vem como argumentos para este script
    # Se não houver argumentos, não faz nada (útil para debug)
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
