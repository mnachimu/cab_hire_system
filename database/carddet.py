import sqlite3

try:
    conn = sqlite3.connect('taxico.sqlite')
    cursor = conn.cursor()
    print('ok')
except:
    print ('not ok')

#sql_command = "insert into card values (?, ? , ? , ?)" , ("1234123412341234","mugunth","123","12/02")"

try:
    cursor.execute("insert into card values (?, ? , ? , ?)" , ("1234123412341234","mugunth","123","12/02"))
    conn.commit()
    print ('successfully added naye')
    print 'done'
    conn.commit();
except:
    print ('failed')
    print 'not done'
finally:
    conn.close();
