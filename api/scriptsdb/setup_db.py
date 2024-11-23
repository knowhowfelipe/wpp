import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

### CONECTA-SE AO BANCO POSTGRES PARA CRIAR O BANCO USUARIOS_DB, CASO NAO EXISTA
def create_database(db_name):
    # Conecta ao banco padrão (postgres) para criar o banco desejado
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='admin',
        host='localhost'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(f'CREATE DATABASE {db_name};')
        print(f"função 'create_database': Banco de dados '{db_name}' criado com sucesso.")
    else:
        print(f"função 'create_database': Banco de dados '{db_name}' já existe.")
    
    cursor.close()
    conn.close()
    
if __name__ == '__main__':
    create_database('wpp_db')
    