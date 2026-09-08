from sqlalchemy import text

from app.database.connection import engine


columns = [
    ("industry", "VARCHAR"),
    ("employee_count", "INTEGER"),
    ("location", "VARCHAR"),
    ("founded_year", "INTEGER"),
    ("technologies", "TEXT"),
    ("revenue_range", "VARCHAR"),
]


with engine.begin() as connection:
    for column, data_type in columns:
        connection.execute(
            text(
                f"ALTER TABLE leads "
                f"ADD COLUMN IF NOT EXISTS {column} {data_type}"
            )
        )