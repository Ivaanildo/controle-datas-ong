# 🏢 Sistema de Controle de Datas para ONGs

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

Sistema completo e moderno para gerenciamento de produtos, controle de validades, categorias e movimentações para ONGs. Desenvolvido com Flask, SQLite, Bootstrap 5 e seguindo as melhores práticas de desenvolvimento de 2025.

## 🌟 Principais Funcionalidades

### 📊 **Dashboard Interativo**
- **Cards de status modernos** com layout responsivo e animações
- **Gráficos dinâmicos** (Chart.js) para análise visual
- **Estatísticas em tempo real** de produtos, categorias e validades
- **Interface responsiva** adaptável a todos os dispositivos

### 📦 **Gestão de Produtos**
- **CRUD completo** com validações avançadas
- **Controle de validade inteligente** com 4 categorias:
  - ❌ **Vencidos** (dias < 0)
  - 🚨 **Urgentes** (0-7 dias)
  - ⚠️ **Próximos** (8-30 dias)
  - ✅ **OK** (mais de 30 dias)
- **Gestão de estoque** com controle de entrada/saída
- **Códigos de barras** e localização de produtos

### 📋 **Categorias e Organização**
- **Sistema de categorias** flexível e hierárquico
- **Relacionamentos automáticos** entre produtos e categorias
- **Filtros dinâmicos** por categoria em todo o sistema

### 📈 **Movimentações e Histórico**
- **Controle de entrada e saída** com timestamps
- **Histórico completo** de todas as operações
- **Rastreabilidade total** dos produtos

### 📄 **Relatórios Avançados**
- **PDFs profissionais** com filtros personalizáveis
- **Exportação Excel** para análise externa
- **Relatórios de validade** com alertas visuais
- **Filtros por data, categoria e status**

### 🔌 **API REST Completa**
- **Endpoints RESTful** para todas as entidades
- **Integração fácil** com outros sistemas
- **Documentação automática** dos endpoints
- **Tratamento de erros** padronizado

### 🧪 **Testes e Qualidade**
- **Testes automáticos** com pytest
- **Coverage reports** para qualidade do código
- **Validação de endpoints** automatizada
- **CI/CD ready** para deploy contínuo

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### 1. **Clone o Repositório**
```bash
git clone <url-do-repositorio>
cd SISTEMAONG-ControleDatas
```

### 2. **Ambiente Virtual (Recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. **Instalação de Dependências**
```bash
pip install -r requirements.txt
```

### 4. **Configuração do Banco de Dados**
```bash
# Inicializar migrações (se necessário)
flask db init

# Criar migração
flask db migrate -m "Initial migration"

# Aplicar migrações
flask db upgrade

# Inserir categorias padrão
python scripts/cadastrar_categorias.py
```

### 5. **Executar o Sistema**
```bash
python run.py
```

🎉 **Acesse**: http://localhost:5000

## 🐳 Docker (Deployment)

### Build da Imagem
```bash
docker build -t sistema-ong .
```

### Executar Container
```bash
docker run -p 5000:5000 sistema-ong
```

### Docker Compose (Recomendado)
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./instance:/app/instance
    environment:
      - FLASK_ENV=production
```

## 🧪 Testes e Validação

### Executar Testes Completos
```bash
pytest
```

### Testes com Coverage
```bash
pytest --cov=app
```

### Teste dos Endpoints
```bash
python test_endpoints.py
```

## 📁 Estrutura do Projeto

```
SISTEMAONG-ControleDatas/
├── 📁 app/                    # Aplicação principal
│   ├── __init__.py           # Factory pattern
│   ├── config.py             # Configurações
│   ├── models.py             # Modelos do banco
│   ├── routes.py             # Rotas e API
│   ├── forms.py              # Formulários WTF
│   ├── 📁 static/            # Arquivos estáticos
│   │   ├── 📁 css/          # Estilos customizados
│   │   └── 📁 js/           # JavaScript
│   └── 📁 templates/         # Templates HTML
├── 📁 migrations/            # Migrações Alembic
├── 📁 scripts/              # Scripts utilitários
├── 📁 tests/                # Testes automatizados
├── 📁 instance/             # Banco SQLite
├── requirements.txt         # Dependências
├── Dockerfile              # Container Docker
├── README.md               # Este arquivo
└── run.py                  # Entry point
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask 2.3.3** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **Flask-Migrate** - Migrações de banco
- **Flask-WTF** - Formulários e validação
- **Flask-Login** - Autenticação
- **SQLite** - Banco de dados

### Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **Chart.js** - Gráficos interativos
- **JavaScript ES6+** - Interatividade
- **CSS Grid/Flexbox** - Layout moderno

### Relatórios e Export
- **ReportLab** - Geração de PDFs
- **Pandas** - Manipulação de dados
- **Openpyxl** - Exportação Excel

### Testes e Qualidade
- **Pytest** - Framework de testes
- **Coverage** - Análise de cobertura
- **Flask-Testing** - Testes de integração

## 📊 API Endpoints

### Produtos
- `GET /api/produtos` - Listar produtos
- `POST /api/produtos` - Criar produto
- `PUT /api/produtos/{id}` - Atualizar produto
- `DELETE /api/produtos/{id}` - Deletar produto

### Categorias
- `GET /api/categorias` - Listar categorias
- `POST /api/categorias` - Criar categoria
- `PUT /api/categorias/{id}` - Atualizar categoria
- `DELETE /api/categorias/{id}` - Deletar categoria

### Movimentações
- `GET /api/movimentacoes` - Listar movimentações
- `POST /api/movimentacoes` - Criar movimentação

### Dashboard
- `GET /api/dashboard/stats` - Estatísticas gerais
- `GET /api/dashboard/chart-data` - Dados para gráficos
- `GET /api/dashboard/product-status-chart` - Status dos produtos

### Relatórios
- `GET /api/relatorio` - Gerar relatórios (PDF/Excel)
- `GET /api/relatorios/validades` - Relatório de validades

## 🎨 Interface e UX

### Design System
- **Cores primárias**: Azul (#06b6d4) e gradientes
- **Typography**: Inter font family
- **Componentes**: Cards modernos com animações
- **Responsividade**: Mobile-first approach

### Melhorias Recentes
- ✨ Cards de status com layout horizontal moderno
- 🎨 Gradientes e sombras refinadas
- 📱 Responsividade aprimorada para todos os dispositivos
- ⚡ Animações suaves com cubic-bezier
- 🎯 Hover effects e micro-interações

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
FLASK_APP=run.py
FLASK_ENV=development  # ou production
SECRET_KEY=sua-chave-secreta
DATABASE_URL=sqlite:///instance/app.db
```

### Configurações de Produção
- Use um servidor WSGI (Gunicorn, uWSGI)
- Configure proxy reverso (Nginx)
- Implemente SSL/TLS
- Configure backup automático do banco

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Sistema de usuários e permissões
- [ ] Notificações por email/SMS
- [ ] Integração com código de barras
- [ ] Dashboard de analytics avançado
- [ ] API GraphQL
- [ ] PWA (Progressive Web App)
- [ ] Integração com ERPs

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Ivanildo Nogueira Lima**
- 📧 Email: [seu-email@exemplo.com]
- 💼 LinkedIn: [seu-linkedin]
- 🐱 GitHub: [seu-github]

## 🙏 Agradecimentos

- Comunidade Flask por frameworks excelentes
- Bootstrap team pelo framework CSS
- Chart.js pelos gráficos interativos
- Todos os contribuidores do projeto

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!** ⭐

