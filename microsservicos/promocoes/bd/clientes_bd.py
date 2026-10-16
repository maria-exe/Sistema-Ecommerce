import sqlite3, os

# cria o bd
diretorio = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(diretorio, "estoque.db")

connection = sqlite3.connect(caminho, check_same_thread=False)
cursor = connection.cursor()

create_table = '''
    CREATE TABLE IF NOT EXISTS Interesses (
        email TEXT NOT NULL, 
        categoria TEXT NOT NULL
        PRIMARY KEY (email, categoria)
    );
    '''

cursor.execute(create_table)
connection.commit()

def registra(email, categoria):
    cursor.execute("INSERT OR IGNORE INTO Interesses VALUES (?, ?)", 
                   (email.lower(), categoria,),
    )
    connection.commit()

def apaga_registro(email, categoria):
    email = email.lower()
    if categoria: 
        cursor.execute("DELETE FROM Interesses WHERE email = ? AND categoria = ?", 
                       (email, categoria),
        )
    else: 
        cursor.execute("DELETE FROM Interesses WHERE email = ?", 
                        (email,),
        )
    connection.commit()

def interesses():
    pass