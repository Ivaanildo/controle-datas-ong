from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()


def create_app(config_class=None):
    app = Flask(__name__)
    env = os.environ.get('FLASK_ENV', 'development')
    if not config_class:
        if env == 'production':
            config_class = ProductionConfig
        elif env == 'testing':
            config_class = TestingConfig
        else:
            config_class = DevelopmentConfig
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Dummy user_loader para testes sem autenticação real
    @login_manager.user_loader
    def load_user(user_id):
        return None

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Comando CLI para popular o banco de dados com eventos de exemplo
    @app.cli.command("seed-db")
    def seed_db():
        from .models import Evento
        from datetime import date
        exemplos = [
            Evento(nome="Reunião Geral", descricao="Reunião mensal da ONG", data=date(2025, 7, 20), categoria="reunião", status="ativo"),
            Evento(nome="Campanha de Arrecadação", descricao="Campanha anual de doações", data=date(2025, 8, 15), categoria="campanha", status="ativo"),
            Evento(nome="Treinamento de Voluntários", descricao="Capacitação para novos voluntários", data=date(2025, 9, 5), categoria="outro", status="ativo")
        ]
        for evento in exemplos:
            if not Evento.query.filter_by(nome=evento.nome).first():
                db.session.add(evento)
        db.session.commit()
        print("Banco de dados populado com eventos de exemplo!")

    # Comando CLI para popular o banco com dados da Central ONG
    @app.cli.command("seed-central-ong")
    def seed_central_ong():
        """Popula o banco com dados de exemplo para Central ONG"""
        from .models import Categoria, Produto, Movimentacao
        from datetime import date, datetime, timedelta
        
        # Limpar dados existentes
        Movimentacao.query.delete()
        Produto.query.delete()
        Categoria.query.delete()
        
        # Criar categorias
        categorias = [
            Categoria(nome='Alimentos Perecíveis', descricao='Produtos que necessitam refrigeração'),
            Categoria(nome='Alimentos Não Perecíveis', descricao='Produtos com longa durabilidade'),
            Categoria(nome='Produtos de Higiene', descricao='Itens de limpeza e higiene pessoal'),
            Categoria(nome='Medicamentos', descricao='Produtos farmacêuticos'),
            Categoria(nome='Roupas e Calçados', descricao='Vestuário e calçados'),
            Categoria(nome='Material Escolar', descricao='Produtos educacionais'),
        ]
        
        for categoria in categorias:
            db.session.add(categoria)
        
        db.session.commit()
        
        # Criar produtos
        hoje = date.today()
        produtos = [
            # Alimentos Perecíveis
            Produto(nome='Leite UHT 1L', descricao='Leite longa vida integral', 
                   quantidade_inicial=50, quantidade_atual=45, unidade='litro',
                   data_validade=hoje + timedelta(days=5), valor_unitario=4.50, 
                   categoria_id=1, localizacao='Geladeira 1', codigo_barras='1234567890001'),
            
            Produto(nome='Iogurte Natural 170g', descricao='Iogurte natural sem açúcar', 
                   quantidade_inicial=30, quantidade_atual=25, unidade='pote',
                   data_validade=hoje + timedelta(days=2), valor_unitario=3.20, 
                   categoria_id=1, localizacao='Geladeira 2', codigo_barras='1234567890002'),
            
            Produto(nome='Queijo Mussarela 400g', descricao='Queijo mussarela fatiado', 
                   quantidade_inicial=20, quantidade_atual=18, unidade='pacote',
                   data_validade=hoje + timedelta(days=8), valor_unitario=12.90, 
                   categoria_id=1, localizacao='Geladeira 1', codigo_barras='1234567890003'),
            
            # Alimentos Não Perecíveis
            Produto(nome='Arroz Integral 5kg', descricao='Arroz integral orgânico', 
                   quantidade_inicial=100, quantidade_atual=85, unidade='pacote',
                   data_validade=hoje + timedelta(days=180), valor_unitario=12.50, 
                   categoria_id=2, localizacao='Estoque A-1', codigo_barras='1234567890004'),
            
            Produto(nome='Feijão Preto 1kg', descricao='Feijão preto tipo 1', 
                   quantidade_inicial=80, quantidade_atual=70, unidade='pacote',
                   data_validade=hoje + timedelta(days=200), valor_unitario=8.90, 
                   categoria_id=2, localizacao='Estoque A-2', codigo_barras='1234567890005'),
            
            Produto(nome='Óleo de Soja 900ml', descricao='Óleo de soja refinado', 
                   quantidade_inicial=60, quantidade_atual=55, unidade='frasco',
                   data_validade=hoje + timedelta(days=365), valor_unitario=6.50, 
                   categoria_id=2, localizacao='Estoque A-3', codigo_barras='1234567890006'),
            
            # Produtos de Higiene
            Produto(nome='Sabonete Líquido 500ml', descricao='Sabonete antibacteriano', 
                   quantidade_inicial=40, quantidade_atual=35, unidade='frasco',
                   data_validade=hoje + timedelta(days=730), valor_unitario=8.90, 
                   categoria_id=3, localizacao='Estoque B-1', codigo_barras='1234567890007'),
            
            Produto(nome='Pasta de Dente 90g', descricao='Creme dental com flúor', 
                   quantidade_inicial=25, quantidade_atual=20, unidade='tubo',
                   data_validade=hoje + timedelta(days=450), valor_unitario=4.50, 
                   categoria_id=3, localizacao='Estoque B-2', codigo_barras='1234567890008'),
            
            # Medicamentos
            Produto(nome='Paracetamol 500mg', descricao='Analgésico e antitérmico', 
                   quantidade_inicial=15, quantidade_atual=12, unidade='caixa',
                   data_validade=hoje + timedelta(days=1), valor_unitario=15.00, 
                   categoria_id=4, localizacao='Farmácia A-1', codigo_barras='1234567890009'),
            
            Produto(nome='Dipirona 500mg', descricao='Analgésico e antitérmico', 
                   quantidade_inicial=10, quantidade_atual=8, unidade='caixa',
                   data_validade=hoje + timedelta(days=30), valor_unitario=12.50, 
                   categoria_id=4, localizacao='Farmácia A-2', codigo_barras='1234567890010'),
            
            # Roupas e Calçados
            Produto(nome='Camiseta Adulto M', descricao='Camiseta manga curta tamanho M', 
                   quantidade_inicial=30, quantidade_atual=25, unidade='peça',
                   data_validade=hoje + timedelta(days=1095), valor_unitario=25.00, 
                   categoria_id=5, localizacao='Estoque C-1', codigo_barras='1234567890011'),
            
            # Material Escolar
            Produto(nome='Caderno Universitário', descricao='Caderno 200 folhas', 
                   quantidade_inicial=50, quantidade_atual=45, unidade='unidade',
                   data_validade=hoje + timedelta(days=1095), valor_unitario=12.00, 
                   categoria_id=6, localizacao='Estoque D-1', codigo_barras='1234567890012'),
        ]
        
        for produto in produtos:
            db.session.add(produto)
        
        db.session.commit()
        
        # Criar movimentações de exemplo
        movimentacoes = [
            Movimentacao(produto_id=1, tipo='entrada', quantidade=10, motivo='doacao', 
                        observacoes='Doação da empresa XYZ', usuario='Admin'),
            Movimentacao(produto_id=2, tipo='saida', quantidade=5, motivo='distribuicao', 
                        observacoes='Distribuição para família carente', usuario='Admin'),
            Movimentacao(produto_id=4, tipo='entrada', quantidade=20, motivo='doacao', 
                        observacoes='Doação de supermercado', usuario='Admin'),
            Movimentacao(produto_id=9, tipo='saida', quantidade=3, motivo='vencimento', 
                        observacoes='Produto próximo ao vencimento', usuario='Admin'),
        ]
        
        for movimentacao in movimentacoes:
            db.session.add(movimentacao)
        
        db.session.commit()
        
        print("✅ Banco de dados populado com sucesso!")
        print(f"📊 {len(categorias)} categorias criadas")
        print(f"📦 {len(produtos)} produtos criados")
        print(f"📋 {len(movimentacoes)} movimentações criadas")

    return app
