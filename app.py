from flask import Flask, render_template, request, redirect, url_for, flash, json, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = 'institutooceanoazulXunilasalle'

# Initialize Flask-Login
autenticador = LoginManager()
autenticador.init_app(app)
autenticador.login_view = 'login'

# ------------------- L O G I N S -----------------------------------------------
# função para conectar ao banco de dados
def conectar_banco(database_name='defaultdb'):
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
    return connection

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
@autenticador.user_loader
def load_user(user_id):
    print(f"Usuário carregado com ID: {user_id}")
    try:
        connection = conectar_banco()
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
        
        print("Usuário não encontrado!")
        return None
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None

# ROTA PARA PÁGINA INICIAL
@app.route('/')
def index():
    return render_template('index.html')

# LOGIN UNIFICADO
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any existing flashed messages to prevent duplicates
    session.pop('_flashes', None)
    
    # Check if user is already logged in
    if current_user.is_authenticated:
        flash('Você já está logado!', 'info')
        if current_user.get_role() == 'admin':
            return redirect(url_for('tables'))
        else:  # client
            return redirect(url_for('consultas_cliente'))

    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        print(f"Login attempt - Identifier: {identifier}")
        print(f"Password entered: {password}")  # Debug - will show in logs
        
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                # Try to find user by email first, then by username
                print(f"Procurando por usuário... Email: {identifier}")
                cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"Procurando por usuário... Username: {identifier}")
                    cursor.execute("SELECT * FROM users WHERE username = %s", (identifier,))
                    user_data = cursor.fetchone()

            if user_data:
                print(f"Found user: {user_data}")
                if check_password_hash(user_data['password_hash'], password):
                    print("Senha correta!")
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        name=user_data['name'],
                        phone=user_data['phone'],
                        role=user_data['role']
                    )
                    user._authenticated = True
                    login_user(user)
                    print(f"Usuário logado: {user}")
                    
                    # Clear messages before redirect
                    session.pop('_flashes', None)
                    
                    # Show success message
                    flash(f'Bem-vindo, {user.name}!', 'success')
                    
                    # redireciona para páginas de admin e cliente baseado na role
                    if user.role == 'admin':
                        return redirect(url_for('tables'))
                    elif user.role == 'client':
                        print(f"Redirecionando cliente {user.email} para consultas_cliente")
                        return redirect(url_for('consultas_cliente'))
                    else:
                        print(f"Função inválida: {user.role}")
                        flash('Função de usuário inválida', 'error')
                        return redirect(url_for('login'))
                else:
                    print(f"Senha errada para senha: {password}")
                    flash('Senha inválida', 'error')
            else:
                print("Nenhum usuário encontrado.")
                flash('Usuário não encontrado', 'error')
            
            # Clear messages before redirect
            session.pop('_flashes', None)
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during login: {e}")
            flash('Erro durante o login', 'error')
            # Clear messages before redirect
            session.pop('_flashes', None)
            return redirect(url_for('login'))
    return render_template('login.html')

    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        print(f"Login attempt - Identifier: {identifier}")
        print(f"Password entered: {password}")  # Debug - will show in logs
        
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                # Try to find user by email first, then by username
                print(f"Procurando por usuário... Email: {identifier}")
                cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"Procurando por usuário... Username: {identifier}")
                    cursor.execute("SELECT * FROM users WHERE username = %s", (identifier,))
                    user_data = cursor.fetchone()

            if user_data:
                print(f"Found user: {user_data}")
                #debug print(f"Password hash: {user_data['password_hash']}")
                #debug print(f"Password entered: {password}")  
                if check_password_hash(user_data['password_hash'], password):
                    print("Senha correta!")
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        name=user_data['name'],
                        phone=user_data['phone'],
                        role=user_data['role']
                    )
                    user._authenticated = True
                    login_user(user)
                    print(f"Usuário logado: {user}")
                    
                    # redireciona para páginas de admin e cliente baseado na role
                    if user.role == 'admin':
                        return redirect(url_for('tables'))
                    elif user.role == 'client':
                        print(f"Redirecionando cliente {user.email} para consultas_cliente")
                        return redirect(url_for('consultas_cliente'))
                    else:
                        print(f"Função inválida: {user.role}")
                        flash('Função de usuário inválida')
                        return redirect(url_for('login'))
                else:
                    print(f"Senha errada para senha: {password}")
            else:
                print("Nenhum usuário encontrado.")
            
            flash('Identificador ou senha inválidos')
            return redirect(url_for('login'))
        
        except Exception as e:
            print(f"Error during login: {e}")
            flash('Erro durante o login')
            return redirect(url_for('login'))
    return render_template('login.html')

# Registro de usuário - cliente ou admin
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Clear any existing flashed messages
    session.pop('_flashes', None)
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        role = request.form.get('role')
        username = request.form.get('username')  # só para admins!
        
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email já cadastrado.', 'error')
                    return render_template('register.html')
                
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Nome de usuário já cadastrado.', 'error')
                    return render_template('register.html')

                password_hash = generate_password_hash(password)

                if role == 'client':
                    # clientes adicionados automaticamente
                    cursor.execute(
                        "INSERT INTO users (email, username, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                        (email, username, password_hash, name, phone, 'client')
                    )
                    flash('Cliente registrado com sucesso!', 'success')
                    # Clear messages before redirect
                    session.pop('_flashes', None)
                    return redirect(url_for('login'))
                else:  # role == 'admin'
                    # Check if admin request already exists
                    cursor.execute(
                        "SELECT id FROM aprovar_admins WHERE email = %s",
                        (email,)
                    )
                    existing_request = cursor.fetchone()
                    if existing_request:
                        flash('Já existe uma solicitação de admin pendente para este email', 'warning')
                        return redirect(url_for('login'))
                    cursor.execute(
                        "SELECT id FROM users WHERE email = %s AND role = 'admin'",
                        (email,)
                    )
                    existing_admin = cursor.fetchone()
                    if existing_admin:
                        flash('Este usuário já é um administrador.', 'warning')
                        return redirect(url_for('login'))
                    cursor.execute(
                        "INSERT INTO aprovar_admins (email, username, password_hash, name, phone) VALUES (%s, %s, %s, %s, %s)",
                        (email, username, password_hash, name, phone)
                    )
                    flash('Solicitação de admin enviada para aprovação!', 'info')
                    # Clear messages before redirect
                    session.pop('_flashes', None)
                    return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during registration: {e}")
            flash('Erro durante o registro', 'error')
            # Clear messages before redirect
            session.pop('_flashes', None)
            return render_template('register.html')
    try:
        password_hash = generate_password_hash(password)

        if role == 'client':
            # clientes adicionados automaticamente
            cursor.execute(
                "INSERT INTO users (email, username, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (email, username, password_hash, name, phone, 'client')
            )
            flash('Cliente registrado com sucesso!', 'success')
        else:  # role == 'admin'
            # Check if admin request already exists
            cursor.execute(
                "SELECT id FROM aprovar_admins WHERE email = %s",
                (email,)
            )
            existing_request = cursor.fetchone()
            if existing_request:
                flash('Já existe uma solicitação de admin pendente para este email', 'warning')
                session.pop('_flashes', None)
                return redirect(url_for('login'))
            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND role = 'admin'",
                (email,)
            )
            existing_admin = cursor.fetchone()
            if existing_admin:
                flash('Este usuário já é um administrador.', 'warning')
                session.pop('_flashes', None)
                return redirect(url_for('login'))
            
            # admins precisam ser aprovados!!
            cursor.execute(
                "INSERT INTO aprovar_admins (email, username, password_hash, name, phone) VALUES (%s, %s, %s, %s, %s)",
                (email, username, password_hash, name, phone)
            )
            flash('Solicitação de admin enviada para aprovação!', 'info')
            session.pop('_flashes', None)
        
        connection.commit()
        return redirect(url_for('login'))

    except Exception as e:
        print(f"Error during registration: {e}")
        flash('Erro durante o registro', 'error')
        session.pop('_flashes', None)
        return render_template('register.html')


# ------------------- R O T A S &&& P A G I N A S -----------------------------------------------

# Rota para aprovar admins
@app.route('/admin/tables/aprovar_admins', methods=['POST'])
@login_required
def aprovar_admins():
    if current_user.role != 'admin':
        flash('Acesso negado - apenas administradores!', 'error')
        return redirect(url_for('login'))

    try:
        connection = conectar_banco()
        with connection.cursor() as cursor:
            admin_id = request.form.get('admin_id')
            action = request.form.get('action')
            
            if action == 'approve':
                cursor.execute(
                    "SELECT * FROM aprovar_admins WHERE id = %s", (admin_id,)
                )
                admin_request = cursor.fetchone()
                
                if admin_request:
                    cursor.execute(
                        "INSERT INTO users (email, username, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                        (admin_request['email'], admin_request['username'], 
                         admin_request['password_hash'], admin_request['name'],
                         admin_request['phone'], 'admin')
                    )
                    cursor.execute("DELETE FROM aprovar_admins WHERE id = %s", (admin_id,))
                    flash('Admin aprovado com sucesso!', 'success')
                else:
                    flash('Solicitação não encontrada', 'error')
            elif action == 'reject':
                cursor.execute("DELETE FROM aprovar_admins WHERE id = %s", (admin_id,))
                flash('Solicitação rejeitada', 'success')

            connection.commit()
            return redirect(url_for('view_table', table_name='aprovar_admins'))
    except Exception as e:
        print(f"Error during aprovação: {e}")
        flash('Erro durante a operação', 'error')
        return redirect(url_for('view_table', table_name='aprovar_admins'))

@app.route('/logout')
def logout():
    # Clear any existing flashed messages
    session.pop('_flashes', None)
    logout_user()
    flash('Você foi desconectado com sucesso!', 'info')
    return redirect(url_for('index'))

# rota para visualizar tabelas (template sistema)
@app.route('/admin/tables', methods=['GET'])
@login_required
def tables():
    if current_user.role != 'admin':
        flash('Accesso negado.')
        return redirect(url_for('login'))
    
    tables = get_tables('defaultdb')
    return render_template('sistema.html', tables=tables)

# pagina de tabela específica : exibe dados da tabela selecionada
@app.route('/admin/table/<table_name>', methods=['GET'])
@login_required
def view_table(table_name):
    if current_user.role != 'admin':
        flash('Accesso negado.')
        return redirect(url_for('login'))
    
    # para rota "aprovar admins" é necessário alterar a página!
    try:
        if table_name == 'aprovar_admins':
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM aprovar_admins")
                data = cursor.fetchall()
                if not data:
                    data = []  # Return empty list instead of message
                return render_template('aprovar_admins.html', admin_requests=data)
        
        data = get_data('defaultdb', table_name)
        if not data:
            data = [{'message': 'Vazio!'}]
        
        return render_template('view_table.html', table_name=table_name, data=data)
    except Exception as e:
        print(f"Error fetching data from table {table_name}: {e}")
        flash('Erro ao carregar dados da tabela')
        return redirect(url_for('tables'))

# rota interna que possibilita pesquisa de linha na tabela e retorna o resultado
@app.route('/admin/search', methods=['POST'])
@login_required
def search():
    if current_user.role != 'admin':
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Acesso negado'}),
            status=403,
            mimetype='application/json'
        )
    
    # Get parameters from form data
    table_name = request.form.get('table_name')
    search_query = request.form.get('search_query')
    
    # Validate required parameters
    if not table_name or not search_query:
        print(f"Parâmetros inválidos: table_name={table_name}, search_query={search_query}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': 'Tabela ou consulta inválida.'}),
            status=400,
            mimetype='application/json'
        )
    
    try:
        print(f"Busca na tabela {table_name} por query: {search_query}")
        results = search_data(table_name, search_query)
        return results
    except Exception as e:
        print(f"Erro durante busca na tabela {table_name}: {e}")
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
        return json.dumps({'error': 'Accesso negado.'}), 403, {'Content-Type': 'application/json'}
    
    table_name = request.form.get('table_name')
    data = {}
    
    # puxa tudo menos o nome da tabela
    for key in request.form.keys():
        if key != 'table_name':
            data[key] = request.form.get(key)
    
    try:
        result = add_data(table_name, data)
        return result
    except Exception as e:
        print(f"Error ao inserir data: {e}")
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

# rota interna que possibilita alterar linhas
@app.route('/admin/update_data', methods=['POST'])
@login_required
def update_data():
    if current_user.role != 'admin':
        print(f"Accesso negado. - user role: {current_user.role}")
        flash('Acesso negado')
        return redirect(url_for('login'))
    
    try:
        connection = conectar_banco()
        id = request.form.get('id')
        table_name = request.form.get('table_name')
        if not id or not table_name:
            return app.response_class(
                response=json.dumps({'status': 'error', 'message': 'ID ou nome da tabela não fornecido.'}),
                status=400,
                mimetype='application/json'
            )
        
        # puxa tudo menos ID e tabela
        updated_data = {}
        for key in request.form.keys():
            if key not in ['id', 'table_name']:
                updated_data[key] = request.form.get(key)

        conectar_banco()
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
            print(f"Accesso negado. - user role: {user.role}")
            flash('Acesso negado')
            return redirect(url_for('login'))
        connection = conectar_banco()
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
        return json.dumps({'error': 'Accesso negado.'}), 403, {'Content-Type': 'application/json'}
    
    consulta_id = request.form.get('consulta_id')
    data = request.form.get('data')
    hora = request.form.get('hora')
    detalhes = request.form.get('detalhes')
    status = request.form.get('status')

    try:
        connection = conectar_banco()
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
        return json.dumps({'error': 'Accesso negado.'}), 403, {'Content-Type': 'application/json'}
    
    consulta_id = request.form.get('consulta_id')

    try:
        connection = conectar_banco()
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
        connection = conectar_banco()
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
def get_data(table_name):
    try:
        connection = conectar_banco()
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
        connection = conectar_banco()
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
        connection = conectar_banco()
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
        conectar_banco()
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
        conectar_banco()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column['Field'] for column in cursor.fetchall()]
            
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
        conectar_banco()
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