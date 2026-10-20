import sqlite3, os

# cria o bd
diretorio = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(diretorio, "estoque.db")

connection = sqlite3.connect(caminho, check_same_thread=False)
cursor = connection.cursor()

cursor.execute ('''
    CREATE TABLE IF NOT EXISTS Livros (
        id TEXT PRIMARY KEY, 
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT NOT NULL,
        preco DECIMAL (10, 2),
        quantidade INTEGER,
        capa TEXT NOT NULL
    );
    ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reservas (
        id_pedido TEXT PRIMARY KEY
    );
''')

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

def pedido_reservado(id_pedido):
    cursor.execute("SELECT 1 FROM Reservas WHERE id_pedido = ?", (id_pedido,))
    return cursor.fetchone() is not None

def reservar_pedido(id_pedido, pedidos):
    try:
        for p in pedidos:
            cursor.execute(
                "UPDATE Livros SET quantidade = quantidade - ? "
                "WHERE id = ? AND quantidade >= ?",
                (p["quantidade"], p["id_livro"], p["quantidade"]),
            )
            if cursor.rowcount == 0:        
                connection.rollback()      
                return False

        cursor.execute("INSERT INTO Reservas (id_pedido) VALUES (?)", (id_pedido,))
        connection.commit()
        return True
    
    except Exception:
        connection.rollback()
        raise

def devolver_pedido(id_pedido, pedidos):
    try:
        cursor.execute("DELETE FROM Reservas WHERE id_pedido = ?", (id_pedido,))
        if cursor.rowcount == 0:        
            connection.rollback()
            return False

        for p in pedidos:
            cursor.execute(
                "UPDATE Livros SET quantidade = quantidade + ? WHERE id = ?",
                (p["quantidade"], p["id_livro"]),
            )
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise

def consulta_produtos():
    cursor.execute("SELECT * FROM Livros WHERE quantidade > 0")
    return cursor.fetchall()