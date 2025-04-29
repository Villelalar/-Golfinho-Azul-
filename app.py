from flask import Flask, render_template, request, redirect, url_for, flash, json 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = 'institutooceanoazulXunilasalle'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------- L O G I N S -----------------------------------------------
# modelo de usuário
class User(UserMixin):
    def __init__(self, id, email, name, phone, role):
        self.id = id
        self.email = email
        self.name = name
        self.phone = phone
        self.role = role
        self._authenticated = False

    def is_authenticated(self):
        return self._authenticated

    def get_id(self):
        return str(self.id)

    def get_role(self):
        return self.role

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, role={self.role}, authenticated={self._authenticated})"

# loader para usuários
@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")
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
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                user = User(
                    id=user_data['id'],
                    email=user_data['email'],
                    name=user_data['name'],
                    phone=user_data['phone'],
                    role=user_data['role']
                )
                user._authenticated = True
                print(f"Loaded user: {user}")
                return user
        
        print("User not found")
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# ROTA PARA PÁGINA INICIAL
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginadmin', methods=['GET', 'POST'])
def loginadmin():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM admins WHERE email = %s', (identifier,))
            user = cursor.fetchone()
            
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['email'], user['name'], user['phone'], 'admin')
            login_user(user_obj)
            return redirect(url_for('tables'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('login.html')

@app.route('/logincliente', methods=['GET', 'POST'])
def logincliente():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM clients WHERE email = %s', (identifier,))
            user = cursor.fetchone()
            
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['email'], user['name'], user['phone'], 'client')
            login_user(user_obj)
            return redirect(url_for('consultas_cliente'))
        else:
            flash('Credenciais inválidas!', 'error')
    
    return render_template('login.html')

# Unified login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        print(f"Login attempt - Identifier: {identifier}")
        print(f"Password entered: {password}")  # Debug - will show in logs
        
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
                # Try to find user by email first, then by username
                print(f"Searching for user with email: {identifier}")
                cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"No user found with email, searching for username: {identifier}")
                    cursor.execute("SELECT * FROM users WHERE username = %s", (identifier,))
                    user_data = cursor.fetchone()

            if user_data:
                print(f"Found user: {user_data}")
                print(f"Password hash: {user_data['password_hash']}")
                print(f"Password entered: {password}")  # Debug - will show in logs
                if check_password_hash(user_data['password_hash'], password):
                    print("Password check succeeded")
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        name=user_data['name'],
                        phone=user_data['phone'],
                        role=user_data['role']
                    )
                    user._authenticated = True
                    login_user(user)
                    print(f"User logged in: {user}")
                    
                    # Redirect based on user role
                    if user.role == 'admin':
                        return redirect(url_for('tables'))
                    elif user.role == 'client':
                        print(f"Redirecting client {user.email} to consultas_cliente")
                        return redirect(url_for('consultas_cliente'))
                    else:
                        print(f"Invalid role: {user.role}")
                        flash('Invalid user role')
                        return redirect(url_for('login'))
                else:
                    print(f"Password check failed for password: {password}")
            else:
                print("No user found in database")
            
            flash('Invalid identifier or password')
            return redirect(url_for('login'))
        
        except Exception as e:
            print(f"Error during login: {e}")
            flash('Error during login')
            return redirect(url_for('login'))
    return render_template('login.html')

# Client registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
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
                # Check if email already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email já cadastrado.', 'error')
                    return render_template('register.html')
                
                # Create new client
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s)",
                    (email, password_hash, name, phone, 'client')
                )
                connection.commit()
                
                flash('Cliente registrado com sucesso!')
                return redirect(url_for('login'))
        
        except Exception as e:
            print(f"Error during client registration: {e}")
            flash('Error during registration')
            return redirect(url_for('register'))
    return render_template('register.html')

# Admin registration route (sends to aprovar_admins table)
@app.route('/admin/register', methods=['GET', 'POST'])
def registeradmin():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
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
                # Check if email or username already exists
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email já cadastrado.', 'error')
                    return render_template('registeradmin.html')
                
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username já cadastrado.', 'error')
                    return render_template('registeradmin.html')
                
                # Create new admin in aprovar_admins table
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO aprovar_admins (email, username, password_hash, name, phone) VALUES (%s, %s, %s, %s, %s)",
                    (email, username, password_hash, name, phone)
                )
                connection.commit()
                
                flash('Solicitação de admin enviada para aprovação!')
                return redirect(url_for('login'))
        
        except Exception as e:
            print(f"Error during admin registration: {e}")
            flash('Error during registration')
            return redirect(url_for('registeradmin'))
    return render_template('registeradmin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ------------------- R O T A S &&& P A G I N A S -----------------------------------------------
# sistema route
@app.route('/admin/tables', methods=['GET'])
@login_required
def tables():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('loginadmin'))
    
    # Get tables from the defaultdb database
    tables = get_tables('defaultdb')
    return render_template('sistema.html', tables=tables)

# pagina de tabela específica : exibe dados da tabela
@app.route('/admin/table/<table_name>', methods=['GET'])
@login_required
def view_table(table_name):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('loginadmin'))
    
    data = get_data('defaultdb', table_name)
    return render_template('view_table.html', table_name=table_name, data=data)

# rota interna que possibilita pesquisa de linha na tabela e retorna o resultado
@app.route('/admin/search', methods=['POST'])
@login_required
def search():
    if current_user.role != 'admin':
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Access denied'}),
            status=403,
            mimetype='application/json'
        )
    
    # Get parameters from form data
    table_name = request.form.get('table_name')
    search_query = request.form.get('search_query')
    
    # Validate required parameters
    if not table_name or not search_query:
        print(f"Invalid search parameters: table_name={table_name}, search_query={search_query}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Tabela ou consulta inválida.'}),
            status=400,
            mimetype='application/json'
        )
    
    try:
        print(f"Searching in table {table_name} for query: {search_query}")
        results = search_data(table_name, search_query)
        return results
    except Exception as e:
        print(f"Error during search in table {table_name}: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )

# rota interna para adicionar novas linhas
@app.route('/admin/add_data', methods=['POST'])
@login_required
def add_data():
    if current_user.role != 'admin':
        return json.dumps({'error': 'Access denied'}), 403, {'Content-Type': 'application/json'}
    
    table_name = request.form.get('table')
    data = request.form.get('data')
    
    try:
        # Parse data
        data_dict = json.loads(data)
        
        result = add_data(table_name, data_dict)
        return result
    except Exception as e:
        print(f"Error adding data: {e}")
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

# conecta ao banco de dados, usado para alterar dados in-line
def get_db_connection():
    return pymysql.connect(
        charset="utf8mb4",
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
        db="defaultdb",
        host="projweb3-projweb3.g.aivencloud.com",
        password="AVNS_J6HaV0sCEBEwuvqBeGP",
        port=19280,
        user="avnadmin",
    )

# rota interna que possibilita alterar linhas
# rota interna que possibilita alterar linhas
@app.route('/admin/update_data', methods=['POST'])
@login_required
def update_data():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('login'))
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

# Client consultation page
@app.route('/client/consultas')
@login_required
def consultas_cliente():
    try:
        # Get the user object from the session
        user = current_user
        print(f"User in consultation page: {user}")
        
        if user.role != 'client':
            print(f"Access denied - user role: {user.role}")
            flash('Access denied')
            return redirect(url_for('logincliente'))
        
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
            cursor.execute("SELECT * FROM consultas WHERE user_id = %s", (user.id,))
            consultas = cursor.fetchall()
            
            return render_template('consultascliente.html', consultas=consultas)
    except Exception as e:
        print(f"Error getting consultas: {e}")
        flash('Erro ao carregar consultas.')
        return redirect(url_for('logincliente'))
    finally:
        if 'connection' in locals():
            connection.close()

# Client update consultation
@app.route('/client/consultas/atualizarconsulta', methods=['POST'])
@login_required
def atualizar_consulta():
    if current_user.role != 'client':
        return json.dumps({'error': 'Access denied'}), 403, {'Content-Type': 'application/json'}
    
    consulta_id = request.form.get('consulta_id')
    data = request.form.get('data')
    hora = request.form.get('hora')
    detalhes = request.form.get('detalhes')
    status = request.form.get('status')

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
            cursor.execute("""
                UPDATE consultas 
                SET data = %s, hora = %s, detalhes = %s, status = %s
                WHERE id = %s AND user_id = %s
            """, (data, hora, detalhes, status, consulta_id, current_user.id))
            connection.commit()
            
            return json.dumps({'status': 'success'}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"Error updating consultation: {e}")
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}
    finally:
        if 'connection' in locals():
            connection.close()

# Client delete consultation
@app.route('/client/consultas/deletarconsulta', methods=['POST'])
@login_required
def deletar_consulta():
    if current_user.role != 'client':
        return json.dumps({'error': 'Access denied'}), 403, {'Content-Type': 'application/json'}
    
    consulta_id = request.form.get('consulta_id')

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
            cursor.execute("""
                DELETE FROM consultas 
                WHERE id = %s AND user_id = %s
            """, (consulta_id, current_user.id))
            connection.commit()
            
            return json.dumps({'status': 'success'}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"Error deleting consultation: {e}")
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}
    finally:
        if 'connection' in locals():
            connection.close()

# Função para listar as tabelas do banco de dados
def get_tables(database_name):
    try:
        print(f"Attempting to connect to database: {database_name}")
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
            print(f"Found {len(table_names)} tables")
            return table_names
    except Exception as e:
        print(f"Error getting tables: {e}")
        return []
    finally:
        if 'connection' in locals():
            print("Closing connection")
            connection.close()

# Função para obter dados de uma tabela
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
        print(f"Error getting data: {e}")
        return []
    finally:
        if 'connection' in locals():
            connection.close()

# Função para adicionar dados a uma tabela
def add_data(table_name, data):
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
            # Get column names and values
            columns = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            
            # Build and execute query
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            cursor.execute(query, tuple(data.values()))
            connection.commit()
            
            return app.response_class(
                response=json.dumps({'status': 'success'}),
                status=200,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error adding data: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )
    finally:
        if 'connection' in locals():
            connection.close()

# Função para atualizar dados em uma tabela
def update_data(table_name, data, id):
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
            # Build update query
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            
            # Execute query
            cursor.execute(query, (*data.values(), id))
            connection.commit()
            
            return app.response_class(
                response=json.dumps({'status': 'success'}),
                status=200,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error updating data: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500, {'Content-Type': 'application/json'}
    finally:
        if 'connection' in locals():
            connection.close()

# Função para deletar dados de uma tabela
def delete_data(table_name, id):
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
            cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (id,))
            connection.commit()
            
            return app.response_class(
                response=json.dumps({'status': 'success'}),
                status=200,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error deleting data: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )
    finally:
        if 'connection' in locals():
            connection.close()

# Função para pesquisar dados em uma tabela
def search_data(table_name, search_query):
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
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get all columns
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column['Field'] for column in cursor.fetchall()]
            
            # Build search query
            search_term = f"%{search_query}%"
            query = " OR ".join([f"{column} LIKE %s" for column in columns])
            
            cursor.execute(f"SELECT * FROM {table_name} WHERE {query}", (search_term,) * len(columns))
            results = cursor.fetchall()
            print(results)
            
            return app.response_class(
                response=json.dumps({'status': 'success', 'results': results}),
                status=200,
                mimetype='application/json'
            )
    except Exception as e:
        print(f"Error searching data: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )
    finally:
        if 'connection' in locals():
            connection.close()

# Test route to verify database connection
@app.route('/test_db')
def test_db():
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
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            if tables:
                return f"Database connection successful! Found tables: {', '.join([t[0] for t in tables])}"
            else:
                return "Database connection successful but no tables found."
    except Exception as e:
        return f"Error connecting to database: {str(e)}"
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)