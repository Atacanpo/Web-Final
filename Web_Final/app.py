
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)


secret_key = secrets.token_hex(24)


app.secret_key = secret_key

DATABASE = 'database.db'

def connect_db():
    return sqlite3.connect(DATABASE)


@app.route('/')
def index():
    db = connect_db()

    db.execute('''
       CREATE TABLE IF NOT EXISTS hotel (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          hotel_name TEXT NOT NULL,
          hotel_price REAL NOT NULL,
          hotel_amenities TEXT NOT NULL,
          hotel_comments REAL,
          hotel_location TEXT NOT NULL,
          hotel_rating REAL NOT NULL,
          hotel_memberPrice REAL,
          hotel_country TEXT NOT NULL,
          hotel_city TEXT NOT NULL,
          hotel_discount REAL,
          ImageURL TEXT
       );
    ''')
    
    

    db.execute('DELETE FROM hotel')

    db.execute('''
        INSERT INTO hotel (hotel_name, hotel_price, hotel_amenities, hotel_comments, hotel_location, hotel_rating, hotel_memberPrice, hotel_country, hotel_city, hotel_discount, ImageURL) VALUES
            ('Sundia Exclusive By Liberty Fethiye', '8000', 'restoran,havuz,bar,Spa', '5432', 'Güzeloba Mah. Yaşar Sobutay Mah. No.: 30, Lara, Antalya, Antalya, 07235', '9.2 Olağanüstü', ' 7200', 'Turkey', 'İzmir', '%10 ', 'https://images.trvl-media.com/lodging/68000000/67420000/67416300/67416227/e1f70e7d.jpg?impolicy=resizecrop&rw=1200&ra=fit'),
            ('Villa Doga', '9000', 'restoran,havuz,Wi-Fi,bar,Spa', '2342', 'Akdeniz Bulvarı No.: 104, Konyaaltı, Antalya, 0707', '7.9 İyi', '8100', 'Turkey', 'Antalya', '%10', 'https://images.trvl-media.com/lodging/31000000/30360000/30352900/30352824/f6725eba.jpg?impolicy=resizecrop&rw=1200&ra=fit'),
            ('Casa Margot Hotel', '10000', 'restoran,havuz,bar,Spa', '1232', 'Karagözler, Abdi İpekçi Cd. No:23, 48300 İstanbul, Adalar, 34353', '9 Mükemmel', '9000', 'Turkey', 'İstanbul', '%10', 'https://images.trvl-media.com/lodging/21000000/20520000/20517900/20517810/b87c4f43.jpg?impolicy=resizecrop&rw=1200&ra=fit'),
            ('Alesta Seaside Residence', '12000', 'restoran,havuz,bar,Spa', '34532', 'Foça, Barış Manço Blv. No: 107 A/A, 48300 İzmir, Foça', '8.7 Çok İyi', '10800', 'Turkey', 'İzmir', '%10', 'https://images.trvl-media.com/lodging/77000000/76380000/76377600/76377511/c44365f3.jpg?impolicy=resizecrop&rw=1200&ra=fit'),
            ('Ada Dreams History ', '13000', 'restoran,havuz,bar,Spa', '3234', 'Kayaköy, Belen caddesi No: 80, 48300 İstanbul ,Şişli , 34353', '7 İyi', '11700', 'Turkey', 'İstanbul', '%10', 'https://images.trvl-media.com/lodging/76000000/75950000/75947000/75946931/9251a09d.jpg?impolicy=resizecrop&rw=1200&ra=fit')
    ''')

    db.commit()

    destination_city = request.args.get('destination_city')
    

    if destination_city is None:
        query = '''
            SELECT * FROM hotel
            ORDER BY hotel_price DESC
        '''
        cursor = db.execute(query)
        hotels = cursor.fetchall()
        db.close()

        return render_template('index.html', hotels=hotels)

    query = '''
        SELECT * FROM hotel
        WHERE hotel_city = ?
        ORDER BY hotel_price DESC
    '''
    cursor = db.execute(query, (destination_city,))
    hotels = cursor.fetchall()
    db.close()

    return render_template('index.html', hotels=hotels)

@app.route('/detail/<int:hotel_id>')
def detail(hotel_id):
    db = connect_db()

    query = '''
        SELECT * FROM hotel
        WHERE id = ?
    '''
    cursor = db.execute(query, (hotel_id,))
    hotel = cursor.fetchone()
    db.close()

    return render_template('detail.html', hotel=hotel)



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = connect_db()
        query = '''
            SELECT * FROM users
            WHERE email = ?
        '''
        cursor = db.execute(query, (email,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user[4], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]  
            return redirect(url_for('index'))
        else:
            error = 'Invalid email or password. Please try again.'

    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['Name']
        surname = request.form['surName']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        db = connect_db()

        db.execute('''
           CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              surname TEXT NOT NULL,
              email TEXT NOT NULL,
              password TEXT NOT NULL
           );
        ''')

        query = '''
            INSERT INTO users (name, surname, email, password)
            VALUES (?, ?, ?, ?)
        '''
        db.execute(query, (name, surname, email, hashed_password))
        db.commit()
        db.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)