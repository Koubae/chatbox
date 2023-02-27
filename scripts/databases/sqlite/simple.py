import sqlite3


DB_NAME = "simple.db"
TABLE_MOVE = """CREATE TABLE IF NOT EXISTS MOVIE(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title,
    year,
    score
)
"""


def main():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    # create table movie
    cursor.execute(f"{TABLE_MOVE}")
    # verify table creation
    res = cursor.execute("SELECT name FROM sqlite_master")
    table = res.fetchone()
    print(f"Table: {table}")
    # populate movies
    cursor.execute("""INSERT INTO movie(title, year, score)
        VALUES
            ('Monty Python and the Holy Grail', 1975, 8.2),
            ('And Now for Something Completely Different', 1971, 7.5)
    """)
    connection.commit()

    # select movies
    res = cursor.execute("SELECT * FROM movie")
    movies = res.fetchall()
    print(f"Movies:\n{movies}")

    # insert multiple movies
    data = [
        ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
        ("Monty Python's The Meaning of Life", 1983, 7.5),
        ("Monty Python's Life of Brian", 1979, 8.0),
    ]
    cursor.executemany("INSERT INTO movie(title, year, score) VALUES(?, ?, ?)", data)
    connection.commit()
    for row in cursor.execute("SELECT * FROM movie ORDER BY id DESC"):
        print(row)



if __name__ == '__main__':
    main()