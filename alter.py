import sqlite3

try:
    connection = sqlite3.connect('database/taxico.sqlite')
    cursor = connection.cursor()
    print('ok')
except:
    print ('not ok')

sql_command = ("ALTER TABLE user add column balance INTEGER")

try:
    cursor.execute(sql_command)
    connection.commit()
    print ('successfully added naye')
    print 'done'
except:
    print ('failed')
    print 'not done'
finally:
    connection.close()

