from dash import html, dcc
import dash_bootstrap_components as dbc

def generate_mapping_page():

    return html.Div([

        html.H2("User Company Mapping", style={'marginBottom': '20px'}),

        dbc.Card([
            dbc.CardBody([

                html.Label("Select User"),
                dcc.Dropdown(id='mapping-user-dropdown'),

                html.Br(),

                html.Label("Select Companies"),
                dcc.Dropdown(id='mapping-company-dropdown', multi=True),

                html.Br(),

                dbc.Button("Assign Companies", id='btn-assign-company', color='primary'),

                html.Div(id='mapping-msg', style={'marginTop': '10px'})

            ])
        ], className="mb-4"),

        dbc.Card([
            dbc.CardBody([
                html.H5("Mappings"),
                html.Div(id='mapping-table')
            ])
        ])

    ], style={'padding': '20px'})