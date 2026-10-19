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
        quantidade INTEGER,
        capa TEXT NOT NULL
    );
    '''
cursor.execute(create_table)
connection.commit()

# preenche o bd
cursor.execute("SELECT COUNT(*) FROM Livros")
if cursor.fetchone()[0] == 0:
    livros = [
        ("l01", "O Retrato de Dorian Gray", "Oscar Wilde", "Romance", 60.40, 10, "https://ecx.images-amazon.com/images/P/0199535981.01._SX600_SY1200_SCRM_.jpg",), 
        ("l02", "Atelier of Witch", "Kamone", "Quadrinhos", 38, 5, "https://pics.cdn.librarything.com/picsizes/11/85/11859807-b-h1200-w600-pv25_596c2f337441425941724145_v5.jpg",),
        ("l03", "Vidas Secas", "Graciliano Ramos", "Romance", 25, 5, "https://pics.cdn.librarything.com/picsizes/16/21/16219043-b-h1200-w600-pv25_59714e373977425941724145_v5.jpg",), 
        ("l04", "Misery", "Stephen King", "Terror", 40, 1, "https://pics.cdn.librarything.com/picsizes/53/07/5307936-c-h1200-w600-pv25_5979442b5541425941724145_v5.jpg",), 
        ("l05", "Mrs. Dalloway", "Virginia Woolf", "Romance", 41.24, 15, "https://ecx.images-amazon.com/images/P/0199536007.01._SX600_SY1200_SCRM_.jpg",)
    ]

    cursor.executemany (
    'INSERT INTO Livros (id, titulo, autor, categoria, preco, quantidade, capa) VALUES (?, ?, ?, ?, ?, ?, ?)', 
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

# nova funcao que vai ser chamada para a api 
# lista todos os produtos que estao em estoque
def consulta_produtos():
    produtos = cursor.execute("SELECT * from Livros WHERE quantidade > 0")
    return produtos