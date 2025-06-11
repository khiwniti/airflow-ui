# Oracle ERP Integration Guide

This guide explains how to integrate Oracle E-Business Suite (EBS) with your Airflow deployment for data analytics and ETL operations.

## 🔗 Connection Details

### Development Environment
- **Hostname**: 176.16.30.133
- **Port**: 1554
- **SID**: EBSDEV
- **Username**: apps
- **Password**: appsdev

## 🚀 Quick Setup

### 1. Install Dependencies
The required Oracle libraries are already included in `requirements.txt`:
```
cx_Oracle==8.3.0
oracledb==1.4.2
apache-airflow-providers-oracle==3.10.1
```

### 2. Set Up Connection
Run the setup script to create the Airflow connection:
```bash
# From inside the Airflow container
python /opt/airflow/scripts/setup_oracle_connection.py
```

### 3. Restart Services
```bash
docker-compose restart airflow-webserver airflow-scheduler
```

## 📊 Available DAGs

### Oracle ERP Data Pipeline (`oracle_erp_data_pipeline`)
- **Purpose**: Extract and process data from Oracle ERP
- **Schedule**: Daily
- **Features**:
  - Connection testing
  - Customer data extraction
  - Invoice data extraction
  - Data validation
  - Summary reporting

## 🔧 Configuration

### Environment Variables
Set these in your `.env` file:
```bash
ORACLE_ERP_HOST=176.16.30.133
ORACLE_ERP_PORT=1554
ORACLE_ERP_SID=EBSDEV
ORACLE_ERP_USERNAME=apps
ORACLE_ERP_PASSWORD=appsdev
```

### Airflow Connection
- **Connection ID**: `oracle_erp_dev`
- **Connection Type**: Oracle
- **Host**: 176.16.30.133
- **Port**: 1554
- **Schema**: EBSDEV
- **Login**: apps
- **Password**: appsdev

## 📋 Common ERP Tables

### Customer Management
- `AR_CUSTOMERS` - Customer master data
- `HZ_PARTIES` - Party information
- `HZ_PARTY_SITES` - Customer sites

### Financial Data
- `AR_INVOICES_ALL` - Invoice headers
- `AR_INVOICE_LINES_ALL` - Invoice line details
- `AR_RECEIPTS` - Receipt information

### Inventory
- `MTL_SYSTEM_ITEMS_B` - Item master
- `MTL_ONHAND_QUANTITIES` - On-hand inventory
- `MTL_TRANSACTIONS` - Inventory transactions

### Purchase Orders
- `PO_HEADERS_ALL` - Purchase order headers
- `PO_LINES_ALL` - Purchase order lines
- `PO_RECEIPTS` - Receipt information

## 🛠️ Sample Queries

### Customer Data
```sql
SELECT 
    CUSTOMER_ID,
    CUSTOMER_NAME,
    CUSTOMER_NUMBER,
    CREATION_DATE,
    STATUS
FROM AR_CUSTOMERS 
WHERE CREATION_DATE >= SYSDATE - 30
```

### Invoice Summary
```sql
SELECT 
    INVOICE_NUMBER,
    CUSTOMER_ID,
    INVOICE_DATE,
    TOTAL_AMOUNT,
    CURRENCY_CODE
FROM AR_INVOICES_ALL 
WHERE INVOICE_DATE >= SYSDATE - 7
```

### Inventory Levels
```sql
SELECT 
    ITEM_ID,
    ORGANIZATION_ID,
    SUBINVENTORY_CODE,
    SUM(TRANSACTION_QUANTITY) as ON_HAND_QTY
FROM MTL_ONHAND_QUANTITIES
GROUP BY ITEM_ID, ORGANIZATION_ID, SUBINVENTORY_CODE
```

## 🔒 Security Considerations

### Development Environment
- ✅ Using development credentials
- ✅ Environment variables for configuration
- ✅ Connection encryption

### Production Recommendations
- 🔐 Use Airflow Variables or Secrets Backend
- 🔐 Implement database connection pooling
- 🔐 Regular password rotation
- 🔐 Network security (VPN/firewall)
- 🔐 Audit logging and monitoring
- 🔐 Principle of least privilege

## 🚨 Troubleshooting

### Connection Issues
1. **TNS Error**: Check hostname, port, and SID
2. **Authentication Failed**: Verify username/password
3. **Network Timeout**: Check firewall and network connectivity

### Common Solutions
```bash
# Test connection from container
docker-compose exec airflow-scheduler python -c "
from airflow.providers.oracle.hooks.oracle import OracleHook
hook = OracleHook(oracle_conn_id='oracle_erp_dev')
conn = hook.get_conn()
print('Connection successful!')
"

# Check Oracle client version
docker-compose exec airflow-scheduler python -c "
import cx_Oracle
print(f'Oracle Client Version: {cx_Oracle.clientversion()}')
"
```

### Performance Optimization
- Use connection pooling
- Implement query pagination for large datasets
- Add appropriate indexes on frequently queried columns
- Monitor query execution plans

## 📈 Monitoring and Logging

### Key Metrics to Monitor
- Connection success rate
- Query execution time
- Data extraction volume
- Error rates

### Log Locations
- Airflow Task Logs: Available in Airflow UI
- Oracle Alert Logs: Check with DBA
- Network Logs: Check firewall/proxy logs

## 🔄 Data Pipeline Best Practices

### 1. Incremental Loading
```python
# Use date filters for incremental loads
WHERE LAST_UPDATE_DATE >= :last_run_date
```

### 2. Error Handling
```python
try:
    data = oracle_hook.get_pandas_df(sql)
except Exception as e:
    logging.error(f"Query failed: {e}")
    raise
```

### 3. Data Validation
```python
# Validate data quality
if len(data) == 0:
    raise ValueError("No data returned from query")
```

### 4. Resource Management
```python
# Always close connections
try:
    conn = oracle_hook.get_conn()
    # ... use connection
finally:
    conn.close()
```

## 📞 Support

For issues with:
- **Airflow**: Check logs in Airflow UI
- **Oracle Connection**: Contact DBA team
- **Data Pipeline**: Review DAG logs and task details

## 🔗 Useful Links

- [Oracle Provider Documentation](https://airflow.apache.org/docs/apache-airflow-providers-oracle/)
- [cx_Oracle Documentation](https://cx-oracle.readthedocs.io/)
- [Oracle EBS Documentation](https://docs.oracle.com/cd/E26401_01/index.htm)
