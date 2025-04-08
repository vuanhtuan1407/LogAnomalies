import psycopg2

def get_connection():
    return psycopg2.connect(
        host="postgres",
        database="anomaly_logs",
        user="postgres",
        password="postgres"
    )

def insert_anomaly(record):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO anomalies (date, time, pid, level, component, event_id, event_template, template_params)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, record)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("[Postgres ERROR]", e)
