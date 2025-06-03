import pymysql
from pathlib import Path

# Configurações (substitua pelas suas credenciais reais)
CONFIG = {
    "host": "projweb3-projweb3.g.aivencloud.com",
    "port": 19280,
    "user": "avnadmin",
    "password": "AVNS_J6HaV0sCEBEwuvqBeGP",
    "db": "defaultdb",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 10,
    "read_timeout": 10,
    "write_timeout": 10
}

def executar_arquivo_sql(arquivo_sql):
    """Executa todos os comandos de um arquivo SQL"""
    try:
        # Conexão com o Aiven (mantendo sua configuração original)
        connection = pymysql.connect(**CONFIG)
        
        with connection.cursor() as cursor:
            # Lê o arquivo SQL completo
            sql_script = Path(arquivo_sql).read_text(encoding='utf-8')
            
            # Divide em comandos individuais (separados por ';')
            comandos = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
            
            # Executa cada comando
            for comando in comandos:
                try:
                    cursor.execute(comando)
                    print(f"✅ Comando executado: {comando[:50]}...")  # Log resumido
                except pymysql.Error as e:
                    print(f"⚠️ Erro no comando: {comando[:50]}...\n   → {e}")
            
            
            connection.commit()
            print("🎉 Script SQL executado com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro na conexão/execução: {e}")
        if 'connection' in locals() and connection:
            connection.rollback()
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    # Substitua 'script.sql' pelo seu arquivo
    executar_arquivo_sql("metodo.sql")