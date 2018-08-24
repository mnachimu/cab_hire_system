import sqlite3 as db

conn = db.connect('taxico.sqlite')
c = conn.cursor()
try:
    User = 'n.mgnth@gmail.com'
    c.execute("update user set balance = 10 where email like '%@%'")
    c.execute("select balance from user where email = '{}'".format(User))
    balance = c.fetchone()
    conn.commit()
    b=balance[0]
    print (b)
    print('done')
except:
    print('not ')
finally:
    conn.close()



