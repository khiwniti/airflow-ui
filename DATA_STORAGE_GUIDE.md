# 📊 Local Data Storage Guide

This guide explains how data from Airflow DAGs is automatically stored on your localhost after DAG execution.

## 🎯 Overview

All DAGs in this project are configured to save their output data to local files on your machine. This allows you to:
- ✅ **Access processed data** directly from your localhost
- ✅ **Analyze results** using your preferred tools
- ✅ **Archive data** for historical analysis
- ✅ **Share outputs** easily with your team

## 📁 Data Storage Location

All data files are stored in the `data_output/` directory:

```
synapes-analytics/
├── data_output/           # 📊 All DAG output data
│   ├── customer_data_*.json
│   ├── customer_data_*.csv
│   ├── sales_data_*.json
│   ├── sales_data_*.csv
│   ├── analytics_result_*.json
│   ├── analytics_summary_*.csv
│   └── oracle_*.json/csv  # (when Oracle DAG runs)
├── dags/
├── scripts/
└── ...
```

## 🔄 How It Works

### 1. **Automatic Data Generation**
When DAGs run, they automatically:
- Extract data from sources
- Process and transform data
- Save results to both JSON and CSV formats
- Include timestamps in filenames for versioning

### 2. **File Naming Convention**
```
{data_type}_{timestamp}.{format}

Examples:
- customer_data_20250611_085014.json
- sales_data_20250611_085014.csv
- analytics_result_20250611_085015.json
- oracle_customers_20250611_120000.json
```

### 3. **Data Formats**

#### **JSON Files** 📄
- Complete data with full details
- Nested structures for complex data
- Timestamps and metadata included
- Easy to parse programmatically

#### **CSV Files** 📊
- Tabular format for spreadsheet analysis
- Compatible with Excel, Power BI, etc.
- Summary data for quick analysis
- Easy to import into databases

## 📋 Available Data Types

### 1. **Customer Data** 👥
- **Files**: `customer_data_*.json/csv`
- **Content**: Customer information, contact details
- **Source**: Dataset example DAG or Oracle ERP

### 2. **Sales Data** 💰
- **Files**: `sales_data_*.json/csv`
- **Content**: Transaction records, amounts, dates
- **Source**: Dataset example DAG or Oracle ERP

### 3. **Analytics Results** 📈
- **Files**: `analytics_result_*.json`, `analytics_summary_*.csv`
- **Content**: Processed metrics, KPIs, summaries
- **Source**: Data processing tasks

### 4. **Oracle ERP Data** 🏢
- **Files**: `oracle_customers_*.json/csv`, `oracle_invoices_*.json/csv`
- **Content**: Real ERP data from Oracle database
- **Source**: Oracle ERP integration DAG

## 🛠️ How to Access Data

### **Method 1: Direct File Access**
```bash
# View latest files
ls -lt data_output/

# View JSON data
cat data_output/customer_data_*.json

# View CSV data
cat data_output/analytics_summary_*.csv
```

### **Method 2: Copy from Container** (Recommended)
Use the provided scripts to copy latest data:

#### **Windows (PowerShell)**
```powershell
.\scripts\copy_data_from_container.ps1
```

#### **Linux/Mac**
```bash
./scripts/copy_data_from_container.sh
```

### **Method 3: Programmatic Access**

#### **Python**
```python
import json
import pandas as pd
from pathlib import Path

# Read JSON data
with open('data_output/customer_data_latest.json') as f:
    customers = json.load(f)

# Read CSV data
sales_df = pd.read_csv('data_output/sales_data_latest.csv')

# Analyze data
print(f"Total customers: {len(customers)}")
print(f"Total sales: ${sales_df['amount'].sum():.2f}")
```

#### **PowerShell**
```powershell
# Read JSON
$customers = Get-Content data_output\customer_data_*.json | ConvertFrom-Json

# Read CSV
$sales = Import-Csv data_output\sales_data_*.csv

# Analyze
Write-Host "Total customers: $($customers.Count)"
Write-Host "Total sales: $($sales | Measure-Object amount -Sum | Select -ExpandProperty Sum)"
```

## 📊 Data Monitoring

### **Data Monitor DAG**
The `data_monitor_pipeline` DAG automatically:
- 🔍 Scans all data files
- 📈 Generates usage statistics
- 🗂️ Categorizes by data type
- 📅 Tracks file creation times
- 💾 Creates summary reports

### **Manual Monitoring**
```bash
# Count files by type
find data_output -name "*.json" | wc -l
find data_output -name "*.csv" | wc -l

# Show disk usage
du -sh data_output/

# Latest files
ls -lt data_output/ | head -10
```

## 🔧 Configuration

### **Customizing Output Location**
To change the data output directory, update the DAGs:

```python
# In your DAG files, change:
output_dir = "/opt/airflow/data_output"
# To:
output_dir = "/opt/airflow/custom_output"
```

### **File Retention**
The data monitor DAG includes cleanup logic (currently disabled for safety):
- Files older than 7 days are identified
- Manual cleanup can be enabled
- Automatic archiving can be implemented

## 🚀 Integration Examples

### **Excel Analysis**
1. Copy CSV files to your desktop
2. Open in Excel or Google Sheets
3. Create pivot tables and charts
4. Generate business reports

### **Power BI Dashboard**
1. Connect Power BI to the `data_output` folder
2. Set up automatic refresh
3. Create real-time dashboards
4. Share with stakeholders

### **Database Import**
```sql
-- Import CSV to database
LOAD DATA INFILE 'data_output/sales_data_latest.csv'
INTO TABLE sales_analysis
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

## 🔍 Troubleshooting

### **No Data Files Generated**
1. Check if DAGs are running successfully
2. Verify container volume mounts
3. Run the copy script manually
4. Check DAG logs for errors

### **Permission Issues**
```bash
# Fix permissions (Linux/Mac)
sudo chown -R $USER:$USER data_output/
chmod -R 755 data_output/
```

### **Large File Sizes**
- Monitor disk space usage
- Implement data archiving
- Compress old files
- Set up automatic cleanup

## 📈 Best Practices

1. **Regular Backups**: Archive important data files
2. **Monitoring**: Use the data monitor DAG regularly
3. **Cleanup**: Remove old files periodically
4. **Documentation**: Document custom data formats
5. **Security**: Protect sensitive data appropriately

## 🎉 Success Indicators

✅ **Data files appear in `data_output/`**  
✅ **Files have recent timestamps**  
✅ **Both JSON and CSV formats available**  
✅ **Data contains expected content**  
✅ **Copy scripts work without errors**  

Your Airflow setup now automatically stores all processed data locally for easy access and analysis! 🎊
