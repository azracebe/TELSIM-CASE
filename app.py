from flask import Flask, render_template, request
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temp REAL,
            condition TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        
        api_key = "cd1d7d96faed4a41acc221120252406"  
        api_url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q=Nicosia"
        
        try:
            response = requests.get(api_url)
            data = response.json()

            # SQLite'a kaydet
            conn = get_db()
            conn.execute('''
                INSERT INTO weather (city, temp, condition, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (
                data['location']['name'],
                data['current']['temp_c'],
                data['current']['condition']['text'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
            
            message = "Veri başarıyla kaydedildi!"
        except Exception as e:
            message = f"Hata: {e}"
    else:
        message = None

   
    conn = get_db()
    last_record = conn.execute('SELECT * FROM weather ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()

    return render_template('index.html', message=message, record=last_record)

if __name__ == '__main__':
    app.run(debug=True)