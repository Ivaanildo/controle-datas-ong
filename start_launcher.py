import os
import subprocess
import sys
import venv

# Caminhos
venv_dir = os.path.join(os.getcwd(), 'venv')
activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')

# 1. Cria o venv se não existir
def ensure_venv():
    if not os.path.isdir(venv_dir):
        print('Criando ambiente virtual...')
        venv.create(venv_dir, with_pip=True)

# 2. Instala dependências

def install_requirements():
    print('Instalando dependências...')
    subprocess.check_call([os.path.join(venv_dir, 'Scripts', 'python.exe'), '-m', 'pip', 'install', '-r', 'requirements.txt'])

# 3. Executa script de categorias

def cadastrar_categorias():
    print('Cadastrando categorias padrão...')
    subprocess.call([os.path.join(venv_dir, 'Scripts', 'python.exe'), 'scripts/cadastrar_categorias.py'])

# 4. Inicia o sistema

def run_app():
    print('Iniciando o sistema Central ONG...')
    subprocess.call([os.path.join(venv_dir, 'Scripts', 'python.exe'), 'run.py'])

if __name__ == '__main__':
    ensure_venv()
    install_requirements()
    cadastrar_categorias()
    run_app()
    input('Pressione Enter para sair...')
