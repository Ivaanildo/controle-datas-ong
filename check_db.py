from app import create_app, db
from app.models import Produto, Categoria, Movimentacao

app = create_app()
app.app_context().push()

print("Verificando dados no banco de dados...")

try:
    produtos_count = db.session.query(Produto).count()
    categorias_count = db.session.query(Categoria).count()
    movimentacoes_count = db.session.query(Movimentacao).count()

    print(f"Produtos: {produtos_count} registros")
    print(f"Categorias: {categorias_count} registros")
    print(f"Movimentacoes: {movimentacoes_count} registros")

except Exception as e:
    print(f"Erro ao acessar o banco de dados: {e}")

db.session.remove()
