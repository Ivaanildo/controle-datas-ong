# Arquitetura UML - Sistema Central ONG

## 1. Diagrama de Classes (Modelo de Dados)

```
┌─────────────────────────┐
│       Categoria         │
├─────────────────────────┤
│ + id: Integer (PK)      │
│ + nome: String(100)     │
│ + descricao: Text       │
│ + created_at: DateTime  │
├─────────────────────────┤
│ + __repr__()            │
└─────────────────────────┘
            │ 1
            │ has
            │ *
┌─────────────────────────┐
│        Produto          │
├─────────────────────────┤
│ + id: Integer (PK)      │
│ + nome: String(200)     │
│ + descricao: Text       │
│ + quantidade_inicial: Int│
│ + quantidade_atual: Int │
│ + unidade: String(20)   │
│ + data_validade: Date   │
│ + valor_unitario: Float │
│ + categoria_id: Int (FK)│
│ + localizacao: String   │
│ + codigo_barras: String │
│ + status: String        │
│ + created_at: DateTime  │
│ + updated_at: DateTime  │
├─────────────────────────┤
│ + dias_restantes: Int   │
│ + status_validade: Str  │
│ + valor_total: Float    │
└─────────────────────────┘
            │ 1
            │ has
            │ *
┌─────────────────────────┐
│     Movimentacao        │
├─────────────────────────┤
│ + id: Integer (PK)      │
│ + produto_id: Int (FK)  │
│ + tipo: String(20)      │
│ + quantidade: Integer   │
│ + motivo: String(50)    │
│ + observacoes: Text     │
│ + data_movimentacao: DT │
│ + usuario: String(100)  │
├─────────────────────────┤
│ + __repr__()            │
└─────────────────────────┘
```

## 2. Diagrama de Componentes (Arquitetura do Sistema)

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)               │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Dashboard  │  │  Produtos   │  │ Categorias  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │Movimentações│  │ Relatórios  │  │ Validades   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                             │ HTTP/AJAX
                             ▼
┌─────────────────────────────────────────────────────────┐
│                   FLASK APPLICATION                     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │   Routes.py     │    │     API.py      │            │
│  │ (Web Routes)    │    │ (REST API)      │            │
│  └─────────────────┘    └─────────────────┘            │
│                             │                           │
│  ┌─────────────────────────────────────────┐           │
│  │            Models.py                    │           │
│  │  (Categoria, Produto, Movimentacao)     │           │
│  └─────────────────────────────────────────┘           │
│                             │                           │
│  ┌─────────────────────────────────────────┐           │
│  │          SQLAlchemy ORM                 │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    SQLite Database                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ categorias  │  │  produtos   │  │movimentacoes│     │
│  │    table    │  │    table    │  │    table    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 3. Diagrama de Sequência (Fluxo de Cadastro de Produto)

```
Cliente    Frontend    Flask App    Database
  │           │           │           │
  │  Preenche │           │           │
  │  Formulário          │           │
  │           │           │           │
  │  Clica    │           │           │
  │  Salvar   │           │           │
  │───────────▶           │           │
  │           │ POST      │           │
  │           │/api/produtos         │
  │           │───────────▶           │
  │           │           │ INSERT    │
  │           │           │───────────▶
  │           │           │ Produto   │
  │           │           │◀──────────│
  │           │ JSON      │ Created   │
  │           │ Response  │           │
  │           │◀──────────│           │
  │  Atualiza │           │           │
  │  Tabela   │           │           │
  │◀──────────│           │           │
```

## 4. Diagrama de Casos de Uso

```
                    ┌─────────────────┐
                    │   Administrador │
                    └─────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Gerenciar    │    │Controlar    │    │Gerar        │
│Produtos     │    │Estoque      │    │Relatórios   │
└─────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │
        │                   │                   │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Gerenciar    │    │Registrar    │    │Monitorar    │
│Categorias   │    │Movimentações│    │Validades    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 5. Diagrama de Arquitetura de Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUÇÃO                             │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │   Web Server    │    │  Static Files   │            │
│  │   (Gunicorn)    │    │    (Nginx)      │            │
│  └─────────────────┘    └─────────────────┘            │
│           │                       │                     │
│           └───────────┬───────────┘                     │
│                       │                                 │
│  ┌─────────────────────────────────────────┐           │
│  │        Flask Application                │           │
│  │         (Central ONG)                   │           │
│  └─────────────────────────────────────────┘           │
│                       │                                 │
│  ┌─────────────────────────────────────────┐           │
│  │         SQLite Database                 │           │
│  │        (instance/app.db)                │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 DESENVOLVIMENTO                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐           │
│  │      Flask Development Server           │           │
│  │           (python run.py)               │           │
│  └─────────────────────────────────────────┘           │
│                       │                                 │
│  ┌─────────────────────────────────────────┐           │
│  │         SQLite Database                 │           │
│  │        (instance/app.db)                │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

## 6. Fluxo de Dados (Data Flow)

```
1. ENTRADA DE DADOS
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Formulário │───▶│   Validação │───▶│   Banco de  │
│   Web UI    │    │   (Forms)   │    │    Dados    │
└─────────────┘    └─────────────┘    └─────────────┘

2. PROCESSAMENTO
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Modelos   │───▶│   Cálculos  │───▶│ Estatísticas│
│ (ORM/SQL)   │    │ (Validades) │    │ (Dashboard) │
└─────────────┘    └─────────────┘    └─────────────┘

3. SAÍDA DE DADOS
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   JSON API  │───▶│  Templates  │───▶│   Relatórios│
│  (Frontend) │    │   (HTML)    │    │    (PDF)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

Este documento UML fornece uma visão completa da arquitetura do sistema Central ONG, incluindo modelos, componentes, fluxos e deployment.
