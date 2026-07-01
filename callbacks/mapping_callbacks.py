from dash import callback, Input, Output, State, html
import dash_bootstrap_components as dbc
from core.db_connector import get_session
from core.app_db import User, Company, UserCompany


@callback(
    Output('mapping-user-dropdown', 'options'),
    Input('mapping-user-dropdown', 'id')
)
def load_users(_):
    session = get_session()
    users = session.query(User).all()
    session.close()

    return [{"label": u.username, "value": u.user_id} for u in users]

@callback(
    Output('mapping-company-dropdown', 'options'),
    Input('mapping-company-dropdown', 'id')
)
def load_companies(_):
    session = get_session()
    companies = session.query(Company).all()
    session.close()

    return [{"label": c.company_name, "value": c.company_id} for c in companies]


@callback(
    Output('mapping-msg', 'children'),
    Input('btn-assign-company', 'n_clicks'),
    State('mapping-user-dropdown', 'value'),
    State('mapping-company-dropdown', 'value'),
    prevent_initial_call=True
)
def assign_companies(n_clicks, user_id, company_ids):

    session = get_session()

    try:
        if not user_id or not company_ids:
            return dbc.Alert("Select user and company", color="warning")

        for cid in company_ids:
            existing = session.query(UserCompany).filter_by(
                user_id=user_id,
                company_id=cid
            ).first()

            if not existing:
                mapping = UserCompany(user_id=user_id, company_id=cid)
                session.add(mapping)

        session.commit()

        return dbc.Alert(" Mapping saved", color="success")

    except Exception as e:
        session.rollback()
        return dbc.Alert(f" {str(e)}", color="danger")

    finally:
        session.close()
        
        
        
@callback(
    Output('mapping-table', 'children'),
    Input('btn-assign-company', 'n_clicks')
)

def load_mapping(_):

    session = get_session()

    # ✅ JOIN tables to get names instead of IDs
    data = session.query(UserCompany, User, Company) \
        .join(User, User.user_id == UserCompany.user_id) \
        .join(Company, Company.company_id == UserCompany.company_id) \
        .all()

    rows = []

    for m, u, c in data:
        rows.append(html.Tr([
            html.Td(u.username),          # ✅ show username
            html.Td(c.company_name)       # ✅ show company name
        ]))

    session.close()

    return dbc.Table([
    html.Thead(html.Tr([
        html.Th("User"),
        html.Th("Company")
    ])),
    html.Tbody(rows)
], bordered=True, striped=True, hover=True)

