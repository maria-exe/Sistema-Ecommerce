import sqlite3, os

# cria o bd
diretorio = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(diretorio, "estoque.db")

with sqlite3.connect(caminho) as connection:
    cursor = connection.cursor()

    create_table = '''
    CREATE TABLE IF NOT EXISTS Produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        produto TEXT NOT NULL,
        categoria TEXT NOT NULL,
        preco DECIMAL (10, 2),
        quantidade INTEGER
    );
    '''

    cursor.execute(create_table)

    connection.commit()