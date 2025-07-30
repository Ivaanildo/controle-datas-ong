import sqlite3
from datetime import datetime

conn = sqlite3.connect('instance/app.db')
c = conn.cursor()
categorias = [
    ('Alimentos Perecíveis', 'Produtos com validade curta, como frutas, verduras, carnes, laticínios'),
    ('Alimentos Não Perecíveis', 'Produtos com validade longa, como arroz, feijão, enlatados, massas'),
    ('Higiene e Limpeza', 'Produtos de higiene pessoal e limpeza'),
    ('Outros', 'Outros tipos de produtos')
]
now = datetime.now().isoformat(' ')
for nome, desc in categorias:
    c.execute('INSERT INTO categorias (nome, descricao, created_at) VALUES (?, ?, ?)', (nome, desc, now))
conn.commit()
conn.close()
print('Categorias cadastradas.')
