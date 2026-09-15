import sqlite3, os

# cria o bd
diretorio = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(diretorio, "estoque.db")

connection = sqlite3.connect(caminho, check_same_thread=False)
cursor = connection.cursor()

create_table = '''
    CREATE TABLE IF NOT EXISTS Livros (
        id TEXT, 
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT NOT NULL,
        preco DECIMAL (10, 2),
        quantidade INTEGER
    );
    '''
cursor.execute(create_table)
connection.commit()

# preenche o bd
cursor.execute("SELECT COUNT(*) FROM Livros")
if cursor.fetchone()[0] == 0:
    livros = [
        ("l01", "O Retrato de Dorian Gray", "Oscar Wilde", "Romance", 60.40, 10), 
        ("l02", "Atelier of Witch", "Kamone", "Quadrinhos", 38, 5),
        ("l03", "Vidas Secas", "Graciliano Ramos", "Romance", 25, 5), 
        ("l04", "Misery", "Stephen King", "Terror", 40, 1), 
        ("l05", "Mrs. Dalloway", "Virginia Woolf", "Romance", 41.24, 15)
    ]

    cursor.executemany (
    'INSERT INTO Livros (id, titulo, autor, categoria, preco, quantidade) VALUES (?, ?, ?, ?, ?, ?)', 
    livros )

    connection.commit()

# funcoes para manipular o estoque
def verificar_estoque(pedidos): 
    for pedido in pedidos:
        id_livro = pedido["id_livro"] 
        quantidade = pedido["quantidade"]
        
        cursor.execute("SELECT quantidade FROM Livros WHERE id = ?", (id_livro,))
        estoque = cursor.fetchone()
        
        if estoque is None or estoque[0] < quantidade:
            return False
    return True 

def devolver_produto(pedidos):
    for pedido in pedidos:
        id_livro = pedido["id_livro"]
        quantidade = pedido["quantidade"]
        cursor.execute("UPDATE Livros SET quantidade = quantidade + ? WHERE id = ?", (quantidade, id_livro,))
    connection.commit()

def reservar_produto(pedidos):
    for pedido in pedidos:
        id_livro = pedido["id_livro"]
        quantidade = pedido["quantidade"]
        cursor.execute("UPDATE Livros SET quantidade = quantidade - ? WHERE id = ?", (quantidade, id_livro,))
    connection.commit()