from . import db
from datetime import datetime, date
from flask_login import UserMixin

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com produtos
    produtos = db.relationship('Produto', backref='categoria_ref', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    quantidade_inicial = db.Column(db.Integer, nullable=False, default=0)
    quantidade_atual = db.Column(db.Integer, nullable=False, default=0)
    unidade = db.Column(db.String(20), nullable=False, default='unidade')
    data_validade = db.Column(db.Date, nullable=False)
    valor_unitario = db.Column(db.Float, default=0.0)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    localizacao = db.Column(db.String(100))
    codigo_barras = db.Column(db.String(50))
    status = db.Column(db.String(20), default='ativo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com movimentações
    movimentacoes = db.relationship('Movimentacao', backref='produto_ref', lazy=True)
    
    @property
    def dias_restantes(self):
        """Calcula quantos dias restam até a validade"""
        if self.data_validade:
            delta = self.data_validade - date.today()
            return delta.days
        return 0
    
    @property
    def status_validade(self):
        """Retorna o status baseado nos dias restantes - LÓGICA FINAL: 4 categorias"""
        dias = self.dias_restantes
        if dias < 0:
            return 'vencido'     # 🔴 Vermelho
        elif dias <= 7:
            return 'urgente'     # 🟡 Amarelo (#f59e0b)
        elif dias <= 30:
            return 'proximo'     # 🟠 Laranja
        else:
            return 'ok'          # 🟢 Verde
    
    @property
    def valor_total(self):
        """Calcula o valor total do produto"""
        return self.quantidade_atual * self.valor_unitario
    
    def __repr__(self):
        return f'<Produto {self.nome}>'

class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saida'
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))  # 'doacao', 'distribuicao', 'vencimento', etc.
    observacoes = db.Column(db.Text)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Movimentacao {self.tipo} - {self.quantidade}>'

# Manter tabela de eventos para não quebrar compatibilidade
class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ativo')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    criado_por = db.Column(db.String(80), nullable=True)
    atualizado_por = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return f'<Evento {self.nome}>'

# Exemplo de usuário para autenticação (pode ser expandido)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
