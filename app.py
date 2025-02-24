from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configuração do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mochi',
    'database': 'oceano_azul'
}

def get_users():
    """Busca os usuários do banco de dados."""
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, email, phone FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/test')
def test_route():
    users = get_users()
    return render_template('test.html', output_data=users)

if __name__ == '__main__':
    app.run(debug=True)
