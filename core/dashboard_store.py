"""
Save and load dashboard configurations using DATABASE (ORM)
"""

from core.app_db import SavedDashboard
from core.db_connector import get_session
from datetime import datetime


# ✅ SAVE to database
def save(name: str, user_id: int, upload_id: int,
         kpi_selections: list, filter_selections: list,
         confirmed_dtypes: dict, ai_suggestions: dict = None):

    session = get_session()

    try:
        print("CREATING DASHBOARD OBJECT")
        dashboard = SavedDashboard(
            user_id=user_id,
            upload_id=upload_id,
            dashboard_name=name,
            kpi_selections=kpi_selections or [],
            filter_selections=filter_selections or [],
            confirmed_dtypes=confirmed_dtypes or {},
            ai_suggestions=ai_suggestions or {},
            created_at=datetime.utcnow()
        )
        print("ADDING TO SESSION")
        session.add(dashboard)
        print("COMMITING")
        session.commit()
        print("COMMIT SUCCESS")
        print(f"[OK] Dashboard saved: {name}")

        return {
            "success": True,
            "dashboard_id": dashboard.dashboard_id
        }

    except Exception as e:
        
        print("EXCEPTION TYPE =", type(e))
        print("EXCEPTION =", str(e))
        session.rollback()
        print(f"[ERROR] save dashboard: {e}")
        return {"success": False, "message": "Failed to save dashboard"}

    finally:
        session.close()


# ✅ LIST dashboards
def list_saved(user_id: int):
    session = get_session()

    try:
        dashboards = (
            session.query(SavedDashboard)
            .filter_by(user_id=user_id)
            .order_by(SavedDashboard.created_at.desc())
            .all()
        )

        return [
            {
                "dashboard_id": d.dashboard_id,
                "name": d.dashboard_name,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in dashboards
        ]

    except Exception as e:
        print(f"[ERROR] list dashboards: {e}")
        return []

    finally:
        session.close()


# ✅ LOAD dashboard
def load(dashboard_id: int, user_id: int):
    session = get_session()

    try:
        dashboard = session.query(SavedDashboard).filter_by(
            dashboard_id=dashboard_id,
            user_id=user_id
        ).first()

        if not dashboard:
            return None

        return {
            "name": dashboard.dashboard_name,
            "kpi_selections": dashboard.kpi_selections,
            "filter_selections": dashboard.filter_selections,
            "confirmed_dtypes": dashboard.confirmed_dtypes,
            "ai_suggestions": dashboard.ai_suggestions,
        }

    except Exception as e:
        print(f"[ERROR] load dashboard: {e}")
        return None

    finally:
        session.close()


# ✅ DELETE dashboard
def delete(dashboard_id: int, user_id: int):
    session = get_session()

    try:
        dashboard = session.query(SavedDashboard).filter_by(
            dashboard_id=dashboard_id,
            user_id=user_id
        ).first()

        if not dashboard:
            return False

        session.delete(dashboard)
        session.commit()

        print(f"[OK] Dashboard deleted: {dashboard_id}")

        return True

    except Exception as e:
        session.rollback()
        print(f"[ERROR] delete dashboard: {e}")
        return False

    finally:
        session.close()