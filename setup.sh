#!/bin/bash

# Script de Setup Automatizado - Sistema ONG
# Autor: Ivanildo Nogueira Lima
# Versão: 1.0.0

set -e  # Sair em caso de erro

echo "🏢 Sistema de Controle de Datas para ONGs"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python está instalado
check_python() {
    print_status "Verificando instalação do Python..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalado. Por favor, instale Python 3.11 ou superior."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
}

# Criar ambiente virtual
create_venv() {
    print_status "Criando ambiente virtual..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Ambiente virtual criado"
    else
        print_warning "Ambiente virtual já existe"
    fi
}

# Ativar ambiente virtual
activate_venv() {
    print_status "Ativando ambiente virtual..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    print_success "Ambiente virtual ativado"
}

# Instalar dependências
install_dependencies() {
    print_status "Instalando dependências..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependências instaladas"
}

# Configurar arquivo .env
setup_env() {
    print_status "Configurando arquivo de ambiente..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Arquivo .env criado a partir do .env.example"
        print_warning "Por favor, edite o arquivo .env com suas configurações"
    else
        print_warning "Arquivo .env já existe"
    fi
}

# Configurar banco de dados
setup_database() {
    print_status "Configurando banco de dados..."
    
    # Criar diretório instance se não existir
    mkdir -p instance
    mkdir -p logs
    
    # Executar migrações
    export FLASK_APP=run.py
    flask db upgrade
    
    print_success "Banco de dados configurado"
}

# Inserir dados iniciais
insert_initial_data() {
    print_status "Inserindo dados iniciais..."
    if [ -f "scripts/cadastrar_categorias.py" ]; then
        python scripts/cadastrar_categorias.py
        print_success "Categorias padrão inseridas"
    else
        print_warning "Script de categorias não encontrado"
    fi
}

# Executar testes
run_tests() {
    print_status "Executando testes..."
    if command -v pytest &> /dev/null; then
        pytest --verbose
        print_success "Todos os testes passaram"
    else
        print_warning "pytest não está disponível. Instalando..."
        pip install pytest pytest-flask
        pytest --verbose
    fi
}

# Verificar instalação
verify_installation() {
    print_status "Verificando instalação..."
    python -c "from app import create_app; app = create_app(); print('✅ Aplicação criada com sucesso')"
    print_success "Instalação verificada"
}

# Menu principal
show_menu() {
    echo ""
    echo "Escolha uma opção:"
    echo "1) Instalação completa (recomendado)"
    echo "2) Apenas instalar dependências"
    echo "3) Apenas configurar banco de dados"
    echo "4) Executar testes"
    echo "5) Iniciar aplicação"
    echo "6) Build Docker"
    echo "7) Sair"
    echo ""
}

# Instalação completa
full_install() {
    print_status "Iniciando instalação completa..."
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_env
    setup_database
    insert_initial_data
    run_tests
    verify_installation
    print_success "Instalação completa finalizada!"
    echo ""
    echo "Para iniciar a aplicação, execute:"
    echo "  source venv/bin/activate  # Linux/Mac"
    echo "  venv\\Scripts\\activate     # Windows"
    echo "  python run.py"
    echo ""
    echo "Ou use o Docker:"
    echo "  docker-compose up"
}

# Build Docker
build_docker() {
    print_status "Construindo imagem Docker..."
    docker build -t sistema-ong:latest .
    print_success "Imagem Docker construída"
    
    print_status "Você pode executar com:"
    echo "  docker run -p 5000:5000 sistema-ong:latest"
    echo "Ou usar docker-compose:"
    echo "  docker-compose up"
}

# Iniciar aplicação
start_app() {
    print_status "Iniciando aplicação..."
    if [ -d "venv" ]; then
        activate_venv
    fi
    
    export FLASK_APP=run.py
    export FLASK_ENV=development
    
    print_success "Aplicação iniciando em http://localhost:5000"
    python run.py
}

# Script principal
main() {
    while true; do
        show_menu
        read -p "Digite sua escolha [1-7]: " choice
        
        case $choice in
            1)
                full_install
                break
                ;;
            2)
                check_python
                create_venv
                activate_venv
                install_dependencies
                ;;
            3)
                setup_database
                insert_initial_data
                ;;
            4)
                run_tests
                ;;
            5)
                start_app
                break
                ;;
            6)
                build_docker
                ;;
            7)
                print_status "Saindo..."
                exit 0
                ;;
            *)
                print_error "Opção inválida. Tente novamente."
                ;;
        esac
        echo ""
    done
}

# Executar script principal
main
