from database import get_db_connection
from datetime import date

def main():
    conn = get_db_connection()
    cur = conn.cursor()
    today = date.today().isoformat()
    print('Today:', today)

    cur.execute('SELECT COUNT(*) FROM employees')
    result = cur.fetchone()
    print('Total employees:', result[0] if result else 0)

    cur.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE date = %s AND status = 'On Time'", (today,))
    result = cur.fetchone()
    print('Present today:', result[0] if result else 0)

    cur.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE date = %s AND status = 'Late'", (today,))
    result = cur.fetchone()
    print('Late today:', result[0] if result else 0)

    cur.execute("SELECT COUNT(DISTINCT employee_id) FROM attendance WHERE date = %s AND status = 'Holiday'", (today,))
    result = cur.fetchone()
    print('On leave:', result[0] if result else 0)

    cur.execute("SELECT e.name, a.time, a.status FROM attendance a JOIN employees e ON a.employee_id = e.id WHERE a.date = %s ORDER BY a.time DESC LIMIT 5", (today,))
    print('Recent entries:', cur.fetchall())

    conn.close()

if __name__ == '__main__':
    main() 