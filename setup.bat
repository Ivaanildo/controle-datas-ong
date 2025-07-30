@echo off
setlocal enabledelayedexpansion

REM Script de Setup Automatizado - Sistema ONG (Windows)
REM Autor: Ivanildo Nogueira Lima
REM Versão: 1.0.0

echo 🏢 Sistema de Controle de Datas para ONGs
echo ==========================================
echo.

REM Verificar se Python está instalado
:check_python
echo [INFO] Verificando instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python não está instalado. Por favor, instale Python 3.11 ou superior.
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python !PYTHON_VERSION! encontrado

REM Criar ambiente virtual
:create_venv
echo [INFO] Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Ambiente virtual criado
) else (
    echo [WARNING] Ambiente virtual já existe
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo [INFO] Instalando dependências...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [SUCCESS] Dependências instaladas

REM Configurar arquivo .env
echo [INFO] Configurando arquivo de ambiente...
if not exist ".env" (
    copy .env.example .env >nul
    echo [SUCCESS] Arquivo .env criado a partir do .env.example
    echo [WARNING] Por favor, edite o arquivo .env com suas configurações
) else (
    echo [WARNING] Arquivo .env já existe
)

REM Criar diretórios necessários
echo [INFO] Criando diretórios necessários...
if not exist "instance" mkdir instance
if not exist "logs" mkdir logs

REM Configurar banco de dados
echo [INFO] Configurando banco de dados...
set FLASK_APP=run.py
flask db upgrade
echo [SUCCESS] Banco de dados configurado

REM Inserir dados iniciais
echo [INFO] Inserindo dados iniciais...
if exist "scripts\cadastrar_categorias.py" (
    python scripts\cadastrar_categorias.py
    echo [SUCCESS] Categorias padrão inseridas
) else (
    echo [WARNING] Script de categorias não encontrado
)

REM Executar testes
echo [INFO] Executando testes...
pytest --verbose
if %errorlevel% equ 0 (
    echo [SUCCESS] Todos os testes passaram
) else (
    echo [WARNING] Alguns testes falharam
)

REM Verificar instalação
echo [INFO] Verificando instalação...
python -c "from app import create_app; app = create_app(); print('✅ Aplicação criada com sucesso')"
echo [SUCCESS] Instalação verificada

echo.
echo [SUCCESS] Instalação completa finalizada!
echo.
echo Para iniciar a aplicação:
echo   venv\Scripts\activate
echo   python run.py
echo.
echo Ou use o Docker:
echo   docker-compose up
echo.

REM Menu de opções
:menu
echo.
echo Escolha uma opção:
echo 1) Iniciar aplicação
echo 2) Executar testes
echo 3) Build Docker
echo 4) Abrir no navegador
echo 5) Sair
echo.
set /p choice="Digite sua escolha [1-5]: "

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto run_tests
if "%choice%"=="3" goto build_docker
if "%choice%"=="4" goto open_browser
if "%choice%"=="5" goto exit
goto menu

:start_app
echo [INFO] Iniciando aplicação...
set FLASK_APP=run.py
set FLASK_ENV=development
echo [SUCCESS] Aplicação iniciando em http://localhost:5000
python run.py
goto menu

:run_tests
echo [INFO] Executando testes...
pytest --verbose
goto menu

:build_docker
echo [INFO] Construindo imagem Docker...
docker build -t sistema-ong:latest .
echo [SUCCESS] Imagem Docker construída
echo Você pode executar com:
echo   docker run -p 5000:5000 sistema-ong:latest
echo Ou usar docker-compose:
echo   docker-compose up
goto menu

:open_browser
echo [INFO] Abrindo navegador...
start http://localhost:5000
goto menu

:exit
echo [INFO] Saindo...
pause
exit /b 0
