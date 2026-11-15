
import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-I8D3VRTA\\SQLEXPRESS;"
        "DATABASE=Superstore_DW;"
        "Trusted_Connection=yes;"
    )

    print("Ket noi SQL Server thanh cong!")

    cursor = conn.cursor()

    cursor.execute("SELECT DB_NAME()")

    result = cursor.fetchone()

    print("Database dang ket noi:", result[0])

    conn.close()

except Exception as e:
    print("Ket noi that bai!")
    print("Chi tiet loi:", e)
