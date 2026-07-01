from dash import html, dcc
import dash_bootstrap_components as dbc


def generate_companies_page():

    return html.Div([

        html.H2("Company Master", style={'marginBottom': '20px'}),

        # ✅ FORM
        dbc.Card([
            dbc.CardBody([

                html.H5("Create Company"),

                dbc.Row([
                    dbc.Col([
                        html.Label("Company Name"),
                        dcc.Input(id='company-name', className='form-control')
                    ], width=4),

                    dbc.Col([
                        html.Label("Company Code"),
                        dcc.Input(id='company-code', className='form-control')
                    ], width=4),

                    dbc.Col([
                        html.Label("Status"),
                        dcc.Dropdown(
                            id='company-status',
                            options=[
                                {"label": "Active", "value": True},
                                {"label": "Inactive", "value": False},
                            ],
                            value=True
                        )
                    ], width=4),
                ], className="mb-3"),

                dbc.Button("Create Company", id='btn-create-company', color='primary'),

                html.Div(id='company-msg', style={'marginTop': '10px'})

            ])
        ], className="mb-4"),

        # ✅ TABLE
        dbc.Card([
            dbc.CardBody([
                html.H5("Company List"),
                html.Div(id='company-table')
            ])
        ])

    ], style={'padding': '20px'})
