# Microsoft Fabric Budgeting Agent

A conversational AI assistant built on Microsoft Fabric Data Agent that enables managers to create annual budgets through natural language interactions. The Budget Bot analyzes historical expenses, generates budget projections using various forecasting methods, and exports approved budgets to SharePoint.

![Demo](assets/demo.gif)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [How It Works](#how-it-works)
- [Data Model](#data-model)
- [Budget Calculation Methods](#budget-calculation-methods)
- [Setup Guide](#setup-guide)
- [Agent Instructions](#agent-instructions)
- [Example Conversation](#example-conversation)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

The **Budget Bot** transforms the traditional spreadsheet-based budgeting process into an interactive, conversational experience. Instead of manually navigating complex Excel files, budget managers can simply chat with the AI to:

- View historical spending by GL account and vendor
- Apply budget calculations (percentage increases, fixed amounts, custom allocations)
- Document reasoning for each budget decision
- Export finalized budgets to SharePoint

This solution was built for a manufacturing company to streamline their annual budgeting cycle, reducing the time to complete budgets by 50% while improving accuracy and auditability.

---

## Features

| Feature | Description |
|---------|-------------|
| **Natural Language Queries** | Ask questions in plain English - no SQL knowledge required |
| **Hybrid 12-Month Baseline** | Combines current year actuals with prior year data for incomplete months |
| **Multiple Calculation Methods** | Percentage increase, fixed dollar increase, spread evenly, or custom amounts |
| **Pivot Table Visualization** | Historical data displayed in easy-to-read vendor x month format |
| **Reasoning Capture** | Document justifications for each budget decision |
| **Variance Analysis** | Automatic calculation of % and $ differences vs. prior year |
| **SharePoint Export** | Approved budgets automatically saved as CSV to SharePoint |
| **Teams Integration** | Access the bot directly from Microsoft Teams |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MICROSOFT FABRIC WORKSPACE                          │
│                                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐                    │
│  │   LAKEHOUSE        │         │   DATA AGENT         │                    │
│  │                    │◄────────┤   (Budget Bot)       │                    │
│  │  Tables:           │         │                      │                    │
│  │  └─ GL_Detail_     │         │  - Agent Instructions│                    │
│  │     Budgeting      │         │  - Data Source       │                    │
│  │                    │         │    Instructions      │                    │
│  │  Columns:          │         │  - Example Queries   │                    │
│  │  • GL Number       │         │                      │                    │
│  │  • Vendor          │         │  Powered by:         │                    │
│  │  • Month & Year    │         │  Azure OpenAI        │                    │
│  │  • Amount          │         └──────────┬───────────┘                    │
│  │  • Department      │                    │                                │
│  └────────────────────┘                    │                                │
│                                            │                                │
└────────────────────────────────────────────┼────────────────────────────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              │                              │                              │
              ▼                              ▼                              ▼
   ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
   │  COPILOT STUDIO  │         │  POWER AUTOMATE  │         │  MICROSOFT TEAMS │
   │                  │         │                  │         │                  │
   │  Multi-Agent     │         │  Export to       │         │  User Access     │
   │  Orchestration   │────────►│  SharePoint CSV  │         │  Point           │
   └──────────────────┘         └──────────────────┘         └──────────────────┘
```

### Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   ERP/GL     │     │   Fabric     │     │   Data       │     │   Copilot    │
│   Export     │────►│   Lakehouse  │────►│   Agent      │────►│   Studio     │
│   (Excel)    │     │   (Delta)    │     │   (NL2SQL)   │     │   (Teams)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                            │                    │
                            │              ┌─────▼─────┐
                            │              │  Budget   │
                            │              │  Manager  │
                            │              └─────┬─────┘
                            │                    │
                            │              ┌─────▼─────┐
                            └─────────────►│ SharePoint│
                                           │   CSV     │
                                           └───────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Data Platform** | Microsoft Fabric Lakehouse | Store GL transaction data as Delta tables |
| **AI Engine** | Fabric Data Agent | Natural language to SQL conversion |
| **LLM Backend** | Azure OpenAI | Powers the conversational AI |
| **Orchestration** | Copilot Studio | Multi-agent workflow and Teams publishing |
| **Automation** | Power Automate | Export approved budgets to SharePoint |
| **Storage** | SharePoint | Store finalized budget CSV files |
| **Access Point** | Microsoft Teams | End-user interface |

---

## How It Works

### Conversation Flow

```
    USER                          BUDGET BOT
     │                                │
     ├─► "Hi Budget Bot"              │
     │                                ├─► Greeting + Ask for
     │                                │   Department
     │                                │
     ◄── "Sales & Marketing"          │
     │                                ├─► Query GL Numbers
     │                                │   Show available accounts
     │                                │
     ◄── "I want GL 35.600.500"       │
     │                                ├─► Query historical data
     │                                │   Display pivot table
     │                                │
     ◄── "Let's do FEDEX"             │
     │                                ├─► Show FEDEX spending
     │                                │   Offer budget methods
     │                                │
     ◄── "5% increase for inflation"  │
     │                                ├─► Calculate new budget
     │                                │   Show comparison
     │                                │   Ask for reasoning
     │                                │
     ◄── "Add $3K in March"           │
     │                                ├─► Recalculate with
     │                                │   one-time adjustment
     │                                │
     ◄── "Looks good, next vendor"    │
     │                                ├─► Save budget decision
     │                                │   Move to next vendor
```

### Workflow Steps

1. **Department Selection** - Bot asks which department the manager is responsible for
2. **GL Account Selection** - Shows available GL accounts for that department
3. **Historical Data Display** - Presents last 12 months of spending in pivot table format
4. **Vendor Selection** - Manager chooses which vendor to budget
5. **Budget Method** - Choose from 4 calculation methods
6. **Reasoning Capture** - Document the justification for the budget
7. **Review & Iterate** - Make adjustments as needed
8. **Export** - Save approved budgets to SharePoint

---

## Data Model

### Table Schema: GL_Detail_Budgeting

| Column | Type | Description |
|--------|------|-------------|
| `GL Number` | VARCHAR(50) | General Ledger account (format: XX.XXX.XXX) |
| `Vendor` | VARCHAR(255) | Vendor/supplier name |
| `Month & Year` | DATE | Transaction month (first day of month) |
| `Amount` | DECIMAL(18,2) | Transaction amount (negative = expense) |
| `Month Offset` | INT | Relative month (-1 = last month, -12 = 12 months ago) |
| `Department` | VARCHAR(100) | Department name |
| `GL Description` | VARCHAR(500) | Account description |

### Department to GL Mapping

| Department | GL Prefix |
|------------|-----------|
| Sales & Marketing | 32.600.XXX, 35.600.XXX, 36.600.XXX |
| Finance | 10.500.XXX, 11.500.XXX |
| HR | 30.500.XXX |
| Operations | 17.500.XXX, 18.500.XXX |
| Shipping | 33.700.XXX |

### Hybrid 12-Month Baseline

The bot uses a hybrid approach for the baseline data:

- **Current Year Actuals**: January through the last completed month
- **Prior Year Data**: For months not yet completed in current year

Example (if current month is October 2025):
- Jan 2025 - Sep 2025: Current year actuals
- Oct 2024 - Dec 2024: Prior year data (proxy for incomplete months)

---

## Budget Calculation Methods

### Method 1: Percentage Increase

```
New Budget = Prior Year Amount × (1 + Percentage/100)

Example:
  Prior Year: $1,000/month
  Increase: 5%
  New Budget: $1,000 × 1.05 = $1,050/month
```

### Method 2: Fixed Dollar Increase

```
New Budget = Prior Year Amount + Fixed Amount

Example:
  Prior Year: $1,000/month
  Increase: $50/month
  New Budget: $1,000 + $50 = $1,050/month
```

### Method 3: Annual Total Spread Evenly

```
New Budget = Annual Total ÷ 12

Example:
  Annual Budget: $12,000
  Monthly Budget: $12,000 ÷ 12 = $1,000/month
```

### Method 4: Custom Monthly + One-Time Adjustments

```
New Budget = (Prior Year Amount × (1 + Percentage/100)) + One-Time Adjustment

Example:
  Prior Year March: $899.10
  Base increase: 5%
  One-time: +$3,000 (for equipment purchase)

  Base Budget: $899.10 × 1.05 = $944.06
  Final Budget: $944.06 + $3,000 = $3,944.06
```

---

## Setup Guide

### Prerequisites

- Microsoft Fabric workspace (F2 SKU or higher)
- Access to create Data Agents
- Copilot Studio license (for Teams integration)
- SharePoint site for exports

### Step 1: Prepare Your Data

1. Export GL transaction data from your ERP system
2. Format with required columns:
   ```csv
   GL Number,Vendor,Month & Year,Amount,Month Offset,Department,GL Description
   35.600.500,FEDEX,2024-10-01,-224.89,-4,Sales & Marketing,Postage & Freight
   ```
3. Upload CSV to Fabric Lakehouse Files folder

### Step 2: Create Delta Table

Run this in a Fabric Notebook:

```python
from pyspark.sql.types import *

# Define schema
schema = StructType([
    StructField("GL_Number", StringType(), False),
    StructField("Vendor", StringType(), False),
    StructField("Month_Year", DateType(), False),
    StructField("Amount", DecimalType(18,2), False),
    StructField("Month_Offset", IntegerType(), False),
    StructField("Department", StringType(), True),
    StructField("GL_Description", StringType(), True)
])

# Read CSV
df = spark.read.format("csv") \
    .option("header", "true") \
    .schema(schema) \
    .load("/lakehouse/default/Files/GL_Detail_Budgeting.csv")

# Write to Delta table
df.write.mode("overwrite").format("delta").saveAsTable("GL_Detail_Budgeting")

print(f"Table created with {df.count()} rows")
```

### Step 3: Create Data Agent

1. In Fabric workspace, click **+ New Item** → **Data agent**
2. Name it "Budget Bot"
3. Add Lakehouse as data source
4. Select `GL_Detail_Budgeting` table
5. Copy the [Agent Instructions](#agent-instructions) below

### Step 4: Publish to Teams (Optional)

1. Open Copilot Studio
2. Import the Data Agent
3. Create agent flow for SharePoint export
4. Publish to Microsoft Teams

---

## Agent Instructions

### Agent-Level Instructions

Copy this into your Data Agent's main instructions:

```markdown
## Objective
You are Budget Bot, an AI assistant specialized in helping managers create annual budgets.
You help users analyze historical spending patterns by GL account and vendor, then create
budget projections for the coming year using various calculation methods.

## Core Responsibilities
1. Retrieve and present historical spending data by GL Number and Vendor
2. Create pivot tables showing monthly spending trends (last 12 months)
3. Help users apply budget calculations:
   - Same as last year + X% increase
   - Same as last year + $X per month
   - Total annual budget spread evenly
   - Custom monthly amounts
4. Track budget reasoning for each line item
5. Present data in clear, tabular formats

## Conversation Flow
1. Department Selection: Start by asking which department they manage
2. GL Account Selection: Show available GL accounts for that department
3. Historical Data: Display last 12 months of actuals by vendor (pivot format)
4. Vendor Selection: Ask which vendor to budget
5. Budget Method: Offer calculation options
6. Reasoning Capture: Ask for justification
7. Review & Iterate: Show calculations and ask for changes
8. Next Vendor: Continue until all vendors completed

## Department-to-GL Mapping
- Sales & Marketing: 32.600.XXX, 35.600.XXX, 36.600.XXX
- Finance: 10.500.XXX, 11.500.XXX
- HR: 30.500.XXX
- Operations: 17.500.XXX, 18.500.XXX
- Shipping: 33.700.XXX

## Output Format for Historical Data
Always present data in this pivot table format:

Vendor       | Jan 2025 | Feb 2025 | Mar 2025 | ... | Dec 2024 | Grand Total
-------------|----------|----------|----------|-----|----------|-------------
VENDOR A     | $XXX.XX  | $XXX.XX  | $XXX.XX  | ... | $XXX.XX  | $X,XXX.XX
VENDOR B     | $XXX.XX  | $XXX.XX  | $XXX.XX  | ... | $XXX.XX  | $X,XXX.XX
-------------|----------|----------|----------|-----|----------|-------------
Grand Total  | $XXX.XX  | $XXX.XX  | $XXX.XX  | ... | $XXX.XX  | $X,XXX.XX

## Tone & Style
- Be friendly and conversational
- Use clear, professional language
- Always confirm understanding before making calculations
- Celebrate progress ("Great! Let's save this and move to the next vendor")
- Ask clarifying questions when needed
```

### Data Source Instructions

Copy this into your Lakehouse data source instructions:

```markdown
## Schema Details
- GL Number: VARCHAR(50) - Format: XX.XXX.XXX (e.g., "35.600.500")
- Vendor: VARCHAR(255) - Company name providing goods/services
- Month & Year: DATE - Transaction month (stored as first day of month)
- Amount: DECIMAL(18,2) - Transaction amount (negative for expenses)
- Month Offset: INT - Relative month (-1 = last month, -12 = one year ago)

## Key Query Pattern
When the user asks for historical data by GL Number:

SELECT
    Vendor,
    FORMAT([Month & Year], 'MMM yyyy') AS Month,
    Amount
FROM GL_Detail_Budgeting
WHERE [GL Number] = '<USER_GL_NUMBER>'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY Vendor, [Month & Year] DESC
```

### Example Queries

Add these as few-shot examples:

**Question:** Show me the historical spending for GL Number 35.600.500 by vendor
```sql
SELECT Vendor, FORMAT([Month & Year], 'MMM yyyy') AS Month, Amount
FROM GL_Detail_Budgeting
WHERE [GL Number] = '35.600.500'
    AND [Month Offset] BETWEEN -12 AND -1
ORDER BY Vendor, [Month & Year] DESC
```

**Question:** What GL accounts are available for Sales & Marketing?
```sql
SELECT DISTINCT [GL Number], COUNT(*) AS TransactionCount, SUM(Amount) AS TotalAmount
FROM GL_Detail_Budgeting
WHERE [GL Number] LIKE '35.600.%' OR [GL Number] LIKE '32.600.%' OR [GL Number] LIKE '36.600.%'
GROUP BY [GL Number]
ORDER BY [GL Number]
```

---

## Example Conversation

```
User: Hi Budget Bot, I need help creating a budget for next year

Bot: Hi! I'm Budget Bot. I'm here to help you develop a budget for the coming year.
     For which department are you responsible for creating a budget?
     (1) Sales & Marketing
     (2) Finance
     (3) HR
     (4) Operations
     (5) Shipping

User: I'm in charge of Sales & Marketing

Bot: The Sales & Marketing department is responsible for the following GL Accounts:
     (1) Postage & Frt Out - PKG S&M (35.600.500)
     (2) Supplies - PKG S&M (35.600.260)
     (3) Meetings & Seminars - PB S&M (32.600.340)

     Which GL account would you like to work on?

User: Let's work on 35.600.500

Bot: Here are the expenses by vendor for Postage & Frt Out - PKG S&M (35.600.500).
     I'm showing 2025 actuals for January to September. Since we haven't finished
     October to December for 2025, I've used figures from 2024 for those months.

                    Jan 2025  Feb 2025  Mar 2025  ...  Oct 2024  Nov 2024  Dec 2024  Total
     FEDEX              $0        $0      $899   ...     $225      $478      $203   $5,041
     UPS SUPPLY         $0        $0        $0   ...      $64        $0        $0      $64
     Grand Total        $0        $0      $899   ...     $289      $478      $203   $5,105

     Which vendor do you want to budget for first?

User: Let's budget for FEDEX with a 5% increase for inflation

Bot: What is the reason for the 5% increase?

User: General inflation in shipping costs

Bot: Ok, here is what a 5% increase over last year for inflation would look like:

     Historical (2025 Actuals + 2024 proxy):
                    Jan    Feb    Mar    Apr    May    Jun    ...    Total
     FEDEX           $0     $0   $899   $530   $487   $526   ...   $5,041

     Projected Budget 2026:
                    Jan    Feb    Mar    Apr    May    Jun    ...    Total
     FEDEX           $0     $0   $944   $557   $511   $552   ...   $5,293
     % Diff         n/a    n/a     5%     5%     5%     5%   ...       5%

     Reasoning: 5% increase for general inflation in shipping costs

     Do you want to make any changes or move on to the next vendor?

User: We also need to add $3,000 in March for new equipment

Bot: Updated budget with $3,000 one-time expense in March:

     Projected Budget 2026:
                    Jan    Feb      Mar    Apr    May    Jun    ...    Total
     FEDEX           $0     $0   $3,944   $557   $511   $552   ...   $8,293
     % Diff         n/a    n/a     339%     5%     5%     5%   ...      65%

     Reasoning: 5% increase for inflation + $3K in March for new equipment

     Do you want to make any changes or move on to the next vendor?

User: That looks good, let's save and move to the next vendor

Bot: Saved! Moving to the next vendor...
```

---

## Project Structure

```
Microsoft-Fabric-Budgeting-Agent/
├── README.md                    # This file
├── assets/
│   └── demo.gif                 # Demo video
├── instructions/
│   ├── agent-instructions.md    # Main agent instructions
│   └── data-source-instructions.md
├── queries/
│   └── example-queries.sql      # Few-shot learning queries
├── scripts/
│   └── create-table.py          # Notebook code for table creation
└── sample-data/
    └── GL_Detail_Budgeting.csv  # Sample data structure
```

---

## Key Learnings

1. **Star Schema Matters** - Optimizing the data model for the agent significantly improves query accuracy
2. **Few-Shot Examples** - Adding specific SQL examples dramatically improves NL2SQL performance
3. **Clear Instructions** - Detailed agent instructions with output formats reduce ambiguity
4. **Hybrid Baseline** - Combining current and prior year data provides complete 12-month views
5. **Conversation Design** - A structured flow keeps users on track while allowing flexibility

---

## Resources

- [Microsoft Fabric Data Agent Documentation](https://learn.microsoft.com/fabric/data-science/concept-data-agent)
- [Create a Data Agent](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent)
- [Best Practices for Data Agents](https://learn.microsoft.com/fabric/data-science/data-agent-configuration-best-practices)
- [Copilot Studio Integration](https://learn.microsoft.com/microsoft-copilot-studio/)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Sulaiman Ahmed**

- Built for enterprise budgeting workflow automation
- Deployed October 2025
