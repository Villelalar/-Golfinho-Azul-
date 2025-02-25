from flask import Flask, render_template
import pymysql
app = Flask(__name__)

# Configuração do banco de dados
def get_users():
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",
            host="localhost",
            password="mochi",
            port=3306,
            user="root",
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
        return users
    except Exception as e:
        print("Erro ao conectar:", e)
        return []
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/')
def index():
    users = get_users()
    return render_template('home.html', output_data=users)

@app.route('/test')
def test_route():
    users = get_users()
    return render_template('test.html', output_data=users)

if __name__ == '__main__':
    app.run(debug=True)
