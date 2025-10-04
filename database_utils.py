import sqlite3


def initialize_db():
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS MyVocab (
            id integer primary key autoincrement,
            cat1 text not null,
            cat2 text default '',
            word text not null unique,
            pronunciation text,
            meaning text not null,
            note text,
            example text default '',
            star integer default 0,
            synonym text default '',
            antonym text default '',
            img text null,
            search_date date not null
        );
    """)

    con.close()

def get_data():
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    res = cur.execute("""
        SELECT cat1, cat2, word, pronunciation, meaning, note, example, star, synonym, antonym, img, search_date FROM MyVocab;
    """)
    return res.fetchall()

def insert_data(records):
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    cur.execute("BEGIN TRANSACTION;")
    stmt = """
            INSERT INTO MyVocab(cat1, cat2, word, pronunciation, meaning, note, example, synonym, antonym, img, search_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
    cur.executemany(stmt, records)
    
    con.commit()
    con.close()

def delete_data(words):   
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    cur.execute(f"""
        DELETE FROM MyVocab
        WHERE word IN ({words});
    """)

    con.commit()
    con.close()

def retrieve_data_by_date(date):
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    res = cur.execute(f"""
        SELECT * FROM MyVocab
        WHERE search_date='{date}';
    """)
    return res.fetchall()

def update_data(word, set_clause):
    con = sqlite3.connect("my_vocab.db")
    cur = con.cursor()

    cur.execute(f"""
        UPDATE MyVocab
        SET {set_clause}
        WHERE word='{word}';
    """)

    con.commit()
    con.close()