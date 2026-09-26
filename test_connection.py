from ingestion.database import get_engine
from sqlalchemy import text


try:

    engine = get_engine()

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT NOW();")
        )

        current_time = result.fetchone()[0]

        print(
            "Successfully connected to Supabase!"
        )

        print(
            "Database time:",
            current_time
        )


except Exception as e:

    print(
        "Supabase connection failed:"
    )

    print(e)