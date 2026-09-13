import sqlite3, os

# cria o bd
diretorio = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(diretorio, "estoque.db")

with sqlite3.connect(caminho) as connection:
    cursor = connection.cursor()

    create_table = '''
    CREATE TABLE IF NOT EXISTS Livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        categoria TEXT NOT NULL,
        preco DECIMAL (10, 2),
        quantidade INTEGER
    );
    '''
    cursor.execute(create_table)
    connection.commit()

    # preencher o banco de dados
    livros = [
        ("O Retrato de Dorian Gray", "Oscar Wilde", "Romance", 60.40, 10), 
        ("O Hobbit", "J.R.R Tolkien", "Romance", 50, 1),
        ("A Figura", "Natalia Grecco", "Terror", 56, 4),  
        ("Misery", "Stephen King", "Terror", 40, 0), 
        ("Joy", "Etsuko", "Quadrinhos", 30.00, 2),
        ("Define The Relationship", "Flona", "Quadrinhos", 76.80, 3),
        ("Vidas Secas", "Graciliano Ramos", "Romance", 25, 6), 
        ("Mrs. Dalloway", "Virginia Woolf", "Romance", 41.24, 15),
        ("Frankenstein", "Mary Shelley", "Terror", 35, 2),  
        ("Drácula", "Bram Stoker", "Terror", 42, 0), 
        ("Atelier of Witch", "Kamone", "Quadrinhos", 38, 5),
        ("Nana", "Ai Yazawa", "Quadrinhos", 26.30, 3),
    ]

    cursor.executemany (
    'INSERT INTO Livros (titulo, autor, categoria, preco, quantidade) VALUES (?, ?, ?, ?, ?)', 
    livros )

    connection.commit()


    # funcoes para manipulacao do bd para o servico estoque
    def verifica_estoque(livros):
        # abro bd

        # com o id dos livros faco uma consultado do quantidade.
        # se algum da lista tiver com estoque zerado, retorno false ou id dos livros sem estoque
        pass

    def devolver_produto(livros):
        pass

   

    def reserve_produto(livros):
        pass