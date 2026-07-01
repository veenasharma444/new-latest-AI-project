"""
Intelligent Data Dashboard - Multi-Page Architecture with PostgreSQL Authentication
====================================================================================
Phases:
1. Authentication - PostgreSQL user database with secure session management
2. Code Refactoring - Modular architecture
3. Intelligence Layer - Auto-analysis & recommendations
4. LLM Integration - LMStudio + Claude fallback
5. User Interaction - Multi-page flow with user customization

Usage:
    python dashboard.py
    Open http://0.0.0.0:8050
"""

import os
import json
import pickle
import warnings
import pandas as pd
import numpy as np
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, callback, ALL
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import secrets
# from sqlalchemy import create_engine, text
# from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv

load_dotenv()

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
# POSTGRESQL AUTHENTICATION MODULE
# ═══════════════════════════════════════════════════════════════


# class PostgreSQLAuthenticator:

#     def __init__(self):
#         self.host = os.getenv("DB_HOST")
#         self.port = int(os.getenv("DB_PORT", 5432))
#         self.database = os.getenv("DB_NAME")
#         self.username = os.getenv("DB_USER")
#         self.password = os.getenv("DB_PASSWORD")
#         self.engine = None
#         self._connect()

#     def _connect(self):
#         try:
#             url = URL.create(
#                 drivername="postgresql+psycopg2",
#                 username=self.username,
#                 password=self.password,
#                 host=self.host,
#                 port=self.port,
#                 database=self.database,
#             )

#             self.engine = create_engine(url, echo=False, pool_pre_ping=True)

#             with self.engine.connect() as conn:
#                 conn.execute(text("SELECT 1"))

#             print(f"[OK] PostgreSQL connected: {self.host}:{self.port}/{self.database}")

#         except Exception as e:
#             print(f"[ERROR] PostgreSQL connection failed: {e}")
#             raise

#     def _init_schema(self):
#         """Initialize database schema if not exists"""
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 # Create users table
#                 conn.execute(text("""
#                     CREATE TABLE IF NOT EXISTS users (
#                         id SERIAL PRIMARY KEY,
#                         username VARCHAR(255) UNIQUE NOT NULL,
#                         email VARCHAR(255) UNIQUE NOT NULL,
#                         name VARCHAR(255),
#                         password_hash VARCHAR(512) NOT NULL,
#                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         last_login TIMESTAMP,
#                         is_active BOOLEAN DEFAULT TRUE,
#                         login_attempts INTEGER DEFAULT 0,
#                         locked_until TIMESTAMP
#                     );
#                 """))
                
#                 # Create sessions table
#                 conn.execute(text("""
#                     CREATE TABLE IF NOT EXISTS sessions (
#                         id SERIAL PRIMARY KEY,
#                         user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
#                         session_token VARCHAR(512) UNIQUE NOT NULL,
#                         expires_at TIMESTAMP NOT NULL,
#                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         ip_address VARCHAR(45),
#                         user_agent VARCHAR(512)
#                     );
#                 """))
                
#                 # Create audit log table
#                 conn.execute(text("""
#                     CREATE TABLE IF NOT EXISTS audit_logs (
#                         id SERIAL PRIMARY KEY,
#                         user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
#                         action VARCHAR(255) NOT NULL,
#                         details TEXT,
#                         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         ip_address VARCHAR(45)
#                     );
#                 """))
                
#                 # Create indexes
#                 conn.execute(text("""
#                     CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
#                 """))
#                 conn.execute(text("""
#                     CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
#                 """))
#                 conn.execute(text("""
#                     CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
#                 """))
                
#                 conn.commit()
            
#             print("[OK] Database schema initialized")
#         except Exception as e:
#             print(f"[WARN] Schema initialization: {e}")
    
#     @staticmethod
#     def hash_password(password: str) -> str:
#         """Hash password using werkzeug's Bcrypt"""
#         from werkzeug.security import generate_password_hash
#         return generate_password_hash(password, method='pbkdf2:sha256')
    
#     @staticmethod
#     def verify_password(password: str, password_hash: str) -> bool:
#         """Verify password against hash"""
#         from werkzeug.security import check_password_hash
#         return check_password_hash(password_hash, password)
    
#     def user_exists(self, username: str) -> bool:
#         """Check if username exists in database"""
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 result = conn.execute(
#                     text("SELECT id FROM users WHERE username = :username"),
#                     {"username": username}
#                 )
#                 return result.fetchone() is not None
#         except Exception as e:
#             print(f"[ERROR] user_exists: {e}")
#             return False
    
#     def email_exists(self, email: str) -> bool:
#         """Check if email exists in database"""
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 result = conn.execute(
#                     text("SELECT id FROM users WHERE email = :email"),
#                     {"email": email}
#                 )
#                 return result.fetchone() is not None
#         except Exception as e:
#             print(f"[ERROR] email_exists: {e}")
#             return False
    
#     def register_user(self, username: str, email: str, name: str, password: str) -> dict:
#         """Register new user - SAVE TO DATABASE"""
#         try:
#             from sqlalchemy import text
            
#             # Check if username already exists
#             if self.user_exists(username):
#                 return {'success': False, 'message': 'Username already exists'}
            
#             # Check if email already exists
#             if self.email_exists(email):
#                 return {'success': False, 'message': 'Email already registered'}
            
#             # Hash password
#             pwd_hash = self.hash_password(password)
            
#             # Insert user into database
#             with self.engine.connect() as conn:
#                 result = conn.execute(
#                     text("""
#                         INSERT INTO users (username, email, name, password_hash)
#                         VALUES (:username, :email, :name, :pwd_hash)
#                         RETURNING id
#                     """),
#                     {
#                         'username': username,
#                         'email': email,
#                         'name': name,
#                         'pwd_hash': pwd_hash
#                     }
#                 )
#                 user_id = result.fetchone()[0]
#                 conn.commit()
            
#             self._log_action(user_id, f'New account created: {username}')
#             print(f"[OK] User registered in database: {username} (ID: {user_id})")
            
#             return {
#                 'success': True,
#                 'message': 'User registered successfully',
#                 'user_id': user_id
#             }
#         except Exception as e:
#             print(f"[ERROR] register_user: {e}")
#             return {'success': False, 'message': f'Registration error: {str(e)[:100]}'}
    
#     def authenticate_user(self, username: str, password: str, ip_address: str = None) -> dict:
#         """
#         Authenticate user against DATABASE
#         Returns: {success: bool, message: str, user_id: int, session_token: str, user_data: dict}
#         """
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 # Query user from database
#                 result = conn.execute(
#                     text("""
#                         SELECT id, password_hash, is_active, login_attempts, locked_until
#                         FROM users
#                         WHERE username = :username
#                     """),
#                     {"username": username}
#                 )
#                 user_row = result.fetchone()
                
#                 # User not found in database
#                 if not user_row:
#                     self._log_action(None, f'Failed login: user not found ({username})', ip_address)
#                     print(f"[WARN] Login failed - user not found: {username}")
#                     return {
#                         'success': False,
#                         'message': 'Invalid username or password'
#                     }
                
#                 user_id, pwd_hash, is_active, login_attempts, locked_until = user_row
                
#                 # Check if account is locked
#                 if locked_until:
#                     from datetime import datetime
#                     if datetime.now() < locked_until:
#                         self._log_action(user_id, 'Login attempt - account locked', ip_address)
#                         return {
#                             'success': False,
#                             'message': 'Account locked due to multiple failed attempts. Try again later.'
#                         }
                
#                 # Check if account is active
#                 if not is_active:
#                     self._log_action(user_id, 'Login attempt - account inactive', ip_address)
#                     return {
#                         'success': False,
#                         'message': 'Account is inactive'
#                     }
                
#                 # Verify password against stored hash
#                 if not self.verify_password(password, pwd_hash):
#                     new_attempts = login_attempts + 1
#                     locked_until_val = None
                    
#                     # Lock account after 5 failed attempts
#                     if new_attempts >= 5:
#                         from datetime import datetime, timedelta
#                         locked_until_val = (datetime.now() + timedelta(minutes=15)).isoformat()
                    
#                     conn.execute(
#                         text("""
#                             UPDATE users
#                             SET login_attempts = :attempts,
#                                 locked_until = :locked
#                             WHERE id = :user_id
#                         """),
#                         {
#                             'attempts': new_attempts,
#                             'locked': locked_until_val,
#                             'user_id': user_id
#                         }
#                     )
#                     conn.commit()
                    
#                     self._log_action(user_id, 'Failed login attempt', ip_address)
#                     print(f"[WARN] Login failed - incorrect password: {username} (attempt {new_attempts})")
                    
#                     return {
#                         'success': False,
#                         'message': 'Invalid username or password'
#                     }
                
#                 # ✅ PASSWORD CORRECT - CREATE SESSION
#                 session_token = secrets.token_urlsafe(64)
#                 from datetime import datetime, timedelta
#                 expires_at = (datetime.now() + timedelta(days=7)).isoformat()
                
#                 # Reset login attempts and update last login
#                 conn.execute(
#                     text("""
#                         UPDATE users
#                         SET last_login = CURRENT_TIMESTAMP,
#                             login_attempts = 0,
#                             locked_until = NULL
#                         WHERE id = :user_id
#                     """),
#                     {"user_id": user_id}
#                 )
                
#                 # Create session token
#                 conn.execute(
#                     text("""
#                         INSERT INTO sessions (user_id, session_token, expires_at, ip_address)
#                         VALUES (:user_id, :token, :expires, :ip)
#                     """),
#                     {
#                         'user_id': user_id,
#                         'token': session_token,
#                         'expires': expires_at,
#                         'ip': ip_address
#                     }
#                 )
#                 conn.commit()
                
#                 # Get user data
#                 user_result = conn.execute(
#                     text("""
#                         SELECT id, username, email, name, created_at
#                         FROM users
#                         WHERE id = :user_id
#                     """),
#                     {"user_id": user_id}
#                 )
#                 user_data_row = user_result.fetchone()
                
#                 self._log_action(user_id, 'Successful login', ip_address)
#                 print(f"[OK] User authenticated from database: {username}")
                
#                 return {
#                     'success': True,
#                     'message': 'Login successful',
#                     'user_id': user_id,
#                     'session_token': session_token,
#                     'user_data': {
#                         'id': user_data_row[0],
#                         'username': user_data_row[1],
#                         'email': user_data_row[2],
#                         'name': user_data_row[3],
#                         'created_at': str(user_data_row[4])
#                     }
#                 }
#         except Exception as e:
#             print(f"[ERROR] authenticate_user: {e}")
#             import traceback
#             traceback.print_exc()
#             return {
#                 'success': False,
#                 'message': f'Authentication error: {str(e)[:100]}'
#             }
    
#     def logout(self, session_token: str) -> bool:
#         """Logout user - invalidate session"""
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 conn.execute(
#                     text("DELETE FROM sessions WHERE session_token = :token"),
#                     {"token": session_token}
#                 )
#                 conn.commit()
#             print(f"[OK] User logged out")
#             return True
#         except Exception as e:
#             print(f"[ERROR] logout: {e}")
#             return False
    
#     def _log_action(self, user_id: int = None, action: str = None, ip_address: str = None):
#         """Log user action to audit table"""
#         try:
#             from sqlalchemy import text
            
#             with self.engine.connect() as conn:
#                 conn.execute(
#                     text("""
#                         INSERT INTO audit_logs (user_id, action, ip_address)
#                         VALUES (:user_id, :action, :ip)
#                     """),
#                     {
#                         'user_id': user_id,
#                         'action': action,
#                         'ip': ip_address
#                     }
#                 )
#                 conn.commit()
#         except Exception as e:
#             print(f"[WARN] Failed to log action: {e}")

# ═══════════════════════════════════════════════════════════════
# IMPORTS - Modular Architecture
# ═══════════════════════════════════════════════════════════════

from core.config import *
from core.auth import register_user, authenticate_user, logout_user
from core.db_session import _current_db
from core.components import kpi_card, filter_control, chart_container
from core.data_profiler import DataProfiler, get_filter_candidates, get_key_metrics
from core.formatters import Formatter
from core.auth import PasswordManager, SessionValidator
from intelligence.layout_builder import LayoutBuilder
from intelligence.insight_extractor import InsightExtractor
from intelligence.llm_analyzer import LLMAnalyzer
from intelligence.analysis_formatter import AnalysisFormatter
from intelligence.chart_analyzer import ChartAnalyzer
from llm.config import LLMFactory, DEFAULT_CONFIG
from llm.prompts import build_big_four_prompt

# Import page modules
from pages import page_data_review, page_config, page_dashboard, page_upload, page_auth
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import callback_context
import callbacks.db_callbacks
import callbacks.company_callbacks
import callbacks.mapping_callbacks
from callbacks.dashboard_callbacks import register_dashboard_callbacks
from core.dashboard_store import save as save_dashboard, list_saved, load as load_dashboard, delete as delete_dashboard
from core import db_connector
from core import query_builder

# ═══════════════════════════════════════════════════════════════
# INITIALIZE AUTHENTICATOR
# ═══════════════════════════════════════════════════════════════

# print("\n" + "="*70)
# print("[STARTUP] Initializing AI-INSIGHT Dashboard")
# print("="*70)

# authenticator = None
# try:
#     authenticator = PostgreSQLAuthenticator()
#     print("[OK] PostgreSQL authenticator initialized - ALL USERS STORED IN DATABASE")
# except Exception as e:
#     print(f"[CRITICAL ERROR] Failed to initialize authenticator: {e}")
#     print("[CRITICAL ERROR] Dashboard cannot start without database connection")
#     raise


# ═══════════════════════════════════════════════════════════════
# PHASE 1: DATA LOADING (Only after authentication)
# ═══════════════════════════════════════════════════════════════

def load_data(path: str) -> pd.DataFrame:
    """Load data from cache or CSV or generate sample"""
    from core.cache_manager import CacheManager

    active_upload_path = CacheManager.get_active_upload_path()
    if active_upload_path and os.path.exists(active_upload_path):
        print(f"[OK] Loading active user upload: {active_upload_path}")
        try:
            with open(active_upload_path, 'rb') as f:
                df = pickle.load(f)
            print(f"[OK] Loaded {df.shape[0]:,} rows x {df.shape[1]} cols from user upload")
            return df
        except Exception as e:
            print(f"[WARN] Failed to load active upload: {e}, falling back to default")

    if path and os.path.exists(path):
        df = pd.read_csv(path, parse_dates=True)
        print(f"[OK] Loaded real data from {path} -> {df.shape[0]:,} rows x {df.shape[1]} cols")
        return df

    print("[INFO] CSV not found - using built-in sample data")
    np.random.seed(42)
    n = 500
    categories = ["Electronics", "Clothing", "Food", "Furniture", "Sports"]
    regions = ["North", "South", "East", "West"]
    dates = pd.date_range("2023-01-01", periods=n, freq="D")

    df = pd.DataFrame({
        "date": np.random.choice(dates, n),
        "category": np.random.choice(categories, n),
        "region": np.random.choice(regions, n),
        "sales": np.random.randint(100, 5000, n),
        "profit": np.random.randint(10, 1000, n),
        "units": np.random.randint(1, 50, n),
        "discount": np.round(np.random.uniform(0, 0.4, n), 2),
    })
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# print("\n[INFO] Phase 1: Loading data...")
df = load_data(None)

cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
os.makedirs(cache_dir, exist_ok=True)
df_pickle_path = os.path.join(cache_dir, 'dataframe.pkl')
profiles_json_path = os.path.join(cache_dir, 'profiles.json')

from pandas.api.types import is_numeric_dtype as _is_num_startup

df_processed = df.copy()
_coerced = 0
for _col in df_processed.columns:
    if not _is_num_startup(df_processed[_col]):
        try:
            _cleaned = (df_processed[_col].astype(str)
                        .str.replace(r'[,\u20B9$\u20AC\xa3]', '', regex=True)
                        .str.strip())
            _converted = pd.to_numeric(_cleaned, errors='coerce')
            if _converted.notna().sum() / max(len(df_processed), 1) > 0.5:
                df_processed[_col] = _converted
                _coerced += 1
        except Exception:
            pass
# print(f"[OK] Startup coercion: {_coerced} columns converted to numeric")

with open(df_pickle_path, 'wb') as f:
    pickle.dump(df_processed, f)
# print(f"[OK] DataFrame cached to {df_pickle_path}")

def get_cached_dataframe():
    """Load dataframe from cache"""
    df = None
    try:
        from core.cache_manager import CacheManager
        active_path = CacheManager.get_active_upload_path()
        if active_path and os.path.exists(active_path):
            with open(active_path, 'rb') as f:
                df = pickle.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load active upload: {e}")

    if df is None:
        try:
            with open(df_pickle_path, 'rb') as f:
                df = pickle.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load cached dataframe: {e}")
            return None

    return df.copy()

def load_cached_profiles():
    """Load column profiles"""
    try:
        from core.cache_manager import CacheManager
        upload_profiles_path = CacheManager.get_active_upload_profiles_path()
        if upload_profiles_path and os.path.exists(upload_profiles_path):
            with open(upload_profiles_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load upload profiles: {e}")

    try:
        with open(profiles_json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not load profiles: {e}")
        return {}

# ═══════════════════════════════════════════════════════════════
# PHASE 2: AUTO-ANALYSIS (Intelligence Layer)
# ═══════════════════════════════════════════════════════════════

# print("\n[INFO] Phase 2: Analyzing data structure...")
profiler = DataProfiler()
profiles = profiler.profile(df)

# print("[OK] Data Analysis:")
for name, profile in profiles.items():
    print(f"  - {name}: {profile.dtype} (cardinality={profile.cardinality}, missing={profile.missing_pct:.1f}%)")

profiles_dict = {
    name: {
        'dtype': profile.dtype,
        'cardinality': profile.cardinality,
        'missing_pct': profile.missing_pct,
        'value_range': profile.value_range if hasattr(profile, 'value_range') else None,
        'top_values': profile.top_values if hasattr(profile, 'top_values') else None,
        'is_temporal': profile.is_temporal,
        'has_outliers': profile.has_outliers if hasattr(profile, 'has_outliers') else False,
    }
    for name, profile in profiles.items()
}
with open(profiles_json_path, 'w') as f:
    json.dump(profiles_dict, f, indent=2, default=str)
print(f"[OK] Profiles cached to {profiles_json_path}")

print("\n[INFO] Phase 1-2: Generating auto-layout...")
builder = LayoutBuilder()
auto_config = builder.build_config(profiles)
print(f"[OK] Auto-generated {len(auto_config.charts)} charts, {len(auto_config.filters)} filters, {len(auto_config.kpis)} KPIs")

insight_extractor = InsightExtractor()
insights = insight_extractor.extract(df, profiles)
if insights:
    print("\n[WARN] Data Quality Issues:")
    for insight in insights:
        print(f"  - {insight.description}")

# ═══════════════════════════════════════════════════════════════
# PHASE 3: LLM ANALYSIS
# ═══════════════════════════════════════════════════════════════

llm_config = None
llm_config_obj = None
llm_analyzer = None
provider = None
dashboard_config = auto_config

try:
    config_paths = [
        "llm_config.json",
        os.path.join(os.path.dirname(__file__), "llm_config.json"),
        os.path.join(os.getcwd(), "llm_config.json"),
    ]

    llm_config_path = None
    for path in config_paths:
        if os.path.exists(path):
            llm_config_path = path
            break

    if llm_config_path:
        with open(llm_config_path) as f:
            llm_config = json.load(f)
        print(f"\n[OK] Found llm_config.json at: {llm_config_path}")
        print(f"[OK] Loaded LLM config: provider={llm_config.get('provider')}")

        config_obj = DEFAULT_CONFIG
        if llm_config.get('provider'):
            config_obj.provider = llm_config['provider']
        if llm_config.get('model_name'):
            config_obj.model_name = llm_config['model_name']
        if llm_config.get('base_url'):
            config_obj.base_url = llm_config['base_url']
        if llm_config.get('api_key'):
            config_obj.api_key = llm_config['api_key']
        if llm_config.get('include_sample_data') is not None:
            config_obj.include_sample_data = llm_config['include_sample_data']

        llm_config_obj = config_obj

        print("\n[INFO] Phase 3: Analyzing with LLM...")
        print(f"[INFO] Using provider: {config_obj.provider} at {config_obj.base_url}")

        try:
            print("[INFO] Creating LLM provider and analyzer...")
            provider = LLMFactory.create(config_obj)
            llm_analyzer = LLMAnalyzer(provider, config_obj)
            print("[OK] LLM analyzer created successfully")

            user_context = f"Dataset contains {len(df):,} records with {len(profiles)} columns."

            print(f"[INFO] Running startup LLM analysis...")

            try:
                llm_config_result = llm_analyzer.analyze(df, profiles, user_context)
                if llm_config_result:
                    dashboard_config = llm_config_result
                    print("[OK] LLM analysis successful")
                else:
                    dashboard_config = auto_config
                    print("[WARN] LLM returned empty result")
            except (TimeoutError, ConnectionError):
                print(f"[WARN] LLM analysis timeout")
                dashboard_config = auto_config
            except Exception as e:
                print(f"[WARN] LLM analysis failed: {type(e).__name__}")
                dashboard_config = auto_config

        except Exception as e:
            print(f"[WARN] LLM initialization failed: {type(e).__name__}")
            dashboard_config = auto_config
            llm_analyzer = None

    else:
        dashboard_config = auto_config
        print("\n[INFO] llm_config.json not found - using auto-layout only")

except Exception as e:
    print(f"[ERROR] LLM initialization error: {e}")
    dashboard_config = auto_config

chart_analyzer = None
if llm_analyzer is not None and provider is not None:
    try:
        chart_analyzer = ChartAnalyzer(provider, llm_config_obj)
        print("[OK] Chart analyzer initialized")
    except Exception as e:
        print(f"[WARN] Chart analyzer initialization failed: {e}")

# ═══════════════════════════════════════════════════════════════
# PHASE 4: DASH APP LAYOUT
# ═══════════════════════════════════════════════════════════════

app = Dash(__name__, suppress_callback_exceptions=True, title="Onex AI Data Insight",
           external_stylesheets=[dbc.themes.BOOTSTRAP])

print("\n[INFO] Pre-initializing store data...")
df_json = df.to_json(orient='split')

profiles_dict = {}
for col_name, profile in profiles.items():
    profiles_dict[col_name] = {
        'dtype': profile.dtype,
        'cardinality': profile.cardinality,
        'missing_pct': profile.missing_pct,
        'top_values': profile.top_values,
        'is_temporal': profile.is_temporal,
    }

config_dict = dashboard_config.to_dict() if hasattr(dashboard_config, 'to_dict') else {}

print("[OK] Store data pre-initialized")

# ═══════════════════════════════════════════════════════════════
# NAVBAR - Only visible after login
# ═══════════════════════════════════════════════════════════════

NAV_STEPS = [
    ('/upload',    'Upload Data',          '1'),
    ('/data-review','Review Data',         '2'),
    ('/config',    'Config',               '3'),
    ('/dashboard', 'Dashboard',            '4'),
    ('/companies', 'Companies',            '5'),
    ('/mapping', 'Mapping',                '6')
]

# def make_navbar():
#     """Render navigation bar - ONLY after login"""
#     nav_items = []
#     for path, label, step in NAV_STEPS:
#         nav_items.append(
#             dcc.Link(
#                 html.Div([
#                     html.Span(step, style={
#                         'width': '24px', 'height': '24px', 'lineHeight': '24px',
#                         'borderRadius': '50%', 'textAlign': 'center', 'fontSize': '11px',
#                         'fontWeight': '800', 'display': 'inline-block', 'marginRight': '8px',
#                         'backgroundColor': '#D4AF37',
#                         'color': '#1A365D',
#                     }),
#                     html.Span(label, style={
#                         'fontSize': '13px', 'fontWeight': '600',
#                         'color': 'rgba(255,255,255,0.90)',
#                     }),
#                 ], style={
#                     'display': 'flex', 'alignItems': 'center', 'padding': '8px 16px',
#                     'borderRadius': '4px',
#                     'backgroundColor': 'rgba(255,255,255,0.05)',
#                     'hover': {'backgroundColor': 'rgba(255,255,255,0.1)'},
#                 }),
#                 href=path, style={'textDecoration': 'none'}
#             )
#         )

#     logout_btn = dbc.Button(
#         "Logout",
#         id='btn-logout',
#         color='danger',
#         outline=True,
#         size='sm',
#         style={'marginLeft': 'auto'}
#     )

#     return html.Div([
#         html.Div([
#             html.Div("◆", style={'fontSize': '24px', 'color': '#D4AF37', 'marginRight': '12px'}),
#             html.Div([
#                 html.Div("ONEX AI", style={
#                     'fontSize': '14px', 'fontWeight': '800', 'color': '#D4AF37',
#                     'letterSpacing': '0.15em', 'lineHeight': '1',
#                 }),
#                 html.Div("Data Insight", style={
#                     'fontSize': '11px', 'color': 'rgba(255,255,255,0.7)',
#                     'letterSpacing': '0.05em', 'lineHeight': '1', 'marginTop': '3px',
#                 }),
#             ]),
#         ], style={'display': 'flex', 'alignItems': 'center'}),

#         html.Div(nav_items, style={'display': 'flex', 'gap': '8px', 'alignItems': 'center', 'flex': '1'}),
        
#         logout_btn,
#     ], style={
#         'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
#         'backgroundColor': '#1A365D',
#         'padding': '14px 32px',
#         'borderBottom': '3px solid #D4AF37',
#         'position': 'sticky', 'top': '0', 'zIndex': '1000',
#         'boxShadow': '0 2px 12px rgba(0,0,0,0.18)',
#     })


def make_navbar(session_data, pathname):

    username = session_data.get("username", "User")
    role_id = session_data.get("role_id")

    role_name = "Admin" if role_id == 1 else "User"

    #  helper → active highlight (NO icons now)
    def nav_item(label, href):
        active = pathname == href

        return dcc.Link(
            label,
            href=href,
            style={
                'padding': '6px 12px',
                'borderRadius': '6px',
                'textDecoration': 'none',
                'fontSize': '14px',
                'fontWeight': '600',
                'color': '#1A365D' if not active else 'white',
                'backgroundColor': '#E2E8F0' if not active else '#2B6CB0',
                'transition': 'all 0.2s'
            }
        )

    #  COMMON FLOW
    nav_links = [
        nav_item("Upload", "/upload"),
        nav_item("Data Review", "/data-review"),
        nav_item("Config", "/config"),
        nav_item("Dashboard", "/dashboard"),
    ]

    #  ADMIN EXTRA LINKS
    if role_id == 1:
        nav_links += [
            nav_item("Users", "/users"),
            nav_item("Companies", "/companies"),
            nav_item("Mapping", "/mapping"),
        ]

    return html.Div([

        #  LEFT LOGO
        html.Div([
            html.Div("◆", style={
                'fontSize': '18px',
                'color': '#2B6CB0',
                'marginRight': '8px'
            }),

            html.Div([
                html.Div("ONEX AI", style={
                    'fontSize': '15px',
                    'fontWeight': '800',
                    'color': '#1A365D'
                }),
                html.Div("Data Insight Platform", style={
                    'fontSize': '10px',
                    'color': '#718096'
                }),
            ])
        ], style={'display': 'flex', 'alignItems': 'center'}),

        #  CENTER NAV
        html.Div(nav_links, style={
            'display': 'flex',
            'gap': '12px',
            'alignItems': 'center'
        }),

        #  RIGHT USER + LOGOUT
        html.Div([

            html.Div([
                html.Div(username, style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': '#1A365D'
                }),
                html.Div(role_name, style={
                    'fontSize': '11px',
                    'color': '#718096'
                }),
            ], style={'marginRight': '15px'}),

            dbc.Button(
                "Logout",
                id='btn-logout',
                color='danger',
                size='sm'
            )

        ], style={'display': 'flex', 'alignItems': 'center'})

    ], style={
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
        'padding': '10px 20px',
        'backgroundColor': '#F7FAFC',
        'borderBottom': '1px solid #E2E8F0',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.05)'
    })
# ═══════════════════════════════════════════════════════════════
# APP LAYOUT
# ═══════════════════════════════════════════════════════════════

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Navbar - rendered conditionally based on authentication
    html.Div(id='navbar-container'),

    # Session state - stored in browser localStorage
    dcc.Store(id='session-state', storage_type='local', data={}),
    dcc.Store(id='store-upload-id', storage_type='memory', data=None),
    dcc.Store(id='store-global-dataframe', storage_type='memory', data=df_json),
    dcc.Store(id='store-global-profiles', storage_type='memory', data=profiles_dict),
    dcc.Store(id='store-initial-config', storage_type='memory', data=config_dict),

    dcc.Store(id='store-kpi-selections', storage_type='memory', data=[]),
    dcc.Store(id='store-filter-selections', storage_type='memory', data=[]),

    dcc.Store(id='store-ai-suggestions', storage_type='memory', data=None),
    dcc.Store(id='store-objective', storage_type='memory', data=''),
    dcc.Store(id='store-executive-summary', storage_type='memory', data=None),

    dcc.Store(id='store-confirmed-dtypes', storage_type='memory', data={}),

    dcc.Store(id='db-conditions-store', storage_type='memory', data=[]),

    # Page content - changes based on URL
    html.Div(id='page-content'),
], style={'fontFamily': "'Segoe UI', Arial, sans-serif", 'backgroundColor': '#F7FAFC'})

# ═══════════════════════════════════════════════════════════════
# CALLBACKS - ROUTING & AUTHENTICATION
# ═══════════════════════════════════════════════════════════════

# 🔐 SIGN IN CALLBACK - Validate against PostgreSQL database
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('auth-message-container', 'children'),
    Output('session-state', 'data', allow_duplicate=True),
    Input('auth-btn-signin', 'n_clicks'),
    State('auth-signin-username', 'value'),
    State('auth-signin-password', 'value'),
    State('session-state', 'data'),
    prevent_initial_call=True
)
def handle_signin(n_clicks, username, password, session_data):
    print(" Signin clicked", n_clicks, username)  # DEBUG

    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    if not username or not password:
        return dash.no_update, dbc.Alert("Please enter username and password", color="warning"), dash.no_update

    session_data = session_data or {}

    from core.auth import register_user, authenticate_user
    result = authenticate_user(username, password)

    # print(" Auth result:", result)  # DEBUG

    if result['success']:
        result = authenticate_user(username, password)

        if result['success']:
            session_data.update({
                "is_authenticated": True,
                "username": result['user_data']['username'],
                "user_id": result['user_data']['id'],
                "email": result['user_data']['email'],
                "name": result['user_data']['name'],
                "role_id": result['user_data']['role_id']   # ✅ ADD THIS
            })

            return '/upload', dash.no_update, session_data

        # print("✅ LOGIN SUCCESS → redirecting")

        return '/upload', dash.no_update, session_data

    #  failure
    return dash.no_update, dbc.Alert(result['message'], color="danger"), dash.no_update


# SIGN UP CALLBACK - Register user in PostgreSQL database
@app.callback(
    Output('auth-message-container', 'children', allow_duplicate=True),
    Output('session-state', 'data', allow_duplicate=True),
    Input('auth-btn-signup', 'n_clicks'),
    State('auth-signup-name', 'value'),
    State('auth-signup-email', 'value'),
    State('auth-signup-username', 'value'),
    State('auth-signup-password', 'value'),
    State('auth-signup-password-confirm', 'value'),
    State('auth-signup-role', 'value'),
    State('session-state', 'data'),
    prevent_initial_call=True
)
def handle_signup(n_clicks, name, email, username, password, password_confirm, role_id, session_data):
    """Handle user sign up - REGISTER IN DATABASE"""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    session_data = session_data or {}

    # Validation
    if not all([name, email, username, password, password_confirm, role_id]):
        return dbc.Alert("All fields are required", color="warning"), dash.no_update
    
    if not role_id:
        return dbc.Alert("Please select a role", color="warning"), dash.no_update

    if not SessionValidator.is_valid_email(email):
        return dbc.Alert("Invalid email address", color="warning"), dash.no_update

    is_valid_user, user_msg = SessionValidator.validate_username(username)
    if not is_valid_user:
        return dbc.Alert(user_msg, color="warning"), dash.no_update

    is_valid_pwd, pwd_msg = SessionValidator.is_strong_password(password)
    if not is_valid_pwd:
        return dbc.Alert(pwd_msg, color="warning"), dash.no_update

    if password != password_confirm:
        return dbc.Alert("Passwords do not match", color="warning"), dash.no_update
    
   
    # ✅ REGISTER USER IN DATABASE
    reg_result = register_user(username, email, name, password, role_id)
    
    if not reg_result['success']:
        return dbc.Alert(reg_result['message'], color="warning"), dash.no_update

    # ✅ AUTO-LOGIN after signup
    auth_result = authenticate_user(username, password)
    
    if auth_result['success']:
        session_data.update({
            "is_authenticated": True,
            "username": auth_result['user_data']['username'],
            "user_id": auth_result['user_data']['id'],
            "email": auth_result['user_data']['email'],
            "name": auth_result['user_data']['name'],
            "role_id": auth_result['user_data']['role_id']   # ✅ ADD THIS
        })

        success = dbc.Alert(
            [
                html.H4("Account Created!", className="alert-heading"),
                html.P(f"Welcome {name}! You are now logged in."),
            ],
            color="success",
            style={'marginTop': '20px'}
        )
        print(f"[OK] New user registered and logged in: {username}")
        return success, session_data

    return dbc.Alert("Account created, but login failed.", color="warning"), dash.no_update


# 🚪 LOGOUT CALLBACK
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Output('session-state', 'data', allow_duplicate=True),
    Input('btn-logout', 'n_clicks'),
    State('session-state', 'data'),
    prevent_initial_call=True
)
def handle_logout(n_clicks, session_data):
    """Handle user logout"""
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    session_data = session_data or {}
    
    session_token = session_data.get('session_token')
    if session_token:
        logout_user()
    
    session_data.clear()
    print("[OK] User logged out")
    
    return '/auth', session_data


@app.callback(
    Output('navbar-container', 'children'),
    Input('session-state', 'data'),
    Input('url', 'pathname'),   # ✅ ADD THIS
    prevent_initial_call=False
)

def update_navbar_visibility(session_data, pathname):

    session_data = session_data or {}

    is_authenticated = session_data.get("is_authenticated", False)

    if not is_authenticated or pathname in ["/", "/auth", "/login"]:
        return ""

    return make_navbar(session_data, pathname)   # ✅ PASS pathname



# 📄 PAGE ROUTING CALLBACK
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    [State('store-global-dataframe', 'data'),
    State('store-global-profiles', 'data'),
    State('store-objective', 'data'),
    State('store-initial-config', 'data'),
    State('store-ai-suggestions', 'data'),
    State('session-state', 'data'),
    State('store-kpi-selections', 'data'),
    State('store-filter-selections', 'data')],
    prevent_initial_call=False
)
def display_page(pathname, df_json, profiles_dict,  objective_data, config_dict, ai_suggestions, session_data, store_kpi_data, store_filter_data):
    """Route to appropriate page based on URL and authentication"""
    if not pathname or pathname == '':
        pathname = '/'

    pathname = str(pathname).strip()
    
    session_data = session_data or {}
    is_authenticated = session_data.get("is_authenticated", False)

    #  Block all pages except /auth if not authenticated
    if pathname != '/auth' and not is_authenticated:
        return page_auth.generate_auth_page()

    #  Redirect authenticated users away from /auth page
    if pathname == '/auth' and is_authenticated:
        return page_upload.generate_upload_page()
   
    try:
        # Show auth page
        if pathname == '/auth' or pathname == '/login' or pathname == '/':
            return page_auth.generate_auth_page()

        # Check data for other routes
        if not df_json or not profiles_dict:
            return html.Div(
                [
                    html.H3("Error: Data not initialized"),
                    html.P("Please refresh the page."),
                ],
                style={'padding': '20px', 'textAlign': 'center', 'color': 'red'}
            )

        current_df = get_cached_dataframe()
        if current_df is None:
            return html.Div(
                [html.H3("Error: Data not loaded"), html.P("Check server logs.")],
                style={'padding': '20px', 'color': 'red'}
            )

        current_profiles = load_cached_profiles()
        if not current_profiles:
            return html.Div(
                [html.H3("Error: Profiles not available"), html.P("Check server logs.")],
                style={'padding': '20px', 'color': 'red'}
            )

        confirmed_dtypes = session_data.get('confirmed_dtypes', {})
        if not confirmed_dtypes:
            confirmed_dtypes = {}
            for col, profile_data in current_profiles.items():
                confirmed_dtypes[col] = profile_data.get('dtype', 'categorical')

        # Route to pages
        if pathname == '/upload':
            return page_upload.generate_upload_page()

        elif pathname == '/config':
            return page_config.generate_config_page(current_df, current_profiles, confirmed_dtypes)

        elif pathname == '/dashboard':
            # Give priority to loaded dashboard values
            kpi_selections = session_data.get('kpi_selections', store_kpi_data or [])
            filter_selections = session_data.get('filter_selections', store_filter_data or [])

            print("=" *80)
            print("DASHBOARD PAGE")
            print("AI_SUGGESTIONS TYPE:", type(ai_suggestions))
            print("AI_SUGGESTIONS:", ai_suggestions)
            print("=" * 80)
            

            # llm_analysis = None
            # if config_dict:
            #     llm_analysis = AnalysisFormatter.format_analysis(
            #         type('DashboardConfig', (), config_dict)() if isinstance(config_dict, dict) else config_dict
            #     )
            
            effective_config = ai_suggestions or config_dict
            
            llm_analysis = None
            if effective_config:
                llm_analysis = AnalysisFormatter.format_analysis(
                    type('DashboardConfig', (), effective_config)() if isinstance(effective_config, dict) else effective_config
                )

            result = page_dashboard.generate_dashboard_page(
                current_df,
                kpi_selections=kpi_selections,
                filter_selections=filter_selections,
                confirmed_dtypes=confirmed_dtypes,
                llm_analysis=llm_analysis
            )
            return result
        
        elif pathname == '/data-review':
            return page_data_review.generate_data_review_page(current_df, current_profiles)
        
        elif pathname == '/companies':
            from pages import page_companies
            return page_companies.generate_companies_page()
        
        elif pathname == '/mapping':
            from pages import page_user_company
            return page_user_company.generate_mapping_page()

        else:
            return page_auth.generate_auth_page()

    except Exception as e:
        import traceback
        print(f"[ERROR] display_page: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return html.Div(
            [html.H3("Error loading page"), html.P("Check server logs.")],
            style={'padding': '20px', 'backgroundColor': '#ffeeee', 'color': '#cc0000'}
        )


# Sync configuration selections
@app.callback(
    Output('session-state', 'data'),
    [Input('store-kpi-selections', 'data'),
    Input('store-filter-selections', 'data'),
    Input('store-confirmed-dtypes', 'data')],
    [State('session-state', 'data'),
    State('store-objective', 'data')],
    prevent_initial_call=True
)
def sync_config_to_session(kpi_data, filter_data, confirmed_dtypes, session_data, objective_data):
    """Sync configuration selections"""
    if session_data is None:
        session_data = {}

    if kpi_data:
        session_data['kpi_selections'] = kpi_data
    if filter_data:
        session_data['filter_selections'] = filter_data
    if confirmed_dtypes:
        session_data['confirmed_dtypes'] = confirmed_dtypes
    if objective_data:
        session_data['objective'] = objective_data

    return session_data

@app.callback(
    Output('store-confirmed-dtypes', 'data'),
    Input({'type': 'dtype-selector', 'index': ALL}, 'value'),
    State({'type': 'dtype-selector', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def save_confirmed_dtypes(dtype_values, selector_ids):
    """Save data type selections"""
    if not dtype_values or not selector_ids:
        raise dash.exceptions.PreventUpdate
    return {sid['index']: val for sid, val in zip(selector_ids, dtype_values) if val}


from core.db_connector import fetch

@app.callback(
    Output('store-global-dataframe', 'data'),
    Input('db-table-dropdown', 'value'),   # 🔥 when table is selected
    prevent_initial_call=True
)
def load_table_data(table):

    if not table:
        raise dash.exceptions.PreventUpdate

    print(f"[INFO] Selected table = {table}")

    engine = _current_db.get('engine')
    db_type = _current_db.get('db_type', 'postgresql')

    if not engine:
        print("[ERROR] No engine found in _current_db")
        raise dash.exceptions.PreventUpdate

    try:
        print(f"[INFO] Loading table: {table}")

        df = fetch(
            engine,
            table=table,
            db_type=db_type
        )

        from core.cache_manager import CacheManager
        
        CacheManager.save_upload(df, f"database_{table}")
        print(f"[OK] Loaded {len(df)} rows")

        return df.to_json(
            date_format='iso',
            orient='split'
        )

    except Exception as e:
        print(f"[ERROR] {e}")
        raise dash.exceptions.PreventUpdate
    
# def load_table_data(table):

#     if not table:
#         raise dash.exceptions.PreventUpdate

#     engine = _current_db.get('engine')
#     db_type = _current_db.get('db_type', 'postgresql')

#     if not engine:
#         raise dash.exceptions.PreventUpdate

#     df = fetch(
#         engine,
#         table=table,
#         db_type=db_type
#         )


#     return df.to_json(date_format='iso', orient='split')


# ═══════════════════════════════════════════════════════════════
# REGISTER DASHBOARD CALLBACKS
# ═══════════════════════════════════════════════════════════════

register_dashboard_callbacks(app, get_cached_dataframe, chart_analyzer)


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # print("\n" + "="*70)
    # print("[READY] AI-INSIGHT Dashboard ready!")
    # print("="*70)
    # print("\n📍 Database: PostgreSQL")
    # print("   Host: 192.168.202.114:5432")
    # print("   Database: ai_insight")
    # print("\n🔐 Authentication: PostgreSQL-backed")
    # print("   New users register → saved to database")
    # print("   Login validates against database")
    # print("   Session tokens with 7-day expiration")
    # print("   Account lockout after 5 failed attempts")
    # print("\n🎨 UI Features:")
    # print("   • Auth page: NO navbar (full-screen login/signup)")
    # print("   • After login: Navbar appears with navigation steps")
    # print("   • Logout returns to auth page")
    # print("\n🚀 Starting Dashboard at http://0.0.0.0:8050")
    # print("="*70 + "\n")
    
    app.run(host="0.0.0.0", port=8050, debug=True)