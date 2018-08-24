import sqlite3

try:
    conn = sqlite3.connect('taxico.sqlite')
    cursor = conn.cursor()
    print('ok')
except:
    print ('not ok')

sql_command = ("create table if not exists card (number text primary key, name text ,cvv integer not null , expiry text ) ")

try:
    cursor.execute(sql_command)
    conn.commit()
    print ('successfully added naye')
    print 'done'
    conn.commit();
except:
    print ('failed')
    print 'not done'
finally:
    conn.close();
