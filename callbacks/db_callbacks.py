from dash import Input, Output, State
from dash import callback
import dash
from flask import app, views
from core.db_session import _current_db
from core import db_connector
from sqlalchemy import text
from sqlalchemy import inspect
import dash_bootstrap_components as dbc


@callback(
    Output('db-connection-status', 'children'),
    Output('db-table-section', 'style'),
    Output('db-table-dropdown', 'options'),
    Input('btn-test-db', 'n_clicks'),
    State('db-type-dropdown', 'value'),
    State('db-host', 'value'),
    State('db-port', 'value'),
    State('db-name', 'value'),
    State('db-username', 'value'),
    State('db-password', 'value'),
    prevent_initial_call=True
)
def test_db_connection(n_clicks, db_type, host, port, db_name, username, password):

    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    try:
        engine = db_connector.connect(
            db_type,
            host,
            port,
            db_name,
            username,
            password
        )
        _current_db["engine"] = engine
        _current_db["db_type"] = db_type

        if engine is None:
            return dbc.Alert("Unsupported DB type", color="danger"), {'display': 'none'}

        # ✅ safer connection test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        views = inspector.get_view_names()
        options = [{"label": name, "value" : name} for name in tables + views]
        
        return (" Connection successful",{'display': 'block'}, options)  # show table section
    except Exception as e:
        return (
            dbc.Alert(f"❌ Connection failed: {str(e)[:150]}", color="danger"),
            {'display': 'none'},
            []
        )

@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('btn-fetch-db', 'n_clicks'),
    prevent_initial_call=True
)
def go_to_data_review(n_clicks):
    
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    return "/data-review"




# from dash import Input, Output, State, callback
# import dash
# from core import db_connector
# from sqlalchemy import text


# @callback(
#     Output('db-connection-status', 'children'),  # ✅ FIXED TARGET
#     Output('db-table-section', 'style'),  # ✅ ADD THIS
#     Input('btn-test-db', 'n_clicks'),
#     State('db-type-dropdown', 'value'),
#     State('db-host', 'value'),
#     State('db-port', 'value'),
#     State('db-name', 'value'),
#     State('db-username', 'value'),
#     State('db-password', 'value'),
#     prevent_initial_call=True
# )
# def test_db_connection(n_clicks, db_type, host, port, db_name, username, password):

#     if not n_clicks:
#         raise dash.exceptions.PreventUpdate

#     try:
#         #  connect
#         engine = db_connector.connect(
#             db_type,
#             host,
#             port,
#             db_name,     # ✅ correct
#             username,    # ✅ correct
#             password
#         )

#         #  test
#         conn = engine.connect()
#         conn.execute(text("SELECT 1"))
#         conn.close()

#         return " Connection successful", {'display': 'block'}

#     except Exception as e:
#         return f" Connection failed: {str(e)[:100]}", {'display': 'none'}
