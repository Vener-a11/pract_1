from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('books.db')
    conn.row_factory = sqlite3.Row  # Для удобного доступа к колонкам
    return conn

# Создание таблицы при первом запуске
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER,
            genre TEXT,
            copies INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    
    # Подсчет метрик для шапки (как на картинке)
    total_books = len(books)
    total_copies = sum(book['copies'] for book in books)
    total_genres = len(set(book['genre'] for book in books if book['genre']))
    total_authors = len(set(book['author'] for book in books))
    
    conn.close()
    
    return render_template('index.html', 
                         books=books,
                         total_books=total_books,
                         total_copies=total_copies,
                         total_genres=total_genres,
                         total_authors=total_authors)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        year = request.form.get('year', type=int)
        genre = request.form['genre']
        copies = request.form.get('copies', type=int)
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO books (title, author, year, genre, copies) VALUES (?, ?, ?, ?, ?)',
            (title, author, year, genre, copies)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_book.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    books = conn.execute(
        'SELECT * FROM books WHERE title LIKE ? OR author LIKE ?',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('index.html', books=books, search_query=query)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
