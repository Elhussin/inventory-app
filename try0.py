import pymssql

cnxn = pymssql.connect(
    server='69.167.190.215',
    port=1433,
    user='CheckerUser',
    password='zeGowPGX5xwcBcj2t'
    
    # بدون database
)
cursor = cnxn.cursor()
cursor.execute("SELECT name FROM sys.databases")
print("Available databases:")
for row in cursor:
    print(row[0])