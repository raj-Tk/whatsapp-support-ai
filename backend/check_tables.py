from sqlalchemy import text

from app.database import engine


with engine.connect() as conn:
    rows = conn.execute(
        text(
            "SELECT table_name "
            "FROM information_schema.tables "
            "WHERE table_schema = 'public' "
            "ORDER BY table_name"
        )
    )

    print([row[0] for row in rows])