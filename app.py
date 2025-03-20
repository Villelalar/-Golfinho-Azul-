from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__)

# Função para listar as tabelas do banco de dados
def get_tables(database_name):
    try:
        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db=database_name,
            host="projweb3-projweb3.g.aivencloud.com",
            password="senha",
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
            password="senha",
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

# pagina inicial : lista tabelas
@app.route('/')
def index():
    tables = get_tables("defaultdb")  # Listar tabelas do banco defaultdb
    return render_template('index.html', tables=tables)

# pagina de tabela específica : exibe dados da tabela
@app.route('/view_table/<table_name>')
def view_table(table_name):
    data = get_data("defaultdb", table_name)  # Obter dados da tabela selecionada
    return render_template('view_table.html', table_name=table_name, data=data)

# rota interna que possibilita pesquisa de linha na tabela e retorna o resultado
@app.route('/search', methods=['POST'])
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
                password="senha",
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
            return jsonify({'status': 'success', 'results': results})
        except Exception as e:
            print(f"Erro ao buscar na tabela {table_name}: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        return jsonify({'status': 'error', 'message': 'Tabela ou consulta inválida.'})

# rota interna para adicionar novas linhas
@app.route('/add_data', methods=['POST'])
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
                password="senha",
                port=19280,
                user="avnadmin",
            )
            with connection.cursor() as cursor:
                columns = ", ".join(form_data.keys())
                values = ", ".join([f"%({key})s" for key in form_data])
                cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})", form_data)
                connection.commit()
            return jsonify({'status': 'success'})
        except Exception as e:
            print(f"Erro ao adicionar registro na tabela {table_name}: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
        finally:
            if 'connection' in locals():
                connection.close()
    else:
        return jsonify({'status': 'error', 'message': 'Dados inválidos.'})

# rota interna que possibilita alterar linhas
@app.route('/update_data', methods=['POST'])
def update_data():
    try:
        # Obtém os dados JSON da requisição
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'Nenhum dado fornecido.'}), 400

        id = data.get('id')
        table_name = data.get('table_name')
        if not id or not table_name:
            return jsonify({'status': 'error', 'message': 'ID ou nome da tabela não fornecido.'}), 400

        updated_data = {key: value for key, value in data.items() if key not in ['id', 'table_name']}

        connection = pymysql.connect(
            charset="utf8mb4",
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            db="defaultdb",
            host="projweb3-projweb3.g.aivencloud.com",
            password="senha",
            port=19280,
            user="avnadmin",
        )
        with connection.cursor() as cursor:
            set_clause = ", ".join([f"{key} = %s" for key in updated_data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
            cursor.execute(query, list(updated_data.values()) + [id])
            connection.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Erro ao atualizar dados: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)