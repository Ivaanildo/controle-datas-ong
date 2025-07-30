import json
from datetime import date, timedelta

# Helper para criar um produto via API
def create_product(client, nome, dias_validade):
    validade = date.today() + timedelta(days=dias_validade)
    produto_data = {
        "nome": nome,
        "descricao": f"Descrição para {nome}",
        "quantidade_inicial": 10,
        "unidade": "unidade",
        "data_validade": validade.isoformat(),
        "valor_unitario": 5.0,
        "categoria_id": 1  # Usando a categoria de teste criada em conftest.py
    }
    response = client.post('/api/produtos', data=json.dumps(produto_data), content_type='application/json')
    return response

# Teste 1: Criar um produto vencido e verificar o dashboard
def test_create_expired_product_updates_dashboard(test_client):
    # 1. Obter estatísticas iniciais
    response = test_client.get('/api/dashboard/stats')
    initial_stats = json.loads(response.data)

    # 2. Criar um produto vencido
    response = create_product(test_client, "Produto Vencido", -10)
    assert response.status_code == 200

    # 3. Obter novas estatísticas
    response = test_client.get('/api/dashboard/stats')
    new_stats = json.loads(response.data)

    # 4. Verificar se o contador de vencidos aumentou
    assert new_stats['vencidos'] == initial_stats['vencidos'] + 1

# Teste 2: Criar um produto que vence em 7 dias e verificar o dashboard
def test_create_7_day_product_updates_dashboard(test_client):
    response = test_client.get('/api/dashboard/stats')
    initial_stats = json.loads(response.data)

    create_product(test_client, "Produto Urgente", 5)

    response = test_client.get('/api/dashboard/stats')
    new_stats = json.loads(response.data)

    assert new_stats['sete_dias'] == initial_stats['sete_dias'] + 1

# Teste 3: Criar um produto que vence em 30 dias e verificar o dashboard
def test_create_30_day_product_updates_dashboard(test_client):
    response = test_client.get('/api/dashboard/stats')
    initial_stats = json.loads(response.data)

    create_product(test_client, "Produto OK", 20)

    response = test_client.get('/api/dashboard/stats')
    new_stats = json.loads(response.data)

    assert new_stats['trinta_dias'] == initial_stats['trinta_dias'] + 1

# Teste 4: Atualizar um produto e verificar o dashboard
def test_update_product_updates_dashboard(test_client):
    # Criar produto com validade longa
    response = create_product(test_client, "Produto para Atualizar", 60)
    product_id = json.loads(response.data).get('id')

    response = test_client.get('/api/dashboard/stats')
    initial_stats = json.loads(response.data)

    # Atualizar a data de validade para 3 dias
    validade_curta = (date.today() + timedelta(days=3)).isoformat()
    update_data = {
        "nome": "Produto Atualizado",
        "data_validade": validade_curta,
        "quantidade_atual": 10,
        "unidade": "unidade",
        "categoria_id": 1
    }
    test_client.put(f'/api/produtos/{product_id}', data=json.dumps(update_data), content_type='application/json')

    response = test_client.get('/api/dashboard/stats')
    new_stats = json.loads(response.data)

    assert new_stats['sete_dias'] == initial_stats['sete_dias'] + 1

# Teste 5: Excluir um produto e verificar o dashboard
def test_delete_product_updates_dashboard(test_client):
    # Criar um produto para excluir
    response = create_product(test_client, "Produto para Deletar", -5)
    product_id = json.loads(response.data).get('id')

    response = test_client.get('/api/dashboard/stats')
    initial_stats = json.loads(response.data)

    # Excluir o produto
    test_client.delete(f'/api/produtos/{product_id}')

    response = test_client.get('/api/dashboard/stats')
    new_stats = json.loads(response.data)

    assert new_stats['vencidos'] == initial_stats['vencidos'] - 1
