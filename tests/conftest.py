import pytest
from app import create_app, db
from app.models import Categoria

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('app.config.TestingConfig')

    # Criar um contexto de aplicação
    with flask_app.app_context():
        db.create_all()
        # Criar uma categoria de teste
        categoria = Categoria(nome='Teste', descricao='Categoria de teste')
        db.session.add(categoria)
        db.session.commit()

        yield flask_app.test_client()  # Retorna o cliente de teste

        db.session.remove()
        db.drop_all()