
    
# from sqlalchemy import create_engine
# import pandas as pd
# from dotenv import load_dotenv
# import os
# load_dotenv()

# server = os.getenv('SERVER')
# database = os.getenv('DATABASE')
# username = os.getenv('DBUSERNAME')
# password = os.getenv('PASSWORD')
# server_host = server.split(',')[0] if ',' in server else server
# server_port = 1433

# def fetch_from_sqlserver():
#     try:
#         # إنشاء connection string
#         connection_string = f"mssql+pymssql://{username}:{password}@{server_host}:{server_port}/{database}?charset=utf8"
#         print (connection_string)
#         engine = create_engine(connection_string)
#         print (engine)
#         query = """
#             SELECT 
#                 dbo.v_ItemCardtaha.Code, 
#                 dbo.v_ItemCardtaha.Description AS name, 
#                 SUM(dbo.v_ItemCardtaha.Incoming - dbo.v_ItemCardtaha.Outgoing) AS required_qty, 
#                 dbo.Product.CostPrice AS cost, 
#                 dbo.Product.RetailPrice AS retail
#             FROM dbo.v_ItemCardtaha 
#             INNER JOIN dbo.Product ON dbo.v_ItemCardtaha.Code = dbo.Product.Code
#             WHERE (dbo.v_ItemCardtaha.DepName = N'Jeddah Store') 
#               AND (dbo.v_ItemCardtaha.MainGroupID = 38 OR dbo.v_ItemCardtaha.MainGroupID = 58)
#             GROUP BY dbo.v_ItemCardtaha.Description, dbo.v_ItemCardtaha.Code, dbo.Product.RetailPrice, dbo.Product.CostPrice
#             HAVING (SUM(dbo.v_ItemCardtaha.Incoming - dbo.v_ItemCardtaha.Outgoing) <> 0)
#         """
        
#         df = pd.read_sql(query, engine)
#         rows = df.values.tolist()
#         print(f"Connected to SQL Server - Fetched {len(rows)} rows")
#         print(rows)
#         return rows
        
#     except Exception as e:
#         print(e)
#         # messagebox.showerror("SQL Error", f"❌ Error fetching data: {e}")
#         return []
# fetch_from_sqlserver()


import pyodbc
from dotenv import load_dotenv
import os

# تحميل المتغيرات من ملف .env تلقائيًا
load_dotenv()  

server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('DBUSERNAME')
password = os.getenv('PASSWORD')

# إعداد الاتصال
connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'Encrypt=no;'  # غيّرها إلى yes لو السيرفر يتطلب اتصال مشفر
        'TrustServerCertificate=yes;'
)

try:
    cnxn = pyodbc.connect(connection_string)
    cursor = cnxn.cursor()
    cursor.execute("SELECT top 10 * FROM Product")
    rows = cursor.fetchall()
    print(rows)
except Exception as e:
    print(e)