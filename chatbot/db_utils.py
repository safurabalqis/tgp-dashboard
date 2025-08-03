import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432)
    )

def fetch_table_as_df(table_name: str):
    conn = get_connection()
    query = f"SELECT * FROM {table_name} LIMIT 50;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

import json

async def get_schema_info(pool, schema_path='schema.json'):
    print("Getting schema")
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except:  # If schema.json doesn't exist
        conn = pool.getconn()
        query = """
        SELECT
            cols.table_schema,
            cols.table_name,
            cols.column_name,
            cols.data_type,
            cols.is_nullable,
            cons.constraint_type,
            cons.constraint_name,
            fk.references_table AS referenced_table,
            fk.references_column AS referenced_column
        FROM information_schema.columns cols
        LEFT JOIN information_schema.key_column_usage kcu
            ON cols.table_schema = kcu.table_schema
            AND cols.table_name = kcu.table_name
            AND cols.column_name = kcu.column_name
        LEFT JOIN information_schema.table_constraints cons
            ON kcu.table_schema = cons.table_schema
            AND kcu.table_name = cons.table_name
            AND kcu.constraint_name = cons.constraint_name
        LEFT JOIN (
            SELECT
                rc.constraint_name,
                kcu.table_name AS references_table,
                kcu.column_name AS references_column
            FROM information_schema.referential_constraints rc
            JOIN information_schema.key_column_usage kcu
                ON rc.unique_constraint_name = kcu.constraint_name
        ) fk
            ON cons.constraint_name = fk.constraint_name
        WHERE cols.table_schema = 'public'
        ORDER BY cols.table_schema, cols.table_name, cols.ordinal_position;
        """
        schema_cur = conn.cursor()
        schema_cur.execute(query)
        columns = [desc[0] for desc in schema_cur.description]
        rows = schema_cur.fetchall()
        schema_cur.close()
        pool.putconn(conn)

        schema_info = [dict(zip(columns, row)) for row in rows]
        with open(schema_path, 'w') as f:
            json.dump(schema_info, f, indent=2)
        return schema_info
