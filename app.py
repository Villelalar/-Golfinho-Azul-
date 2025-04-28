from flask import Flask, render_template, request, redirect, url_for, flash, json #simplesmente o flask
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql # uso de banco de dados

app = Flask(__name__)
app.secret_key = 'institutooceanoazulXunilasalle'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="logins",
            host="projweb3-projweb3.g.aivencloud.com",
            password="AVNS_J6HaV0sCEBEwuvqBeGP",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
        if user_data:
            return User(id=user_data['id'], username=user_data['username'])
        else:
            return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()

# ROTA PARA PÁGINA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')  # This should be plain text
        try:
            connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor,
                db="logins",
                host="projweb3-projweb3.g.aivencloud.com",
                password="AVNS_J6HaV0sCEBEwuvqBeGP",
                port=19280,
                user="avnadmin",
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()

            # Debugging: Print user data and provided password
            print("User Data:", user_data)
            print("Provided Password (Plain Text):", password)  # Ensure this is plain text

            if user_data:
                # Debugging: Print the hashed password from the database
                print("Hashed Password from DB:", user_data['password_hash'])

                # Verify the password
                if check_password_hash(user_data['password_hash'],password):  # Compare hashed DB password with plain-text password
                    user = User(id=user_data['id'], username=user_data['username'])
                    login_user(user)
                    flash('Logged in successfully.')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password.')
            else:
                flash('Invalid username or password.')
        except Exception as e:
            print(f"Error during login: {e}")
            flash('An error occurred during login.')
        finally:
            if 'connection' in locals():
                connection.close()
    return render_template('login.html')

# e o logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))


# Função para listar as tabelas do banco de dados
def get_tables(database_name):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db=database_name,
            host="projweb3-projweb3.g.aivencloud.com",
            password="AVNS_J6HaV0sCEBEwuvqBeGP",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            # obtem o nome de todas as tabelas
            table_names = [table[f"Tables_in_{database_name}"] for table in tables]
        return table_names
    except Exception as e:
        print(f"Erro ao listar tabelas do banco {database_name}: {e}")
        return []
    finally:
        if 'connection' in locals():
            connection.close()

# Função para obter dados de uma tabela
# usa pymysql e conecta no banco de dados do Aiven
def get_data(database_name, table_name):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db=database_name,
            host="projweb3-projweb3.g.aivencloud.com",
            password="AVNS_J6HaV0sCEBEwuvqBeGP",
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


## ROTAS PARA PÁGINAS REAIS #
# pagina inicial : lista tabelas
@app.route('/')
@login_required
def index():
    tables = get_tables("defaultdb")  # Listar tabelas do banco defaultdb
    return render_template('index.html', tables=tables)

# pagina de tabela específica : exibe dados da tabela
@app.route('/view_table/<table_name>')
@login_required
def view_table(table_name):
    data = get_data("defaultdb", table_name)  # Obter dados da tabela selecionada
    return render_template('view_table.html', table_name=table_name, data=data)

# rota interna que possibilita pesquisa de linha na tabela e retorna o resultado
@app.route('/search', methods=['POST'])
@login_required
def search():
    table_name = request.form.get('table_name')
    search_query = request.form.get('search_query')
    if table_name and search_query:
        try:
            connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor,
                db="defaultdb",
                host="projweb3-projweb3.g.aivencloud.com",
                password="AVNS_J6HaV0sCEBEwuvqBeGP",
                port=19280,
                user="avnadmin",
            )
            with connection.cursor() as cursor:
                # busca dinâmica em todas as colunas da tabela
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = [column['Field'] for column in cursor.fetchall()]
                query = " OR ".join([f"{column} LIKE %s" for column in columns])
                cursor.execute(f"SELECT * FROM {table_name} WHERE {query}", (f"%{search_query}%",) * len(columns))
                results = cursor.fetchall()
            return app.response_class(
                response=json.dumps({'status': 'success', 'results': results}),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            print(f"Erro ao buscar na tabela {table_name}: {e}")
            return app.response_class(
                response=json.dumps({'status': 'error', 'message': str(e)}),
                status=500,
                mimetype='application/json'
            )
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Tabela ou consulta inválida.'}),
            status=400,
            mimetype='application/json'
        )
    

# rota interna para adicionar novas linhas
@app.route('/add_data', methods=['POST'])
@login_required
def add_data():
    table_name = request.form.get('table_name')
    form_data = {key: request.form.get(key) for key in request.form if key != 'table_name'}
    if table_name and form_data:
        try:
            connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor,
                db="defaultdb",
                host="projweb3-projweb3.g.aivencloud.com",
                password="AVNS_J6HaV0sCEBEwuvqBeGP",
                port=19280,
                user="avnadmin",
            )
            with connection.cursor() as cursor:
                columns = ", ".join(form_data.keys())
                values = ", ".join([f"%({key})s" for key in form_data])
                cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})", form_data)
                connection.commit()
            return app.response_class(
                response=json.dumps({'status': 'success'}),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            print(f"Erro ao adicionar registro na tabela {table_name}: {e}")
            return app.response_class(
                response=json.dumps({'status': 'error', 'message': str(e)}),
                status=200,
                mimetype='application/json'
            )
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Dados inválidos.'}),
            status=200,
            mimetype='application/json'
        )
    
# rota interna que possibilita alterar linhas
@app.route('/update_data', methods=['POST'])
@login_required
def update_data():
    try:
        # Obtém os dados JSON da requisição
        data = request.get_json()
        if not data:
            return app.response_class(
                response=json.dumps({'status': 'error', 'message': 'Nenhum dado fornecido.'}),
                status=400,
                mimetype='application/json'
            )

        id = data.get('id')
        table_name = data.get('table_name')
        if not id or not table_name:
            return app.response_class(
                    response=json.dumps({'status': 'error', 'message': 'ID ou nome da tabela não fornecido.'}),
                    status=400,
                    mimetype='application/json'
            )
        
        updated_data = {key: value for key, value in data.items() if key not in ['id', 'table_name']}
        
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",
            host="projweb3-projweb3.g.aivencloud.com",
            password="AVNS_J6HaV0sCEBEwuvqBeGP",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            set_clause = ", ".join([f"{key} = %s" for key in updated_data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            cursor.execute(query, list(updated_data.values()) + [id])
            connection.commit()
        return app.response_class(
            response=json.dumps({'status': 'success'}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Erro ao atualizar dados: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )
    finally:
        if 'connection' in locals():
            connection.close()

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')

        try:
            connection = pymysql.connect(
                charset="utf8mb4",
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor,
                db="logins",
                host="projweb3-projweb3.g.aivencloud.com",
                password="AVNS_J6HaV0sCEBEwuvqBeGP",
                port=19280,
                user="avnadmin",
            )
            with connection.cursor() as cursor:
                # Check if username already exists
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists.', 'error')
                    return render_template('register.html')

                # Create new user
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, password_hash)
                )
                connection.commit()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Error during registration: {e}")
            flash('An error occurred during registration.', 'error')
            return render_template('register.html')
        finally:
            if 'connection' in locals():
                connection.close()

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)