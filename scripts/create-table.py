# Budget Bot - Fabric Notebook Script for Creating Delta Table
# Run this in a Microsoft Fabric Notebook connected to your Lakehouse

# ============================================================================
# STEP 1: Import Required Libraries
# ============================================================================

from pyspark.sql.types import StructType, StructField, StringType, DateType, DecimalType, IntegerType
from pyspark.sql.functions import col, to_date, when, lit, month, year, datediff, current_date
from datetime import datetime, timedelta
import pandas as pd

print("Libraries imported successfully")


# ============================================================================
# STEP 2: Define Schema
# ============================================================================

schema = StructType([
    StructField("GL_Number", StringType(), False),
    StructField("Vendor", StringType(), False),
    StructField("Month_Year", DateType(), False),
    StructField("Amount", DecimalType(18, 2), False),
    StructField("Month_Offset", IntegerType(), False),
    StructField("Department", StringType(), True),
    StructField("GL_Description", StringType(), True)
])

print("Schema defined")


# ============================================================================
# STEP 3: Read CSV from Lakehouse Files
# ============================================================================

# Update this path to match your CSV file location
csv_path = "/lakehouse/default/Files/GL_Detail_Budgeting.csv"

df = spark.read.format("csv") \
    .option("header", "true") \
    .schema(schema) \
    .load(csv_path)

print(f"CSV loaded with {df.count()} rows")


# ============================================================================
# STEP 4: Rename Columns to Match SQL Naming Convention
# ============================================================================

df = df.withColumnRenamed("GL_Number", "GL Number") \
       .withColumnRenamed("Month_Year", "Month & Year") \
       .withColumnRenamed("Month_Offset", "Month Offset") \
       .withColumnRenamed("GL_Description", "GL Description")

print("Columns renamed")


# ============================================================================
# STEP 5: Write to Delta Table
# ============================================================================

table_name = "GL_Detail_Budgeting"

df.write.mode("overwrite").format("delta").saveAsTable(table_name)

print(f"Delta table '{table_name}' created successfully")


# ============================================================================
# STEP 6: Verify Table Creation
# ============================================================================

# Check row count
row_count = spark.sql(f"SELECT COUNT(*) as count FROM {table_name}").collect()[0]['count']
print(f"Table contains {row_count} rows")

# Show sample data
print("\nSample data:")
display(spark.sql(f"SELECT * FROM {table_name} LIMIT 10"))

# Show data summary
print("\nData Summary:")
summary = spark.sql(f"""
    SELECT
        COUNT(DISTINCT [GL Number]) as UniqueGLNumbers,
        COUNT(DISTINCT Vendor) as UniqueVendors,
        COUNT(DISTINCT Department) as UniqueDepartments,
        MIN([Month & Year]) as EarliestDate,
        MAX([Month & Year]) as LatestDate,
        SUM(Amount) as TotalAmount
    FROM {table_name}
""")
display(summary)


# ============================================================================
# STEP 7: Create Indexes for Performance (Optional - Run in SQL Endpoint)
# ============================================================================

# Note: Indexes are created in the SQL Endpoint, not in notebooks
# Run these commands in the SQL Endpoint for better query performance:

index_commands = """
-- Run these in the SQL Analytics Endpoint:

-- Index on GL Number (most frequently filtered column)
CREATE INDEX IX_GL_Number ON GL_Detail_Budgeting([GL Number]);

-- Index on Vendor
CREATE INDEX IX_Vendor ON GL_Detail_Budgeting([Vendor]);

-- Index on Month Offset (used in all queries)
CREATE INDEX IX_Month_Offset ON GL_Detail_Budgeting([Month Offset]);

-- Composite index for common query pattern
CREATE INDEX IX_GL_Vendor_Month ON GL_Detail_Budgeting([GL Number], [Vendor], [Month Offset]);
"""

print("\nIndex Commands (run in SQL Endpoint):")
print(index_commands)


# ============================================================================
# ALTERNATIVE: Load from Excel (if you have Excel instead of CSV)
# ============================================================================

def load_from_excel(excel_path):
    """
    Alternative method to load data from Excel file.
    Uncomment and use if your source is Excel instead of CSV.
    """
    # Read Excel file using pandas
    pdf = pd.read_excel(excel_path)

    # Ensure column names match expected schema
    expected_columns = ['GL Number', 'Vendor', 'Month & Year', 'Amount', 'Month Offset', 'Department', 'GL Description']

    # Rename columns if needed
    if list(pdf.columns) != expected_columns:
        print(f"Warning: Column names don't match expected. Current: {list(pdf.columns)}")
        # Add your column mapping here if needed

    # Convert to Spark DataFrame
    sdf = spark.createDataFrame(pdf)

    # Write to Delta table
    sdf.write.mode("overwrite").format("delta").saveAsTable("GL_Detail_Budgeting")

    return sdf.count()

# Uncomment to use Excel loading:
# excel_path = "/lakehouse/default/Files/data_snapshot.xlsx"
# row_count = load_from_excel(excel_path)
# print(f"Loaded {row_count} rows from Excel")


# ============================================================================
# STEP 8: Data Quality Checks
# ============================================================================

print("\n" + "="*60)
print("DATA QUALITY CHECKS")
print("="*60)

# Check for null values
null_check = spark.sql(f"""
    SELECT
        SUM(CASE WHEN [GL Number] IS NULL THEN 1 ELSE 0 END) as Null_GL_Numbers,
        SUM(CASE WHEN Vendor IS NULL THEN 1 ELSE 0 END) as Null_Vendors,
        SUM(CASE WHEN [Month & Year] IS NULL THEN 1 ELSE 0 END) as Null_Dates,
        SUM(CASE WHEN Amount IS NULL THEN 1 ELSE 0 END) as Null_Amounts
    FROM {table_name}
""")
print("\nNull Value Check:")
display(null_check)

# Check GL Number format
gl_format_check = spark.sql(f"""
    SELECT [GL Number], COUNT(*) as count
    FROM {table_name}
    WHERE [GL Number] NOT LIKE '%.%.%'
    GROUP BY [GL Number]
""")
invalid_gl = gl_format_check.count()
if invalid_gl > 0:
    print(f"\nWarning: {invalid_gl} GL Numbers don't match expected format (XX.XXX.XXX)")
    display(gl_format_check)
else:
    print("\nAll GL Numbers match expected format")

# Check Month Offset range
offset_check = spark.sql(f"""
    SELECT
        MIN([Month Offset]) as Min_Offset,
        MAX([Month Offset]) as Max_Offset
    FROM {table_name}
""")
print("\nMonth Offset Range:")
display(offset_check)

# Check Department distribution
dept_dist = spark.sql(f"""
    SELECT
        Department,
        COUNT(*) as TransactionCount,
        COUNT(DISTINCT [GL Number]) as GLNumbers,
        COUNT(DISTINCT Vendor) as Vendors
    FROM {table_name}
    GROUP BY Department
    ORDER BY TransactionCount DESC
""")
print("\nDepartment Distribution:")
display(dept_dist)

print("\n" + "="*60)
print("TABLE CREATION COMPLETE!")
print("="*60)
print(f"""
Next Steps:
1. Create a Data Agent in your Fabric workspace
2. Add this Lakehouse as a data source
3. Select the '{table_name}' table
4. Copy the agent instructions from the /instructions folder
5. Add example queries from /queries folder
6. Test with: "Hi Budget Bot, I need help creating a budget"
""")
