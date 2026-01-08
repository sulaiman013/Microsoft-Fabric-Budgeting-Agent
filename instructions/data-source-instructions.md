# Budget Bot - Data Source Instructions

Copy this content into your Lakehouse data source instructions in the Data Agent configuration.

---

## General Knowledge

The `GL_Detail_Budgeting` table contains historical General Ledger transaction data for budget planning. Each row represents a transaction or monthly aggregate for a specific vendor and GL account.

## Schema Details

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `GL Number` | VARCHAR(50) | General Ledger account number | "35.600.500" |
| `Vendor` | VARCHAR(255) | Vendor/supplier name | "FEDEX" |
| `Month & Year` | DATE | Transaction month (first day) | 2024-10-01 |
| `Amount` | DECIMAL(18,2) | Transaction amount | -224.89 |
| `Month Offset` | INT | Relative month from current | -4 |
| `Department` | VARCHAR(100) | Department name | "Sales & Marketing" |
| `GL Description` | VARCHAR(500) | Account description | "Postage & Frt Out" |

## Key Data Patterns

### Month Offset Values
- `-1` = Last completed month
- `-2` = Two months ago
- `-12` = One year ago
- Range for 12-month queries: `BETWEEN -12 AND -1`

### Amount Values
- **Negative amounts** = Expenses (most common for budget GL accounts)
- **Positive amounts** = Revenue or credits
- Always use `SUM(Amount)` for aggregations

### Missing Data
- If a vendor has no transactions in a month, there is NO row for that vendor-month combination
- When displaying, show $0 for missing months

## Important Query Patterns

### Pattern 1: Get Last 12 Months by GL Number and Vendor (Primary Query)

Use this when showing historical data for a GL account:

```sql
SELECT
    Vendor,
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    Amount,
    [Month & Year] AS MonthDate
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY Vendor, [Month & Year] DESC
```

### Pattern 2: Get Available GL Numbers for a Department

Use when user selects a department:

```sql
-- For Sales & Marketing:
SELECT DISTINCT [GL Number], [GL Description]
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '35.600.%'
   OR [GL Number] LIKE '32.600.%'
   OR [GL Number] LIKE '36.600.%'
ORDER BY [GL Number]

-- For Finance:
SELECT DISTINCT [GL Number], [GL Description]
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '10.500.%'
   OR [GL Number] LIKE '11.500.%'
ORDER BY [GL Number]

-- For HR:
SELECT DISTINCT [GL Number], [GL Description]
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '30.500.%'
ORDER BY [GL Number]

-- For Operations:
SELECT DISTINCT [GL Number], [GL Description]
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '17.500.%'
   OR [GL Number] LIKE '18.500.%'
ORDER BY [GL Number]

-- For Shipping:
SELECT DISTINCT [GL Number], [GL Description]
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '33.700.%'
ORDER BY [GL Number]
```

### Pattern 3: Get Single Vendor Historical Data

Use when user selects a specific vendor:

```sql
SELECT
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    Amount,
    [Month Offset]
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND Vendor = '<USER_VENDOR>'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY [Month & Year] DESC
```

### Pattern 4: Get All Vendors Summary for GL Number

Use to show vendor breakdown:

```sql
SELECT
    Vendor,
    COUNT(*) AS NumberOfMonths,
    SUM(Amount) AS TotalSpent,
    AVG(Amount) AS AvgMonthlySpend
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY Vendor
ORDER BY TotalSpent DESC
```

### Pattern 5: Get Monthly Totals for GL Number

Use for month-over-month analysis:

```sql
SELECT
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    SUM(Amount) AS TotalAmount,
    COUNT(DISTINCT Vendor) AS NumberOfVendors
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND [Month Offset] BETWEEN -12 AND -1
GROUP BY [Month & Year], FORMAT([Month & Year], 'MMM yyyy')
ORDER BY [Month & Year] DESC
```

## Department Prefix Reference

| Department | GL Prefixes |
|------------|-------------|
| Finance | 10.XXX.XXX, 11.XXX.XXX |
| HR | 30.XXX.XXX |
| Sales & Marketing | 32.XXX.XXX, 35.XXX.XXX, 36.XXX.XXX |
| Operations | 17.XXX.XXX, 18.XXX.XXX |
| Shipping | 33.XXX.XXX |

## Query Optimization Tips

1. **Always filter on indexed columns first**: `[GL Number]`, `Vendor`, `[Month Offset]`
2. **Use specific date ranges**: `[Month Offset] BETWEEN -12 AND -1`
3. **Aggregate before pivoting**: Use `SUM(Amount)` grouped by Vendor and Month
4. **Avoid SELECT ***: Specify only needed columns

## Common Issues & Solutions

### Issue: Pivot query doesn't work directly
**Solution**: Retrieve data in long format (Vendor, Month, Amount) and present it formatted as a markdown table.

### Issue: No data returned for GL Number
**Solution**:
1. Verify GL Number format includes dots (35.600.500 not 35600500)
2. Check if data exists with: `SELECT COUNT(*) FROM GL_Detail_Budgeting WHERE [GL Number] = '35.600.500'`

### Issue: Amounts look incorrect
**Solution**:
1. Verify Month Offset range is correct
2. Check sign of Amount (negative = expense)
3. Ensure aggregation uses SUM not raw values

### Issue: Missing vendors in output
**Solution**: Some vendors may have no transactions in certain months. This is normal - display $0 for missing combinations.

## Hybrid Baseline Logic

For budget planning, we need a complete 12-month view. Since we may not have completed the current year:

**Logic:**
- Use current year actuals for months that have completed
- Use prior year data for months not yet completed

**Example (if current month is October 2025):**
- Jan 2025 - Sep 2025: Current year actuals (Month Offset -1 to -9)
- Oct 2024 - Dec 2024: Prior year data (Month Offset -10 to -12)

**SQL for Hybrid Baseline:**
```sql
-- Get data, system will sort by actual dates
SELECT
    Vendor,
    FORMAT([Month & Year], 'MMM yyyy') AS MonthLabel,
    [Month & Year] AS MonthDate,
    Amount
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY Vendor, [Month & Year]
```

Note: The agent should present months in chronological order, noting which are current year vs. prior year data.
