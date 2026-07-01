
"""
SQLAlchemy-based database connector
Supports:
1. INTERNAL APP DB (ORM session)
2. EXTERNAL DB connections (user uploads)
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# ✅ PART 1: INTERNAL DATABASE (ORM SUPPORT)
# ============================================================

_engine = None
SessionLocal = None


def get_engine():
    """Get singleton engine for internal app DB"""
    global _engine

    if _engine is None:
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME"),
        )

        _engine = create_engine(url, echo=False, pool_pre_ping=True)

        print(f"[OK] App DB connected: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")

    return _engine


def get_session():
    """Get ORM session for internal DB"""
    global SessionLocal

    if SessionLocal is None:
        engine = get_engine()
        SessionLocal = sessionmaker(bind=engine)

    return SessionLocal()


# ============================================================
# ✅ PART 2: EXTERNAL DATABASE CONNECTION (EXISTING LOGIC)
# ============================================================

def connect(db_type, host, port, db_name, username, password):
    """Create engine for external DB connections"""
    try:
        db_type = db_type.lower()

        if db_type == 'postgresql':
            url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
        elif db_type == 'mysql':
            url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
        elif db_type == 'mssql':
            url = (
                f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
            )
            
        elif db_type == 'sqlite':
            url = f"sqlite:///{host}"
        elif db_type == 'oracle':
            url = f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{db_name}"
        else:
            print(f"[db_connector] Unsupported db_type: {db_type}")
            return None

        engine = create_engine(url)
        return engine

    except Exception as e:
        print(f"[db_connector] connect() error: {e}")
        return None


def test_connection(engine):
    """Test DB connection"""
    if engine is None:
        return (False, "Engine is None")

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return (True, "Connected")

    except Exception as e:
        return (False, str(e))

def list_schemas(engine, db_type='postgresql'):
    """Fetch available schemas/databases"""

    if engine is None:
        return []

    try:
        with engine.connect() as conn:

            if db_type == "postgresql":
                result = conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata
                """)).fetchall()

                return [row[0] for row in result]

            elif db_type == "mssql":
                result = conn.execute(text("""
                    SELECT name FROM sys.schemas
                """)).fetchall()

                return [row[0] for row in result]

            elif db_type == "oracle":
                result = conn.execute(text("""
                    SELECT username FROM all_users
                """)).fetchall()

                return [row[0] for row in result]

            elif db_type == "mysql":
                result = conn.execute(text("SHOW DATABASES")).fetchall()
                return [row[0] for row in result]

            else:
                return []

    except Exception as e:
        print(f"[db_connector] list_schemas error: {e}")
        return []

def list_tables(engine, schema=None):
    """List tables from selected schema (dynamic)"""

    if engine is None or not schema:
        return []

    try:
        inspector = inspect(engine)

        tables = inspector.get_table_names(schema=schema)
        views = inspector.get_view_names(schema=schema)

        return tables + views

    except Exception as e:
        print(f"[db_connector] list_tables error: {e}")
        return []


def fetch(engine, table, where_str='', params=None, limit=100_000, db_type='postgresql'):
    """Fetch data from external DB with dynamic schema support"""

    if engine is None:
        return pd.DataFrame()

    try:
        n = int(limit)
        db = (db_type or 'postgresql').lower()
        where_clause = f" WHERE {where_str}" if where_str else ""

        #  extract schema from params
        schema = None
        if params and isinstance(params, dict):
            schema = params.get("schema")

        #  build full table name safely
        if schema:
            if db in ['postgresql', 'oracle']:
                full_table = f'"{schema}"."{table}"'
            else:
                full_table = f"{schema}.{table}"
        else:
            full_table = table

        #  build query based on DB type
        if db == 'mssql':
            query = f"SELECT TOP {n} * FROM {full_table}{where_clause}"

        elif db == 'oracle':
            query = f"SELECT * FROM {full_table}{where_clause} FETCH FIRST {n} ROWS ONLY"

        else:  # postgresql, mysql, sqlite
            query = f"SELECT * FROM {full_table}{where_clause} LIMIT {n}"

        #  execute query
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))

        return df

    except Exception as e:
        print(f"[db_connector] fetch() error: {e}")
        return pd.DataFrame()


# def fetch(engine, table, where_str='', params=None, limit=100_000, db_type='postgresql'):
#     """Fetch data from external DB"""
#     if engine is None:
#         return pd.DataFrame()

#     try:
#         n = int(limit)
#         db = (db_type or 'postgresql').lower()
#         where_clause = f" WHERE {where_str}" if where_str else ""

#         if db == 'mssql':
#             query = f"SELECT TOP {n} * FROM {table}{where_clause}"
#         elif db == 'oracle':
#             query = f"SELECT * FROM {table}{where_clause} FETCH FIRST {n} ROWS ONLY"
#         else:
#             query = f"SELECT * FROM {table}{where_clause} LIMIT {n}"

#         with engine.connect() as conn:
#             result = conn.execute(text(query), params or {})
#             df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))

#         return df

#     except Exception as e:
#         print(f"[db_connector] fetch() error: {e}")
#         return pd.DataFrame()











# """SQLAlchemy-based database connector for the dashboard."""

# import pandas as pd
# from sqlalchemy import create_engine, text, inspect


# def connect(db_type, host, port, db_name, username, password):
#     """Build SQLAlchemy URL and create engine. Returns engine or None on failure."""
#     try:
#         db_type = db_type.lower()
#         if db_type == 'postgresql':
#             url = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
#         elif db_type == 'mysql':
#             url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
#         elif db_type == 'mssql':
#             url = (
#                 f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}"
#                 f"?driver=ODBC+Driver+17+for+SQL+Server"
#             )
#         elif db_type == 'sqlite':
#             # host is used as the file path for sqlite
#             url = f"sqlite:///{host}"
#         elif db_type == 'oracle':
#             url = f"oracle+cx_oracle://{username}:{password}@{host}:{port}/{db_name}"
#         else:
#             print(f"[db_connector] Unsupported db_type: {db_type}")
#             return None

#         engine = create_engine(url)
#         return engine
#     except Exception as e:
#         print(f"[db_connector] connect() error: {e}")
#         return None


# def test_connection(engine):
#     """Execute SELECT 1. Returns (True, 'Connected') or (False, error_message)."""
#     if engine is None:
#         return (False, "Engine is None")
#     try:
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))
#         return (True, "Connected")
#     except Exception as e:
#         return (False, str(e))


# def list_tables(engine):
#     """Return list of table and view names using sqlalchemy inspect. Returns [] on error."""
#     if engine is None:
#         return []
#     try:
#         inspector = inspect(engine)
#         tables = inspector.get_table_names()
#         views = inspector.get_view_names()
#         return tables + views
#     except Exception as e:
#         print(f"[db_connector] list_tables() error: {e}")
#         return []


# def fetch(engine, table, where_str='', params=None, limit=100_000, db_type='postgresql'):
#     """SELECT * FROM table with optional WHERE conditions and row limit.

#     `where_str` should be bare conditions (no WHERE keyword) — produced by
#     query_builder.build(). `db_type` controls LIMIT syntax: MSSQL uses TOP,
#     Oracle uses FETCH FIRST, all others use LIMIT.
#     Table name comes from list_tables() output (trusted).
#     Returns empty DataFrame on error.
#     """
#     if engine is None:
#         return pd.DataFrame()
#     try:
#         n = int(limit)
#         db = (db_type or 'postgresql').lower()
#         where_clause = f" WHERE {where_str}" if where_str else ""
#         if db == 'mssql':
#             query = f"SELECT TOP {n} * FROM {table}{where_clause}"
#         elif db == 'oracle':
#             query = f"SELECT * FROM {table}{where_clause} FETCH FIRST {n} ROWS ONLY"
#         else:
#             query = f"SELECT * FROM {table}{where_clause} LIMIT {n}"

#         with engine.connect() as conn:
#             result = conn.execute(text(query), params or {})
#             df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
#         return df
#     except Exception as e:
#         print(f"[db_connector] fetch() error: {e}")
#         return pd.DataFrame()
