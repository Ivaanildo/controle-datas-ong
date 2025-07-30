from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from datetime import date


class EventoForm(FlaskForm):
    """Formulário para criação e edição de eventos"""
    
    nome = StringField(
        'Nome do Evento',
        validators=[
            DataRequired(message='Nome é obrigatório'),
            Length(min=2, max=120, message='Nome deve ter entre 2 e 120 caracteres')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Digite o nome do evento'}
    )
    
    descricao = TextAreaField(
        'Descrição',
        render_kw={
            'class': 'form-control', 
            'placeholder': 'Descreva o evento (opcional)',
            'rows': 4
        }
    )
    
    data = DateField(
        'Data do Evento',
        validators=[DataRequired(message='Data é obrigatória')],
        default=date.today,
        render_kw={'class': 'form-control'}
    )
    
    categoria = SelectField(
        'Categoria',
        validators=[DataRequired(message='Categoria é obrigatória')],
        choices=[
            ('doacao', 'Doação'),
            ('distribuicao', 'Distribuição'),
            ('evento', 'Evento Especial'),
            ('treinamento', 'Treinamento'),
            ('reuniao', 'Reunião'),
            ('campanha', 'Campanha'),
            ('outro', 'Outro')
        ],
        render_kw={'class': 'form-select'}
    )
    
    status = SelectField(
        'Status',
        validators=[DataRequired(message='Status é obrigatório')],
        choices=[
            ('ativo', 'Ativo'),
            ('cancelado', 'Cancelado'),
            ('concluido', 'Concluído'),
            ('adiado', 'Adiado')
        ],
        default='ativo',
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Salvar',
        render_kw={'class': 'btn btn-primary'}
    )


# Formulários adicionais para o sistema de controle de estoque (podem ser usados futuramente)

class ProdutoForm(FlaskForm):
    """Formulário para criação e edição de produtos"""
    
    nome = StringField(
        'Nome do Produto',
        validators=[
            DataRequired(message='Nome é obrigatório'),
            Length(min=2, max=200, message='Nome deve ter entre 2 e 200 caracteres')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Digite o nome do produto'}
    )
    
    descricao = TextAreaField(
        'Descrição',
        render_kw={
            'class': 'form-control', 
            'placeholder': 'Descreva o produto (opcional)',
            'rows': 3
        }
    )
    
    categoria_id = SelectField(
        'Categoria',
        validators=[DataRequired(message='Categoria é obrigatória')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    quantidade_inicial = StringField(
        'Quantidade Inicial',
        validators=[DataRequired(message='Quantidade é obrigatória')],
        render_kw={'class': 'form-control', 'type': 'number', 'min': '0'}
    )
    
    unidade = SelectField(
        'Unidade',
        validators=[DataRequired(message='Unidade é obrigatória')],
        choices=[
            ('unidade', 'Unidade'),
            ('kg', 'Quilograma'),
            ('g', 'Grama'),
            ('litro', 'Litro'),
            ('ml', 'Mililitro'),
            ('caixa', 'Caixa'),
            ('pacote', 'Pacote'),
            ('saco', 'Saco')
        ],
        default='unidade',
        render_kw={'class': 'form-select'}
    )
    
    data_validade = DateField(
        'Data de Validade',
        validators=[DataRequired(message='Data de validade é obrigatória')],
        render_kw={'class': 'form-control'}
    )
    
    valor_unitario = StringField(
        'Valor Unitário (R$)',
        render_kw={'class': 'form-control', 'type': 'number', 'step': '0.01', 'min': '0'}
    )
    
    localizacao = StringField(
        'Localização',
        render_kw={'class': 'form-control', 'placeholder': 'Ex: Prateleira A1, Geladeira 2, etc.'}
    )
    
    codigo_barras = StringField(
        'Código de Barras',
        render_kw={'class': 'form-control', 'placeholder': 'Código de barras (opcional)'}
    )
    
    submit = SubmitField(
        'Salvar',
        render_kw={'class': 'btn btn-primary'}
    )


class CategoriaForm(FlaskForm):
    """Formulário para criação e edição de categorias"""
    
    nome = StringField(
        'Nome da Categoria',
        validators=[
            DataRequired(message='Nome é obrigatório'),
            Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Digite o nome da categoria'}
    )
    
    descricao = TextAreaField(
        'Descrição',
        render_kw={
            'class': 'form-control', 
            'placeholder': 'Descreva a categoria (opcional)',
            'rows': 3
        }
    )
    
    submit = SubmitField(
        'Salvar',
        render_kw={'class': 'btn btn-primary'}
    )


class MovimentacaoForm(FlaskForm):
    """Formulário para registro de movimentações"""
    
    produto_id = SelectField(
        'Produto',
        validators=[DataRequired(message='Produto é obrigatório')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    tipo = SelectField(
        'Tipo de Movimentação',
        validators=[DataRequired(message='Tipo é obrigatório')],
        choices=[
            ('entrada', 'Entrada'),
            ('saida', 'Saída')
        ],
        render_kw={'class': 'form-select'}
    )
    
    quantidade = StringField(
        'Quantidade',
        validators=[DataRequired(message='Quantidade é obrigatória')],
        render_kw={'class': 'form-control', 'type': 'number', 'min': '1'}
    )
    
    motivo = SelectField(
        'Motivo',
        validators=[DataRequired(message='Motivo é obrigatório')],
        choices=[
            ('doacao', 'Doação Recebida'),
            ('compra', 'Compra'),
            ('distribuicao', 'Distribuição'),
            ('doacao_saida', 'Doação Feita'),
            ('vencimento', 'Produto Vencido'),
            ('perda', 'Perda/Dano'),
            ('outro', 'Outro')
        ],
        render_kw={'class': 'form-select'}
    )
    
    observacoes = TextAreaField(
        'Observações',
        render_kw={
            'class': 'form-control', 
            'placeholder': 'Observações adicionais (opcional)',
            'rows': 3
        }
    )
    
    usuario = StringField(
        'Usuário Responsável',
        render_kw={'class': 'form-control', 'placeholder': 'Nome do responsável'}
    )
    
    submit = SubmitField(
        'Registrar Movimentação',
        render_kw={'class': 'btn btn-primary'}
    )
