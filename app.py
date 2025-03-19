from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__)

# Função para obter usuários do banco de dados
def get_data(database_name, table_name):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db=database_name,  # Agora escolhemos o banco dinamicamente
            host="HOST",
            password="SENHA",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
        return data
    except Exception as e:
        print(f"Erro ao conectar na tabela {table_name} do banco {database_name}: {e}")
        return []
    finally:
        if 'connection' in locals():
            connection.close()


# Função para adicionar um usuário ao banco de dados
def add_user_to_db(user_id, name, email, phone):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",
            host="HOST",
            password="SENHA",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (id, name, email, phone) VALUES (%s, %s, %s, %s)",
                           (user_id, name, email, phone))
            connection.commit()
    except Exception as e:
        print(f"Erro ao adicionar usuário: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

# Rota para a página principal
@app.route('/')
def index():
    users = get_data("defaultdb","users")  # Buscando os usuários para exibição
    return render_template('home.html', users=users)

# Rota para adicionar um usuário via AJAX
@app.route('/add_user', methods=['POST'])
def add_user():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    if user_id and name and email and phone:
        add_user_to_db(user_id, name, email, phone)
        return jsonify({'status': 'success', 'user': {'id': user_id, 'name': name, 'email': email, 'phone': phone}})
    else:
        return jsonify({'status': 'error', 'message': 'Todos os campos são obrigatórios!'})

if __name__ == '__main__':
    app.run(debug=True)
