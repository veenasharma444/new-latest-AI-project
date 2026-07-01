from dash import Input, Output, State, callback, html
from core.db_connector import get_session
from core.app_db import Company
import dash_bootstrap_components as dbc


@callback(
    Output('company-msg', 'children'),
    Input('btn-create-company', 'n_clicks'),
    State('company-name', 'value'),
    State('company-code', 'value'),
    State('company-status', 'value'),
    prevent_initial_call=True
)
def create_company(n_clicks, name, code, status):

    session = get_session()

    try:
        if not name or not code:
            return dbc.Alert("All fields required", color="warning")

        company = Company(
            company_name=name,
            company_code=code,
            is_active=status
        )

        session.add(company)
        session.commit()

        return dbc.Alert(" Company created", color="success")

    except Exception as e:
        session.rollback()
        return dbc.Alert(f" {str(e)}", color="danger")

    finally:
        session.close()
        

        
@callback(
    Output('company-table', 'children'),
    Input('company-table', 'id')
)
def load_companies(_):

    session = get_session()
    companies = session.query(Company).all()

    rows = []

    for c in companies:
        rows.append(html.Tr([
            html.Td(c.company_name),
            html.Td(c.company_code),
            html.Td("Active" if c.is_active else "Inactive")
        ]))

    session.close()

    return html.Table([
        html.Thead(html.Tr([
            html.Th("Name"),
            html.Th("Code"),
            html.Th("Status")
        ])),
        html.Tbody(rows)
    ])