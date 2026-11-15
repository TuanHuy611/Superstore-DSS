
import pyodbc
import pandas as pd

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-I8D3VRTA\\SQLEXPRESS;"
    "DATABASE=Superstore_DW;"
    "Trusted_Connection=yes;"
)

query = """
SELECT
    YEAR(d.Date) AS SalesYear,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit,
    SUM(f.Quantity) AS TotalQuantity
FROM Fact_Sales f
JOIN Dim_Date d
    ON f.OrderDateKey = d.DateKey
GROUP BY YEAR(d.Date)
ORDER BY SalesYear;
"""

df = pd.read_sql(query, conn)

print("Du lieu truy van tu SQL Server:")
print(df)

conn.close()
