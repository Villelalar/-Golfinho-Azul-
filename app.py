import os 
from flask import Flask, render_template, request, redirect, url_for, flash, json, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql
import time
from datetime import datetime

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
    def __init__(self, id, email, name, phone, role, profile_color='#008bb4'):
        self.cpf = id
        self.email = email
        self.name = name
        self.phone = phone
        self.role = role
        self.profile_color = profile_color
        self._authenticated = False

    def is_authenticated(self):
        return self._authenticated

    def get_id(self):
        return str(self.cpf)

    def get_role(self):
        return self.role

    def __repr__(self):
        return f"User(CPF={self.cpf}, email={self.email}, role={self.role}, profile_color={self.profile_color}, authenticated={self._authenticated})"

# loader para usuários
@autenticador.user_loader
def load_user(user_id):
    print(f"Usuário carregado com CPF: {user_id}")
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
                    role=user_data['role'],
                    profile_color=user_data['profile_color']
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
    if current_user.is_authenticated:
        if 'from_acesso_negado' in request.args:
            logout_user()
            session.clear()
            flash('Acesso negado. Por favor, faça login novamente.', 'error')
        else:
            flash('Você já está logado!', 'info')
            if current_user.get_role() == 'admin':
                return redirect(url_for('tables'))
            else:  # client
                return redirect(url_for('historico'))


    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        print(f"Tentando login - Identifier: {identifier}")
        print(f"Senha inserida: {password}")
        
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                # email, depois CPF
                print(f"Procurando por usuário... Email: {identifier}")
                cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
                user_data = cursor.fetchone()
                if not user_data:
                    print(f"Procurando por CPF... CPF: {identifier}")
                    cursor.execute("SELECT * FROM users WHERE id = %s", (identifier,))
                    user_data = cursor.fetchone()

            if user_data:
                print(f"Usuario encontrado: {user_data}")
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
                    
                    # Show success message
                    flash(f'Bem-vindo, {user.name}!', 'success')
                    
                    # redireciona para páginas de admin e cliente baseado na role
                    if user.role == 'admin':
                        return redirect(url_for('tables'))
                    elif user.role == 'client':
                        print(f"Redirecionando cliente {user.email} para historico")
                        return redirect(url_for('historico'))
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
            
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during login: {e}")
            flash('Erro durante o login', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Registro de usuário - cliente ou admin
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        id = request.form.get('id')
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')
        role = request.form.get('role')
        
        print(f"Registrando usuário - ID: {id}, Email: {email}, Role: {role}")
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email já cadastrado.', 'error')
                    return render_template('register.html')
                
                cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
                if cursor.fetchone():
                    flash('CPF já cadastrado.', 'error')
                    return render_template('register.html')

                password_hash = generate_password_hash(password)

                if role == 'client':
                    # clientes adicionados automaticamente
                    cursor.execute(
                        "INSERT INTO users (id, email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                        (id, email, password_hash, name, phone, 'client')
                    )
                    flash('Cliente registrado com sucesso!', 'success')
                    cursor.execute("SELECT id FROM users WHERE id = %s", (id,))
                    user = cursor.fetchone()
                    print(f"Usuário registrado: {user}")
                    connection.commit()
                    return redirect(url_for('login'))
                else:  # role == 'admin'
                    cursor.execute(
                        "SELECT id FROM aprovar_admins WHERE id = %s",
                        (id,)
                    )
                    existing_request = cursor.fetchone()
                    if existing_request:
                        flash('Já existe uma solicitação de admin pendente para este CPF.', 'warning')
                        return redirect(url_for('login'))
                    cursor.execute(
                        "SELECT id FROM users WHERE id = %s AND role = 'admin'",
                        (id,)
                    )
                    existing_admin = cursor.fetchone()
                    if existing_admin:
                        flash('Este usuário já é um administrador.', 'warning')
                        return redirect(url_for('login'))
                    cursor.execute(
                        "INSERT INTO aprovar_admins (id, email, password_hash, name, phone) VALUES (%s, %s, %s, %s, %s)",
                        (id, email, password_hash, name, phone)
                    )
                    flash('Solicitação de admin enviada para aprovação!', 'info')
                connection.commit()
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Error during registration: {e}")
            flash('Erro durante o registro', 'error')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/alterar_dados', methods=['GET', 'POST'])
@login_required
def alterar_dados():
    if request.method == 'GET':
        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (current_user.cpf,))
                user_data = cursor.fetchone()
                if user_data:
                    return render_template('alterar_dados.html', user=user_data)
                else:
                    flash('Usuário não encontrado.', 'error')
                    return redirect(url_for('index'))
        except Exception as e:
            print(f"Error fetching user data: {e}")
            flash('Erro ao carregar dados do usuário.', 'error')
            return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        profile_color = request.form.get('profile_color')

        try:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET name = %s, email = %s, phone = %s, profile_color = %s WHERE id = %s",
                    (name, email, phone, profile_color, current_user.cpf)
                )
                connection.commit()
                flash('Dados atualizados com sucesso!', 'success')
                return redirect(request.url)
                
        except pymysql.Error as e:
            connection.rollback()
            flash(f'Erro ao atualizar dados: {str(e)}', 'error')
            
        finally:
            if connection:
                connection.close()

# ------------------- R O T A S &&& P A G I N A S -----------------------------------------------

# Rota para acesso negado
@app.route('/acesso_negado')
def acesso_negado():
    return render_template('acesso_negado.html')

# Rota para aprovar admins
# Rota para aprovar admins
@app.route('/admin/tables/aprovar_admins', methods=['POST'])
@login_required
def aprovar_admins():
    if current_user.role != 'admin':
        flash('Acesso negado - apenas administradores!', 'error')
        time.sleep(2)
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
                        "INSERT INTO users (id, email, password_hash, name, phone, role) VALUES (%s, %s, %s, %s, %s, %s)",
                        (admin_request['id'], admin_request['email'], 
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
        print(f"Accesso negado. - user role: {current_user.role}")
        flash('Acesso negado')
        return redirect(url_for('login')) 
    tables = get_tables('defaultdb')
    return render_template('sistema.html', tables=tables)

# pagina de tabela específica : exibe dados da tabela selecionada
@app.route('/admin/table/<table_name>', methods=['GET'])
@login_required
def view_table(table_name):
    if current_user.role != 'admin':
        print(f"Accesso negado. - user role: {current_user.role}")
        flash('Acesso negado')
        return redirect(url_for('login')) 
    
    # para rota "aprovar admins" é necessário alterar a página!
    try:
        if table_name == 'aprovar_admins':
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM aprovar_admins")
                data = cursor.fetchall()
                if not data:
                    data = []  
                return render_template('aprovar_admins.html', admin_requests=data)
        
        data = get_data(table_name)
        if not data:
            connection = conectar_banco()
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = cursor.fetchall()  # Aqui pegamos as colunas da tabela
                # Criar um dicionário falso com valores vazios (ou algum valor fictício)
                fake = {column['Field']: '--' for column in columns} 
                data = [fake]
        return render_template('view_table.html', table_name=table_name, data=data)
    except Exception as e:
        print(f"Error fetching data from table {table_name}: {e}")
        flash('Erro ao carregar dados da tabela.')
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
        return app.response_class(
            response=json.dumps({'status': 'success'}),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print(f"Error ao inserir data: {e}")
        return app.response_class(
            response=json.dumps({'status': 'error', 'message': str(e)}),
            status=500,
            mimetype='application/json'
        )

@app.route('/add_doacao/<valor>', methods=['POST'])
@login_required
def add_doacao(valor):
    try:
        metodo = request.form.get('metodo')  # Get the payment method from the form
        if not metodo:
            return json.dumps({'error': 'Método de pagamento não fornecido'}), 400, {'Content-Type': 'application/json'}
            
        connection = conectar_banco()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO doacoes (user_id, valor, metodo, status, created_at) VALUES (%s, %s, %s, %s, %s)",
                           (current_user.cpf, valor, metodo, 'pendente', datetime.now()))
            connection.commit()
        return json.dumps({'status': 'success', 'message': 'Doação registrada com sucesso!'}), 200, {'Content-Type': 'application/json'}
    except pymysql.IntegrityError as e:
        print(f"Integrity error: {e}")
        return json.dumps({'error': 'Doação já registrada para este usuário.'}), 400, {'Content-Type': 'application/json'}
    except Exception as e:
        print(f"Error ao inserir data: {e}")
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'GET':
        return render_template('alterar_senha.html')
    
    connection = None
    try:
        # Get form data
        cpf = request.form.get('cpf')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # If user is logged in, use their info
        if current_user.is_authenticated:
            cpf = current_user.cpf
            email = current_user.email
        
        # Validate required fields
        if not all([cpf, email, new_password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return redirect(url_for('alterar_senha'))
            
        if new_password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('alterar_senha'))
            
        connection = conectar_banco()
        with connection.cursor() as cursor:
            # Check if user exists and get current password hash
            cursor.execute("SELECT password_hash FROM users WHERE id = %s AND email = %s", (cpf, email))
            user = cursor.fetchone()
            
            if not user:
                flash('CPF e/ou e-mail incorretos. Por favor, verifique os dados informados.', 'error')
                return redirect(url_for('alterar_senha'))
                
            # Check if new password is different from current
            if check_password_hash(user['password_hash'], new_password):
                flash('Por favor, use uma senha diferente da anterior.', 'error')
                return redirect(url_for('alterar_senha'))
                
            # Update password
            hash_nova = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hash_nova, cpf))
            connection.commit()
            
            if current_user.is_authenticated:
                flash('Senha alterada com sucesso!', 'success')
                return redirect(url_for('alterar_dados'))
            else:
                flash('Senha alterada com sucesso! Faça login com a nova senha.', 'success')
                return redirect(url_for('login'))
    
    except Exception as e:
        print(f"Erro ao alterar senha: {e}")
        flash(f'Ocorreu um erro ao processar sua solicitação: {str(e)}', 'error')
        return redirect(url_for('alterar_senha'))
    finally:
        if connection:
            connection.close()

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
                # ... depois salve normalmente no banco

        connection = conectar_banco()
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
@app.route('/client/historico')
@login_required
def historico():
    try:
        user = current_user
        print(f"Página de Histórico: {user}")
        
        if user.role != 'client':
            print(f"Accesso negado. - user role: {user.role}")
            flash('Acesso negado')
            return redirect(url_for('login'))
        connection = conectar_banco()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM doacoes WHERE user_id = %s", (user.cpf,))
            historico = cursor.fetchall()
            return render_template('historico.html', historico=historico)
    except Exception as e:
        print(f"Error getting doacoes: {e}")
        flash('Erro ao carregar doacoes.')
        return redirect(url_for('login'))
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
def get_data(table_name, database_name='defaultdb'):
    try:
        connection = conectar_banco(database_name)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
        return data
    except Exception as e:
        print(f"Error getting data from {database_name}.{table_name}: {e}")
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
        connection = conectar_banco()
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
        connection = conectar_banco()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column['Field'] for column in cursor.fetchall()]
            
            search_term = f"%{search_query}%"
            query = " OR ".join([f"{column} LIKE %s" for column in columns])
            
            cursor.execute(f"SELECT * FROM {table_name} WHERE {query}", (search_term,) * len(columns))
            results = cursor.fetchall()

            # Formatar campos de data/hora para o padrão SQL
            for row in results:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.strftime('%Y-%m-%d %H:%M:%S')

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

# Route to delete data from a table
@app.route('/admin/delete_data', methods=['POST'])
@login_required
def route_delete_data():
    if current_user.role != 'admin':
        return json.dumps({'status': 'error', 'message': 'Acesso negado'}), 403, {'Content-Type': 'application/json'}
    
    try:
        table_name = request.form.get('table_name')
        row_id = request.form.get('id')
        
        if not table_name or not row_id:
            return json.dumps({'status': 'error', 'message': 'Nome da tabela ou ID não fornecidos'}), 400
            
        # Call the delete_data helper function
        result = delete_data(table_name, row_id)
        return json.dumps({'status': 'success'}), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        print(f"Error deleting data: {e}")
        return json.dumps({'status': 'error', 'message': str(e)}), 500, {'Content-Type': 'application/json'}

# Test route to verify database connection
@app.route('/test_db')
def test_db():
    try:
        connection = conectar_banco()
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
