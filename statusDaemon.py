import subprocess
import psycopg2
from time import sleep

def connect():
    db_config = {
        'dbname': 'polarDB',
        'user': 'threadripper',
        'password': 'Epididymis0!',
        'host': '10.21.4.63',
        'port': '5432',
    }
    return psycopg2.connect(**db_config)


while True:

    completed_process = subprocess.run(['celery', '-A', 'tasks', 'status'], text=True, capture_output=True)
    status = completed_process.stdout.replace('->', '').replace('celery@', '').replace(' ', '').split('\n')
    statusList = {}
    for node in status:
        if ':' in node:
            statusList[node.split(':')[0]] = node.split(':')[1]
    
    conn = connect()
    cursor = conn.cursor()

    for name, status in statusList.items():
    
        # Update or insert row 
        cursor.execute("""
        INSERT INTO status (name, status) 
        VALUES (%s, %s) 
        ON CONFLICT (name) DO UPDATE 
        SET status = EXCLUDED.status
        """, (name, status))

    # Set offline for any names not in statusList
    if statusList:
        cursor.execute("""
            UPDATE status 
            SET status = 'offline' 
            WHERE name NOT IN %s
        """, (tuple(statusList.keys()),))
    
    if not statusList:
        cursor.execute("""
            UPDATE status 
            SET status = 'OFFLINE'
        """)

    conn.commit()
    conn.close()
    sleep(10)

