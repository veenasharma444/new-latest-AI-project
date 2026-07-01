"""
Dedicated Authentication Page
Enhanced login and signup with separate flows
Full-screen page with no navbar visible during auth
Authentication Page (Updated with Role Support)
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
from core.config import NAVY, GOLD, PRIMARY_BG, CARD_BG, TEXT, TEXT_LIGHT, BORDER, PRIMARY
from core.db_connector import get_session
from core.app_db import Role


def generate_auth_page():
    """Generate a beautiful full-screen standalone authentication page"""
    
    return html.Div([
        # Full-screen auth page (no navbar)
        html.Div([
            dbc.Row([
                # Left Side - Branding & Features
                dbc.Col([
                    html.Div([
                        # Logo
                        html.Div([
                            html.Div("◆", style={'fontSize': '56px', 'color': GOLD, 'marginBottom': '15px'}),
                            html.H1("ONEX AI", style={
                                'color': '#FFFFFF', 'fontWeight': '800', 
                                'marginBottom': '4px', 'fontSize': '42px', 'letterSpacing': '2px'
                            }),
                            html.P("Data Insight Platform", style={
                                'color': GOLD, 'fontSize': '16px', 'fontWeight': '600', 
                                'margin': '0', 'letterSpacing': '1px'
                            }),
                        ], style={'textAlign': 'center', 'marginBottom': '60px'}),
                        
                        # Features List
                        html.Div([
                            html.H3("Intelligent Analytics", style={
                                'color': '#FFFFFF', 'fontWeight': '700', 
                                'marginBottom': '24px', 'fontSize': '24px'
                            }),
                            *[
                                html.Div([
                                    html.Div("✓", style={
                                        'color': GOLD, 'fontWeight': '800', 'fontSize': '20px',
                                        'marginRight': '16px', 'width': '24px'
                                    }),
                                    html.Div(feature, style={
                                        'color': TEXT_LIGHT, 'fontSize': '15px', 
                                        'fontWeight': '500', 'lineHeight': '1.6'
                                    }),
                                ], style={'display': 'flex', 'alignItems': 'flex-start', 'marginBottom': '18px'})
                                for feature in [
                                    "Auto-detect data patterns in seconds",
                                    "Generate insightful dashboards automatically",
                                    "Connect multiple data sources seamlessly",
                                    "AI-powered insights and recommendations",
                                    "Real-time data analysis and monitoring",
                                ]
                            ],
                        ], style={'marginTop': '40px'}),
                        
                    ], style={
                        'backgroundColor': NAVY,
                        'padding': '60px 50px',
                        'minHeight': '100vh',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'color': '#FFFFFF',
                    }),
                ], xs=12, md=6, style={'padding': '0'}),
                
                # Right Side - Form
                dbc.Col([
                    html.Div([
                        # Tab Selection
                        dbc.Row([
                            dbc.Col([
                                html.Button(
                                    "Sign In",
                                    id='auth-btn-signin-tab',
                                    n_clicks=1,
                                    style={
                                        'background': 'none',
                                        'border': 'none',
                                        'fontSize': '18px',
                                        'fontWeight': '700',
                                        'color': NAVY,
                                        'cursor': 'pointer',
                                        'paddingBottom': '12px',
                                        'borderBottom': f'3px solid {NAVY}',
                                        'transition': 'all 0.3s ease',
                                    }
                                ),
                            ], width=6),
                            dbc.Col([
                                html.Button(
                                    "Create Account",
                                    id='auth-btn-signup-tab',
                                    n_clicks=0,
                                    style={
                                        'background': 'none',
                                        'border': 'none',
                                        'fontSize': '18px',
                                        'fontWeight': '700',
                                        'color': TEXT_LIGHT,
                                        'cursor': 'pointer',
                                        'paddingBottom': '12px',
                                        'transition': 'all 0.3s ease',
                                    }
                                ),
                            ], width=6),
                        ], style={
                            'borderBottom': f'2px solid {BORDER}', 
                            'marginBottom': '40px',
                            'paddingLeft': '0',
                            'paddingRight': '0',
                        }),
                        
                        # Sign In Form
                        html.Div(
                            id='auth-signin-form-container',
                            children=_get_signin_form(),
                            style={'display': 'block'}
                        ),

                        # Sign Up Form
                        html.Div(
                            id='auth-signup-form-container',
                            children=_get_signup_form(),
                            style={'display': 'none'}
                        ),
                        
                        # Error/Success Messages
                        html.Div(id='auth-message-container', style={'marginTop': '20px'}),
                        
                    ], style={
                        'padding': '60px 40px',
                        'minHeight': '100vh',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                    }),
                ], xs=12, md=6, style={'padding': '0', 'backgroundColor': PRIMARY_BG}),
            ], style={'margin': '0', 'height': '100vh'}),
            
        ], style={'width': '100%', 'margin': '0', 'padding': '0'})
    ], style={'width': '100%', 'margin': '0', 'padding': '0'})
    

def _get_signin_form():
    """Sign In form component"""
    return html.Div([
        # Username
        html.Div([
            html.Label("Username", style={
                'fontSize': '14px', 'fontWeight': '600', 'color': TEXT, 
                'display': 'block', 'marginBottom': '8px'
            }),
            dcc.Input(
                id='auth-signin-username',
                type='text',
                style={
                    'padding': '2px 8px',
                    'borderRadius': '6px',
                    'border': f'1px solid {BORDER}',
                    'fontSize': '15px',
                    'boxSizing': 'border-box',
                    'width': '100%',
                    'fontFamily': 'inherit',
                    'transition': 'border-color 0.3s ease',
                }
            ),
        ], style={'marginBottom': '20px'}),
        
        # Password
        html.Div([
            html.Label("Password", style={
                'fontSize': '14px', 'fontWeight': '600', 'color': TEXT, 
                'display': 'block', 'marginBottom': '8px'
            }),
            dcc.Input(
                id='auth-signin-password',
                type='password',
                style={
                    'padding': '2px 8px',
                    'borderRadius': '6px',
                    'border': f'1px solid {BORDER}',
                    'fontSize': '15px',
                    'boxSizing': 'border-box',
                    'width': '100%',
                    'fontFamily': 'inherit',
                    'transition': 'border-color 0.3s ease',
                }
            ),
        ], style={'marginBottom': '30px'}),
        
        # Sign In Button
        html.Button(
            "Sign In",
            id='auth-btn-signin',
            n_clicks=0,
            style={
                'width': '100%',
                'backgroundColor': NAVY,
                'borderColor': NAVY,
                'color': '#FFFFFF',
                'fontWeight': '700',
                'fontSize': '15px',
                'padding': '12px 16px',
                'borderRadius': '6px',
                'border': f'2px solid {NAVY}',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease',
            }
        ),
        

    ])


def _get_signup_form():
    return html.Div([

        html.Div([
            html.Label("Full Name"),
            dcc.Input(id='auth-signup-name', type='text', style={'width': '100%'})
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Email"),
            dcc.Input(id='auth-signup-email', type='email', style={'width': '100%'})
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Username"),
            dcc.Input(id='auth-signup-username', type='text', style={'width': '100%'})
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Password"),
            dcc.Input(id='auth-signup-password', type='password', style={'width': '100%'})
        ], style={'marginBottom': '15px'}),

        html.Div([
            html.Label("Confirm Password"),
            dcc.Input(id='auth-signup-password-confirm', type='password', style={'width': '100%'})
        ], style={'marginBottom': '15px'}),

        # ✅ ✅ ROLE DROPDOWN ADDED
        html.Div([
            html.Label("Role"),
            dcc.Dropdown(
                id='auth-signup-role',
                placeholder='Select Role'
            )
        ], style={'marginBottom': '20px'}),

        html.Button(
            "Create Account",
            id='auth-btn-signup',
            style={
                'width': '100%',
                'backgroundColor': NAVY,
                'color': '#FFFFFF'
            }
        )
    ])


# ════════════════════════════════════════════════════════════════
# CALLBACKS TAB SWITCH CALLBACK (SEPARATE)
# ════════════════════════════════════════════════════════════════

@callback(
    [Output('auth-signin-form-container', 'style'),
    Output('auth-signup-form-container', 'style'),
    Output('auth-btn-signin-tab', 'style'),
    Output('auth-btn-signup-tab', 'style')],
    [Input('auth-btn-signin-tab', 'n_clicks'),
    Input('auth-btn-signup-tab', 'n_clicks')],
    prevent_initial_call=False
)

def switch_auth_tabs(signin_clicks, signup_clicks):
    """Switch between Sign In and Sign Up forms"""
    signin_active = not signup_clicks or signin_clicks >= signup_clicks
    
    signin_style = {
        'background': 'none',
        'border': 'none',
        'fontSize': '18px',
        'fontWeight': '700',
        'color': NAVY if signin_active else TEXT_LIGHT,
        'cursor': 'pointer',
        'paddingBottom': '12px',
        'borderBottom': f'3px solid {NAVY}' if signin_active else 'none',
        'transition': 'all 0.3s ease',
    }
    
    signup_style = {
        'background': 'none',
        'border': 'none',
        'fontSize': '18px',
        'fontWeight': '700',
        'color': NAVY if not signin_active else TEXT_LIGHT,
        'cursor': 'pointer',
        'paddingBottom': '12px',
        'transition': 'all 0.3s ease',
    }
    
    return (
        {'display': 'block'} if signin_active else {'display': 'none'},
        {'display': 'block'} if not signin_active else {'display': 'none'},
        signin_style,
        signup_style,
    )
    
    
@callback(    
    Output('auth-signup-role', 'options'),
    Input('auth-signup-role', 'id'),
)
def load_roles(_):
    try:
        session = get_session()
        roles = session.query(Role).all()
        session.close()

        return [{"label": r.role_name, "value": r.role_id} for r in roles]

    except Exception as e:
        print(f"[ERROR] load_roles: {e}")
        return []
