from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, abort
from .models import Evento, Produto, Categoria, Movimentacao, db
import pandas as pd
import io
from .forms import EventoForm
from . import csrf
from sqlalchemy import desc
from datetime import datetime, date
from werkzeug.exceptions import HTTPException
import re

main_bp = Blueprint('main', __name__)

# Handlers globais para erros HTTP
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return jsonify({'success': False, 'message': 'Recurso não encontrado', 'error': str(error)}), 404

@main_bp.app_errorhandler(400)
def bad_request_error(error):
    return jsonify({'success': False, 'message': 'Requisição inválida', 'error': str(error)}), 400

@main_bp.app_errorhandler(HTTPException)
def handle_http_exception(error):
    response = error.get_response()
    response.data = jsonify({'success': False, 'message': error.description, 'error': str(error)}).data
    response.content_type = "application/json"
    return response

@main_bp.route('/')
def index():
    """Página principal do sistema Central ONG"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard com estatísticas do sistema"""
    return render_template('dashboard.html')



# === ROTA DE RELATÓRIO (DOWNLOAD EXCEL OU PDF) ===
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

@main_bp.route('/api/relatorio', methods=['GET'])
def download_relatorio():
    """
    Gera relatório PDF ou Excel filtrado conforme parâmetros da query string.
    Parâmetros aceitos:
      - formato: 'pdf' ou 'xlsx'
      - tipo: 'produtos', 'categorias', 'movimentacoes' (sheet principal)
      - categoria: id da categoria (opcional)
      - status: status do produto (opcional)
      - data_inicio, data_fim: para filtrar movimentações (opcional)
    """
    try:
        tipo = request.args.get('tipo', 'produtos').strip().lower()
        filtro_categoria = request.args.get('categoria')
        filtro_status = request.args.get('status')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')

        # Validação do parâmetro tipo
        if tipo not in ['produtos', 'categorias', 'movimentacoes']:
            return jsonify({'success': False, 'message': "Tipo inválido. Use 'produtos', 'categorias' ou 'movimentacoes'."}), 400

        # Filtragem dinâmica
        query_produtos = Produto.query
        query_movimentacoes = Movimentacao.query
        query_categorias = Categoria.query

        if filtro_categoria:
            try:
                filtro_categoria_id = int(filtro_categoria)
            except Exception:
                return jsonify({'success': False, 'message': 'Categoria inválida'}), 400
            query_produtos = query_produtos.filter_by(categoria_id=filtro_categoria_id)
            query_movimentacoes = query_movimentacoes.join(Produto).filter(Produto.categoria_id == filtro_categoria_id)
        if filtro_status:
            query_produtos = query_produtos.filter(Produto.status_validade == filtro_status)
        if data_inicio:
            try:
                dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
                query_movimentacoes = query_movimentacoes.filter(Movimentacao.data_movimentacao >= dt_inicio)
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de data de início inválido. Use YYYY-MM-DD.'}), 400

        if data_fim:
            try:
                dt_fim = datetime.strptime(data_fim, "%Y-%m-%d")
                query_movimentacoes = query_movimentacoes.filter(Movimentacao.data_movimentacao <= dt_fim)
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de data de fim inválido. Use YYYY-MM-DD.'}), 400

        produtos = query_produtos.all()
        categorias = query_categorias.all()
        movimentacoes = query_movimentacoes.all()

        # Dados para exportação
        produtos_data = [
            {
                'ID': p.id,
                'Nome': p.nome,
                'Categoria': p.categoria_ref.nome if p.categoria_ref else '',
                'Quantidade Inicial': p.quantidade_inicial,
                'Quantidade Atual': p.quantidade_atual,
                'Unidade': p.unidade,
                'Validade': p.data_validade.strftime('%Y-%m-%d') if p.data_validade else '',
                'Valor Unitário': p.valor_unitario,
                'Valor Total': p.valor_total,
                'Status': p.status_validade,
            }
            for p in produtos
        ]
        categorias_data = [
            {
                'ID': c.id,
                'Nome': c.nome,
                'Descrição': c.descricao,
                'Criado em': c.created_at.strftime('%Y-%m-%d') if c.created_at else ''
            }
            for c in categorias
        ]
        movimentacoes_data = [
            {
                'ID': m.id,
                'Produto': m.produto_ref.nome if m.produto_ref else '',
                'Tipo': m.tipo,
                'Quantidade': m.quantidade,
                'Motivo': m.motivo,
                'Data': m.data_movimentacao.strftime('%Y-%m-%d') if m.data_movimentacao else '',
                'Usuário': m.usuario
            }
            for m in movimentacoes
        ]

        formato = request.args.get('formato', 'pdf').strip().lower()
        if formato == 'xlsx':
            output = io.BytesIO()
            if tipo == 'produtos':
                df = pd.DataFrame(produtos_data)
            elif tipo == 'categorias':
                df = pd.DataFrame(categorias_data)
            elif tipo == 'movimentacoes':
                df = pd.DataFrame(movimentacoes_data)
            else:
                df = pd.DataFrame()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name=tipo.capitalize())
            output.seek(0)
            return send_file(
                output,
                as_attachment=True,
                download_name=f'relatorio_ong_{tipo}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            # Geração do arquivo PDF com tabela estilizada
            from reportlab.lib import colors
            from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet

            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            elements = []
            styles = getSampleStyleSheet()
            title = Paragraph("<b>Relatório Central ONG</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            subtipo = Paragraph(f"<b>Tipo:</b> {tipo.capitalize()}", styles['Heading2'])
            elements.append(subtipo)
            elements.append(Spacer(1, 8))

            # Montar dados e cabeçalhos
            if tipo == 'produtos':
                data = [['ID', 'Nome', 'Categoria', 'Qtde Inicial', 'Qtde Atual', 'Unidade', 'Validade', 'Valor Unit.', 'Valor Total', 'Status']]
                for p in produtos_data:
                    data.append([
                        p['ID'], p['Nome'], p['Categoria'], p['Quantidade Inicial'], p['Quantidade Atual'],
                        p['Unidade'], p['Validade'], p['Valor Unitário'], p['Valor Total'], p['Status']
                    ])
                total = len(produtos_data)
                elements.append(Paragraph(f"<b>Total de Produtos:</b> {total}", styles['Normal']))
            elif tipo == 'categorias':
                data = [['ID', 'Nome', 'Descrição', 'Criado em']]
                for c in categorias_data:
                    data.append([c['ID'], c['Nome'], c['Descrição'], c['Criado em']])
                total = len(categorias_data)
                elements.append(Paragraph(f"<b>Total de Categorias:</b> {total}", styles['Normal']))
            elif tipo == 'movimentacoes':
                data = [['ID', 'Produto', 'Tipo', 'Quantidade', 'Motivo', 'Data', 'Usuário']]
                for m in movimentacoes_data:
                    data.append([m['ID'], m['Produto'], m['Tipo'], m['Quantidade'], m['Motivo'], m['Data'], m['Usuário']])
                total = len(movimentacoes_data)
                elements.append(Paragraph(f"<b>Total de Movimentações:</b> {total}", styles['Normal']))

            elements.append(Spacer(1, 8))
            # Tabela estilizada
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#222')),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#888')),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(table)

            doc.build(elements)
            output.seek(0)
            return send_file(
                output,
                as_attachment=True,
                download_name='relatorio_ong.pdf',
                mimetype='application/pdf'
            )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Erro ao gerar relatório: {str(e)}'}), 500

# === ROTAS DE PRODUTOS ===

@main_bp.route('/api/produtos')
@csrf.exempt
def api_produtos():
    """API para listar produtos com paginação e filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        filtro_nome = request.args.get('nome')
        filtro_categoria_id = request.args.get('categoria_id', type=int)
        filtro_quantidade = request.args.get('quantidade')
        filtro_status = request.args.get('status')

        query = Produto.query.order_by(Produto.nome)

        if filtro_nome:
            query = query.filter(Produto.nome.ilike(f'%{filtro_nome}%'))
        if filtro_categoria_id:
            query = query.filter(Produto.categoria_id == filtro_categoria_id)
        if filtro_quantidade:
            if filtro_quantidade == 'baixa':
                query = query.filter(Produto.quantidade_atual < 10)
            elif filtro_quantidade == 'media':
                query = query.filter(Produto.quantidade_atual >= 10, Produto.quantidade_atual <= 50)
            elif filtro_quantidade == 'alta':
                query = query.filter(Produto.quantidade_atual > 50)
        if filtro_status:
            query = query.filter(Produto.status_validade == filtro_status)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        produtos = pagination.items

        return jsonify({
            'produtos': [{
                'id': p.id,
                'nome': p.nome,
                'descricao': p.descricao,
                'quantidade_inicial': p.quantidade_inicial,
                'quantidade_atual': p.quantidade_atual,
                'unidade': p.unidade,
                'data_validade': p.data_validade.isoformat() if p.data_validade else None,
                'valor_unitario': float(p.valor_unitario or 0),
                'categoria_id': p.categoria_id,
                'categoria_nome': p.categoria_ref.nome if p.categoria_ref else 'Sem categoria',
                'localizacao': p.localizacao,
                'codigo_barras': p.codigo_barras,
                'status': p.status,
                'dias_restantes': p.dias_restantes,
                'status_validade': p.status_validade,
                'valor_total': p.valor_total
            } for p in produtos],
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    except Exception as e:
        print(f"❌ Erro na API produtos: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/produtos', methods=['POST'])
@csrf.exempt
def criar_produto():
    """Criar novo produto"""
    try:
        data = request.get_json()
        
        produto = Produto(
            nome=data['nome'],
            descricao=data.get('descricao'),
            quantidade_inicial=data['quantidade_inicial'],
            quantidade_atual=data['quantidade_inicial'],
            unidade=data['unidade'],
            data_validade=datetime.strptime(data['data_validade'], '%Y-%m-%d').date(),
            valor_unitario=data.get('valor_unitario', 0),
            categoria_id=data['categoria_id'],
            localizacao=data.get('localizacao'),
            codigo_barras=data.get('codigo_barras')
        )
        
        db.session.add(produto)
        db.session.commit()
        
        print(f"✅ Produto criado: {produto.nome} (ID: {produto.id})")  # Debug
        return jsonify({
            'success': True, 
            'message': 'Produto criado com sucesso!',
            'id': produto.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar produto: {e}")  # Debug
        return jsonify({'success': False, 'message': f'Erro ao criar produto: {str(e)}'}), 500

@main_bp.route('/api/produtos/<int:produto_id>', methods=['PUT'])
@csrf.exempt
def atualizar_produto(produto_id):
    """Atualizar produto existente"""
    produto = Produto.query.get_or_404(produto_id)
    data = request.get_json()
    
    produto.nome = data['nome']
    produto.descricao = data.get('descricao')
    produto.quantidade_atual = data['quantidade_atual']
    produto.unidade = data['unidade']
    produto.data_validade = datetime.strptime(data['data_validade'], '%Y-%m-%d').date()
    produto.valor_unitario = data.get('valor_unitario', 0)
    produto.categoria_id = data['categoria_id']
    produto.localizacao = data.get('localizacao')
    produto.codigo_barras = data.get('codigo_barras')
    

    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Produto atualizado com sucesso!'})

@main_bp.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
@csrf.exempt
def deletar_produto(produto_id):
    """Deletar produto"""
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Produto removido com sucesso!'})

# === ROTAS DE CATEGORIAS ===

@main_bp.route('/api/categorias')
@csrf.exempt
def api_categorias():
    """API para listar categorias"""
    categorias = Categoria.query.all()
    return jsonify([{
        'id': c.id,
        'nome': c.nome,
        'descricao': c.descricao,
        'produtos_count': len(c.produtos),
        'created_at': c.created_at.isoformat() if c.created_at else None
    } for c in categorias])

@main_bp.route('/api/categorias', methods=['POST'])
@csrf.exempt
def criar_categoria():
    """Criar nova categoria"""
    try:
        data = request.get_json()
        
        categoria = Categoria(
            nome=data['nome'],
            descricao=data.get('descricao')
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        print(f"✅ Categoria criada: {categoria.nome} (ID: {categoria.id})")  # Debug
        return jsonify({'success': True, 'message': 'Categoria criada com sucesso!'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar categoria: {e}")  # Debug
        return jsonify({'success': False, 'message': f'Erro ao criar categoria: {str(e)}'}), 500

@main_bp.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
@csrf.exempt
def atualizar_categoria(categoria_id):
    """Atualizar categoria existente"""
    categoria = Categoria.query.get_or_404(categoria_id)
    data = request.get_json()
    
    categoria.nome = data['nome']
    categoria.descricao = data.get('descricao')
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Categoria atualizada com sucesso!'})

@main_bp.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
@csrf.exempt
def deletar_categoria(categoria_id):
    """Deletar categoria"""
    categoria = Categoria.query.get_or_404(categoria_id)
    
    # Permitir exclusão se todos os produtos associados tiverem estoque 0
    produtos_ativos = [p for p in categoria.produtos if p is not None and p.quantidade_atual > 0]
    if produtos_ativos:
        return jsonify({'success': False, 'message': 'Não é possível excluir categoria com produtos associados com estoque maior que 0!'})

    # Deletar explicitamente todos os produtos associados (mesmo com estoque 0)
    for produto in list(categoria.produtos):
        db.session.delete(produto)

    db.session.delete(categoria)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Categoria removida com sucesso!'})

# === ROTAS DE MOVIMENTAÇÕES ===

@main_bp.route('/api/movimentacoes')
@csrf.exempt
def api_movimentacoes():
    """API para listar movimentações com paginação e filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        filtro_produto_id = request.args.get('produto_id', type=int)
        filtro_tipo = request.args.get('tipo')
        filtro_motivo = request.args.get('motivo')
        filtro_data_inicio = request.args.get('data_inicio')
        filtro_data_fim = request.args.get('data_fim')
        filtro_usuario = request.args.get('usuario')

        query = Movimentacao.query.order_by(desc(Movimentacao.data_movimentacao))

        if filtro_produto_id:
            query = query.filter(Movimentacao.produto_id == filtro_produto_id)
        if filtro_tipo:
            query = query.filter(Movimentacao.tipo == filtro_tipo)
        if filtro_motivo:
            query = query.filter(Movimentacao.motivo == filtro_motivo)
        if filtro_data_inicio:
            try:
                dt_inicio = datetime.strptime(filtro_data_inicio, "%Y-%m-%d")
                query = query.filter(Movimentacao.data_movimentacao >= dt_inicio)
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de data de início inválido. Use YYYY-MM-DD.'}), 400
        if filtro_data_fim:
            try:
                dt_fim = datetime.strptime(filtro_data_fim, "%Y-%m-%d")
                query = query.filter(Movimentacao.data_movimentacao <= dt_fim)
            except ValueError:
                return jsonify({'success': False, 'message': 'Formato de data de fim inválido. Use YYYY-MM-DD.'}), 400
        if filtro_usuario:
            query = query.filter(Movimentacao.usuario.ilike(f'%{filtro_usuario}%'))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        movimentacoes = pagination.items

        return jsonify({
            'movimentacoes': [{
                'id': m.id,
                'produto_id': m.produto_id,
                'produto_nome': m.produto_ref.nome if m.produto_ref else 'Produto não encontrado',
                'tipo': m.tipo,
                'quantidade': m.quantidade,
                'motivo': m.motivo,
                'observacoes': m.observacoes,
                'data_movimentacao': m.data_movimentacao.isoformat() if m.data_movimentacao else None,
                'usuario': m.usuario
            } for m in movimentacoes],
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        })
    except Exception as e:
        print(f"❌ Erro na API movimentacoes: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/movimentacoes', methods=['POST'])
@csrf.exempt
def criar_movimentacao():
    """Criar nova movimentação"""
    data = request.get_json()
    produto = Produto.query.get_or_404(data['produto_id'])

    quantidade = data.get('quantidade', 0)
    if quantidade <= 0:
        return jsonify({'success': False, 'message': 'Quantidade inválida!'}), 400

    if data['tipo'] == 'saida':
        if produto.quantidade_atual <= 0:
            return jsonify({'success': False, 'message': 'Produto sem estoque!'}), 400
        if produto.quantidade_atual < quantidade:
            return jsonify({'success': False, 'message': 'Quantidade insuficiente em estoque!'}), 400
        produto.quantidade_atual -= quantidade
    elif data['tipo'] == 'entrada':
        produto.quantidade_atual += quantidade
    else:
        return jsonify({'success': False, 'message': 'Tipo de movimentação inválido!'}), 400

    # Garante que a quantidade nunca fique negativa
    if produto.quantidade_atual < 0:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro: Estoque não pode ser negativo!'}), 400

    # DEBUG: Exibe o valor recebido do frontend
    print(f"Recebido data_movimentacao: {data.get('data_movimentacao')}")
    data_mov = None
    if data.get('data_movimentacao'):
        try:
            data_mov = datetime.strptime(data['data_movimentacao'], "%Y-%m-%d")
        except Exception as e:
            print(f"Erro ao converter data_movimentacao: {e}")
            return jsonify({'success': False, 'message': f'Data da movimentação inválida: {str(e)}'}), 400
    movimentacao = Movimentacao(
        produto_id=data['produto_id'],
        tipo=data['tipo'],
        quantidade=quantidade,
        motivo=data['motivo'],
        observacoes=data.get('observacoes'),
        usuario=data.get('usuario', 'Sistema'),
        data_movimentacao=data_mov
    )
    db.session.add(movimentacao)
    db.session.commit()
    return jsonify({'success': True, 'movimentacao_id': movimentacao.id})

# === ROTAS DE DASHBOARD ===

@main_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """Estatísticas para o dashboard"""
    hoje = date.today()
    
    # Contar produtos por status de validade
    produtos = Produto.query.all()
    stats = {
        'vencidos': 0,
        'sete_dias': 0,   # Agora inclui até 7 dias (não mais 3 dias)
        'trinta_dias': 0,
        'total_produtos': len(produtos)
    }
    
    for produto in produtos:
        dias = produto.dias_restantes
        if dias < 0:
            stats['vencidos'] += 1
        elif dias <= 7:    # Mudou de <= 3 para <= 7
            stats['sete_dias'] += 1
        elif dias <= 30:
            stats['trinta_dias'] += 1
    
    return jsonify(stats)

@main_bp.route('/api/dashboard/chart-data')
def dashboard_chart_data():
    """Dados para gráficos do dashboard"""
    categorias = Categoria.query.all()
    chart_data = []
    
    for categoria in categorias:
        chart_data.append({
            'label': categoria.nome,
            'count': len(categoria.produtos)
        })
    
    return jsonify(chart_data)

@main_bp.route('/api/dashboard/product-status-chart')
def product_status_chart_data():
    """Dados para o gráfico de status de produtos"""
    produtos = Produto.query.all()
    status_data = {
        'vencido': 0,
        'urgente': 0,  # Agora urgente inclui até 7 dias
        'proximo': 0,
        'ok': 0
    }
    
    for produto in produtos:
        status = produto.status_validade
        if status in status_data:
            status_data[status] += 1
    
    # Reagrupando para o gráfico com nova lógica - 4 categorias
    chart_data = {
        'Vencidos': status_data['vencido'],
        'Vencem em 7 dias': status_data['urgente'],
        'Vencem em 30 dias': status_data['proximo'],
        'Ok': status_data['ok']
    }
    
    return jsonify(chart_data)

# === ROTAS DE RELATÓRIOS ===

@main_bp.route('/api/relatorios/validades')
def relatorio_validades():
    """Relatório de produtos próximos ao vencimento"""
    filtro = request.args.get('filtro', 'all')
    
    produtos = Produto.query.all()
    dados = []
    
    for produto in produtos:
        status = produto.status_validade
        
        if filtro == 'all' or filtro == status:
            categoria = produto.categoria_ref
            dados.append({
                'nome': produto.nome,
                'categoria': categoria.nome if categoria else 'N/A',
                'data_validade': produto.data_validade.strftime('%d/%m/%Y'),
                'dias_restantes': produto.dias_restantes,
                'quantidade': produto.quantidade_atual,
                'unidade': produto.unidade,
                'valor_total': produto.valor_total,
                'status': status
            })
    
    return jsonify(dados)

# === ROTAS DE EVENTOS ===

@main_bp.route('/api/eventos', methods=['GET'])
def get_eventos():
    eventos = Evento.query.all()
    return jsonify([{
        'id': e.id,
        'nome': e.nome,
        'descricao': e.descricao,
        'data': e.data.isoformat(),
        'categoria': e.categoria,
        'status': e.status
    } for e in eventos])

@main_bp.route('/api/eventos/<int:evento_id>', methods=['GET'])
def get_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    return jsonify({
        'id': evento.id,
        'nome': evento.nome,
        'descricao': evento.descricao,
        'data': evento.data.isoformat(),
        'categoria': evento.categoria,
        'status': evento.status
    })

@main_bp.route('/api/eventos', methods=['POST'])
def create_evento():
    data = request.get_json()
    if not data or not all(k in data for k in ('nome', 'data', 'categoria', 'status')):
        abort(400)
    evento = Evento(
        nome=data['nome'],
        descricao=data.get('descricao'),
        data=datetime.fromisoformat(data['data']).date(),
        categoria=data['categoria'],
        status=data['status']
    )
    db.session.add(evento)
    db.session.commit()
    return jsonify({'id': evento.id}), 201

@main_bp.route('/api/eventos/<int:evento_id>', methods=['PUT'])
def update_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    data = request.get_json()
    for field in ['nome', 'descricao', 'data', 'categoria', 'status']:
        if field in data:
            if field == 'data':
                setattr(evento, field, datetime.fromisoformat(data[field]).date())
            else:
                setattr(evento, field, data[field])
    db.session.commit()
    return jsonify({'msg': 'Evento atualizado'})

@main_bp.route('/api/eventos/<int:evento_id>', methods=['DELETE'])
def delete_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    return jsonify({'msg': 'Evento removido'})

# === MANTER ROTAS ANTIGAS PARA COMPATIBILIDADE ===

@main_bp.route('/evento/novo', methods=['GET', 'POST'])
def novo_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento(
            nome=form.nome.data,
            descricao=form.descricao.data,
            data=form.data.data,
            categoria=form.categoria.data,
            status=form.status.data
        )
        db.session.add(evento)
        db.session.commit()
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    return render_template('modal_form.html', form=form)

@main_bp.route('/evento/<int:evento_id>/editar', methods=['GET', 'POST'])
def editar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        form.populate_obj(evento)
        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    return render_template('modal_form.html', form=form, evento=evento)

@main_bp.route('/evento/<int:evento_id>/deletar', methods=['POST'])
def deletar_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento removido com sucesso!', 'success')
    return redirect(url_for('main.index'))
