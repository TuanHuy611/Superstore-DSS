CREATE DATABASE Superstore_DW;
GO

USE Superstore_DW;
GO

USE Superstore_DW;
GO

-- 1. Dimension Customer
CREATE TABLE Dim_Customer (
    CustomerKey INT PRIMARY KEY,
    CustomerID NVARCHAR(20) NOT NULL,
    CustomerName NVARCHAR(100) NOT NULL,
    Segment NVARCHAR(50)
);
GO

-- 2. Dimension Product
CREATE TABLE Dim_Product (
    ProductKey INT PRIMARY KEY,
    ProductID NVARCHAR(30) NOT NULL,
    ProductName NVARCHAR(255) NOT NULL,
    Category NVARCHAR(50),
    SubCategory NVARCHAR(100)
);
GO

-- 3. Dimension Location
CREATE TABLE Dim_Location (
    LocationKey INT PRIMARY KEY,
    Country NVARCHAR(100),
    State NVARCHAR(100),
    City NVARCHAR(100),
    PostalCode NVARCHAR(20),
    Region NVARCHAR(50)
);
GO

-- 4. Dimension Ship Mode
CREATE TABLE Dim_ShipMode (
    ShipModeKey INT PRIMARY KEY,
    ShipMode NVARCHAR(50) NOT NULL
);
GO

-- 5. Dimension Date
CREATE TABLE Dim_Date (
    DateKey INT PRIMARY KEY,
    [Date] DATE NOT NULL,
    [Year] INT,
    [Quarter] INT,
    [Month] INT,
    MonthName NVARCHAR(20),
    [Day] INT,
    DayOfWeek INT,
    DayName NVARCHAR(20),
    IsWeekend BIT
);
GO

-- 6. Fact Sales
CREATE TABLE Fact_Sales (
    SalesKey INT PRIMARY KEY,
    RowID INT NOT NULL,
    OrderID NVARCHAR(30) NOT NULL,

    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    LocationKey INT NOT NULL,
    ShipModeKey INT NOT NULL,

    OrderDateKey INT NOT NULL,
    ShipDateKey INT NOT NULL,

    Sales DECIMAL(18,4) NOT NULL,
    Quantity INT NOT NULL,
    Discount DECIMAL(9,4) NOT NULL,
    Profit DECIMAL(18,4) NOT NULL,
    ShippingDays INT NOT NULL,

    CONSTRAINT FK_Fact_Customer
        FOREIGN KEY (CustomerKey)
        REFERENCES Dim_Customer(CustomerKey),

    CONSTRAINT FK_Fact_Product
        FOREIGN KEY (ProductKey)
        REFERENCES Dim_Product(ProductKey),

    CONSTRAINT FK_Fact_Location
        FOREIGN KEY (LocationKey)
        REFERENCES Dim_Location(LocationKey),

    CONSTRAINT FK_Fact_ShipMode
        FOREIGN KEY (ShipModeKey)
        REFERENCES Dim_ShipMode(ShipModeKey),

    CONSTRAINT FK_Fact_OrderDate
        FOREIGN KEY (OrderDateKey)
        REFERENCES Dim_Date(DateKey),

    CONSTRAINT FK_Fact_ShipDate
        FOREIGN KEY (ShipDateKey)
        REFERENCES Dim_Date(DateKey)
);
GO

USE Superstore_DW;
GO

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

USE Superstore_DW;
GO

SELECT 'Dim_Customer' AS TableName, COUNT(*) AS TotalRows
FROM Dim_Customer

UNION ALL

SELECT 'Dim_Product', COUNT(*)
FROM Dim_Product

UNION ALL

SELECT 'Dim_Location', COUNT(*)
FROM Dim_Location

UNION ALL

SELECT 'Dim_ShipMode', COUNT(*)
FROM Dim_ShipMode

UNION ALL

SELECT 'Dim_Date', COUNT(*)
FROM Dim_Date

UNION ALL

SELECT 'Fact_Sales', COUNT(*)
FROM Fact_Sales;

--Phân tích doanh thu và lợi nhuận theo thời gian
SELECT
    d.[Year],
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit,
    SUM(f.Quantity) AS TotalQuantity
FROM Fact_Sales f
JOIN Dim_Date d
    ON f.OrderDateKey = d.DateKey
GROUP BY d.[Year]
ORDER BY d.[Year];

--Phân tích hiệu quả kinh doanh theo sản phẩm
SELECT
    p.Category,
    p.SubCategory,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit,
    SUM(f.Quantity) AS TotalQuantity
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.ProductKey = p.ProductKey
GROUP BY
    p.Category,
    p.SubCategory
ORDER BY TotalSales DESC;

--Phân tích theo khu vực địa lý
SELECT
    l.Region,
    l.State,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit
FROM Fact_Sales f
JOIN Dim_Location l
    ON f.LocationKey = l.LocationKey
GROUP BY
    l.Region,
    l.State
ORDER BY TotalSales DESC;

--Phân tích khách hàng
SELECT
    c.Segment,
    COUNT(DISTINCT c.CustomerKey) AS TotalCustomers,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit
FROM Fact_Sales f
JOIN Dim_Customer c
    ON f.CustomerKey = c.CustomerKey
GROUP BY c.Segment
ORDER BY TotalSales DESC;

--Phân tích phương thức vận chuyển
SELECT
    s.ShipMode,
    COUNT(*) AS TotalOrdersLines,
    AVG(CAST(f.ShippingDays AS FLOAT)) AS AvgShippingDays,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit
FROM Fact_Sales f
JOIN Dim_ShipMode s
    ON f.ShipModeKey = s.ShipModeKey
GROUP BY s.ShipMode
ORDER BY AvgShippingDays;

--Tổng quan hiệu quả kinh doanh
SELECT
    SUM(Sales) AS TotalSales,
    SUM(Profit) AS TotalProfit,
    SUM(Quantity) AS TotalQuantity,
    COUNT(DISTINCT OrderID) AS TotalOrders,
    CAST(
        SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0)
        AS DECIMAL(10,2)
    ) AS ProfitMargin
FROM Fact_Sales;

--So sánh doanh thu giữa các năm
WITH YearlySales AS (
    SELECT
        d.[Year],
        SUM(f.Sales) AS TotalSales,
        SUM(f.Profit) AS TotalProfit
    FROM Fact_Sales f
    JOIN Dim_Date d
        ON f.OrderDateKey = d.DateKey
    GROUP BY d.[Year]
)

SELECT
    [Year],
    TotalSales,
    TotalProfit,
    LAG(TotalSales) OVER (
        ORDER BY [Year]
    ) AS PreviousYearSales,

    CAST(
        (TotalSales - LAG(TotalSales) OVER (
            ORDER BY [Year]
        )) * 100.0
        / NULLIF(
            LAG(TotalSales) OVER (
                ORDER BY [Year]
            ), 0
        )
        AS DECIMAL(10,2)
    ) AS SalesGrowthRate

FROM YearlySales
ORDER BY [Year];


--Phát hiện nhóm sản phẩm có lợi nhuận âm
SELECT
    p.Category,
    p.SubCategory,
    SUM(f.Sales) AS TotalSales,
    SUM(f.Profit) AS TotalProfit,

    CAST(
        SUM(f.Profit) * 100.0
        / NULLIF(SUM(f.Sales), 0)
        AS DECIMAL(10,2)
    ) AS ProfitMargin,

    CASE
        WHEN SUM(f.Profit) < 0
            THEN N'Negative Profit'
        WHEN SUM(f.Profit) = 0
            THEN N'Break-even'
        ELSE N'Positive Profit'
    END AS BusinessStatus

FROM Fact_Sales f
JOIN Dim_Product p
    ON f.ProductKey = p.ProductKey

GROUP BY
    p.Category,
    p.SubCategory

ORDER BY TotalProfit ASC;