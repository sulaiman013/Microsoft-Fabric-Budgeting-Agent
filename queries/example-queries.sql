-- Budget Bot - Example Queries for Few-Shot Learning
-- Add these as example queries in your Data Agent configuration
-- Each example helps the AI understand how to generate SQL from natural language

--------------------------------------------------------------------------------
-- EXAMPLE 1: Historical Spending by GL Number and Vendor
--------------------------------------------------------------------------------
-- Question: Show me the historical spending for GL Number 35.600.500 by vendor for the last 12 months

SELECT
    Vendor,
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    Amount,
    [Month & Year] AS MonthDate
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY Vendor, [Month & Year] DESC;


--------------------------------------------------------------------------------
-- EXAMPLE 2: Available GL Accounts for Department
--------------------------------------------------------------------------------
-- Question: What GL accounts are available for Sales & Marketing?

SELECT DISTINCT
    [GL Number],
    [GL Description],
    COUNT(*) AS TransactionCount,
    SUM(Amount) AS TotalAmount
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '35.600.%'
    OR [GL Number] LIKE '32.600.%'
    OR [GL Number] LIKE '36.600.%'
GROUP BY [GL Number], [GL Description]
ORDER BY [GL Number];


--------------------------------------------------------------------------------
-- EXAMPLE 3: Single Vendor Historical Data
--------------------------------------------------------------------------------
-- Question: Show me FEDEX spending for GL 35.600.500 for the last 12 months

SELECT
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    Amount,
    [Month Offset]
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND Vendor = 'FEDEX'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY [Month & Year] DESC;


--------------------------------------------------------------------------------
-- EXAMPLE 4: All Vendors Summary for GL Number
--------------------------------------------------------------------------------
-- Question: List all vendors who had transactions in GL 35.600.500 in the last year

SELECT
    Vendor,
    COUNT(*) AS NumberOfMonths,
    SUM(Amount) AS TotalSpent,
    AVG(Amount) AS AvgMonthlySpend,
    MIN(Amount) AS MinMonth,
    MAX(Amount) AS MaxMonth
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY Vendor
ORDER BY TotalSpent DESC;


--------------------------------------------------------------------------------
-- EXAMPLE 5: Monthly Totals for GL Number
--------------------------------------------------------------------------------
-- Question: What was the total spending in GL 35.600.500 by month?

SELECT
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    [Month & Year] AS MonthDate,
    SUM(Amount) AS TotalAmount,
    COUNT(DISTINCT Vendor) AS NumberOfVendors
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY [Month & Year], FORMAT([Month & Year], 'MMM yyyy')
ORDER BY [Month & Year] DESC;


--------------------------------------------------------------------------------
-- EXAMPLE 6: Department GL Numbers with Totals
--------------------------------------------------------------------------------
-- Question: Show me all Finance department GL accounts and their totals

SELECT
    [GL Number],
    [GL Description],
    Department,
    COUNT(DISTINCT Vendor) AS UniqueVendors,
    COUNT(*) AS TransactionCount,
    SUM(Amount) AS TotalAmount
FROM GL_Detail_Budgeting
WHERE Department = 'Finance'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY [GL Number], [GL Description], Department
ORDER BY TotalAmount;


--------------------------------------------------------------------------------
-- EXAMPLE 7: Top Vendors Across All GL Accounts
--------------------------------------------------------------------------------
-- Question: Who are the top 10 vendors by spending in Sales & Marketing?

SELECT TOP 10
    Vendor,
    COUNT(DISTINCT [GL Number]) AS GLAccountsUsed,
    SUM(Amount) AS TotalSpent
FROM GL_Detail_Budgeting
WHERE Department = 'Sales & Marketing'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY Vendor
ORDER BY TotalSpent;


--------------------------------------------------------------------------------
-- EXAMPLE 8: Year-over-Year Comparison (if data exists)
--------------------------------------------------------------------------------
-- Question: Compare this year's spending to last year for FEDEX in GL 35.600.500

SELECT
    YEAR([Month & Year]) AS Year,
    MONTH([Month & Year]) AS MonthNum,
    FORMAT([Month & Year], 'MMM') AS MonthName,
    SUM(Amount) AS TotalAmount
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND Vendor = 'FEDEX'
    AND [Month Offset] BETWEEN -24 AND -1
GROUP BY YEAR([Month & Year]), MONTH([Month & Year]), FORMAT([Month & Year], 'MMM')
ORDER BY Year DESC, MonthNum;


--------------------------------------------------------------------------------
-- EXAMPLE 9: Vendors with No Recent Activity
--------------------------------------------------------------------------------
-- Question: Which vendors haven't had transactions in the last 3 months for GL 35.600.500?

SELECT DISTINCT Vendor
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND [Month Offset] BETWEEN -12 AND -4
    AND Vendor NOT IN (
        SELECT DISTINCT Vendor
        FROM GL_Detail_Budgeting
        WHERE [GL Number] = '35.600.500'
            AND [Month Offset] BETWEEN -3 AND -1
    );


--------------------------------------------------------------------------------
-- EXAMPLE 10: Data Validation Query
--------------------------------------------------------------------------------
-- Question: Show me a summary of all data in the table

SELECT
    COUNT(*) AS TotalRows,
    COUNT(DISTINCT [GL Number]) AS UniqueGLNumbers,
    COUNT(DISTINCT Vendor) AS UniqueVendors,
    COUNT(DISTINCT Department) AS UniqueDepartments,
    MIN([Month & Year]) AS EarliestDate,
    MAX([Month & Year]) AS LatestDate,
    SUM(Amount) AS TotalAmount
FROM GL_Detail_Budgeting
WHERE [Month Offset] BETWEEN -12 AND -1;
