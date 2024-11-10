import pandas as pd
from app.db_connect import get_db

def calculate_total_sales_by_region():
    connection = get_db()
    query = """
        SELECT r.region_name, SUM(sd.monthly_amount) as total_sales
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
        GROUP BY r.region_name
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['region_name', 'total_sales'])
    df['total_sales'] = pd.to_numeric(df['total_sales'])
    return df

def analyze_monthly_sales_trends():
    connection = get_db()
    query = """
        SELECT DATE_FORMAT(sd.date, '%Y-%m') as month, SUM(sd.monthly_amount) as total_sales
        FROM sales_data sd
        GROUP BY month
        ORDER BY month
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['month', 'total_sales'])
    df['total_sales'] = pd.to_numeric(df['total_sales'])
    return df

def identify_top_performing_region():
    connection = get_db()
    query = """
        SELECT r.region_name, SUM(sd.monthly_amount) as total_sales
        FROM sales_data sd
        JOIN regions r ON sd.region_id = r.region_id
        GROUP BY r.region_name
        ORDER BY total_sales DESC
        LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    return result