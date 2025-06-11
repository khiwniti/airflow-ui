#!/usr/bin/env python3
"""
Script to set up Oracle ERP connection in Airflow
This script creates the necessary Airflow connection for Oracle ERP access
"""

import os
import sys
from airflow.models import Connection
from airflow import settings
from sqlalchemy.orm import sessionmaker

def create_oracle_connection():
    """
    Create Oracle ERP connection in Airflow
    """
    
    # Get connection details from environment variables
    host = os.getenv('ORACLE_ERP_HOST', '176.16.30.133')
    port = os.getenv('ORACLE_ERP_PORT', '1554')
    sid = os.getenv('ORACLE_ERP_SID', 'EBSDEV')
    username = os.getenv('ORACLE_ERP_USERNAME', 'apps')
    password = os.getenv('ORACLE_ERP_PASSWORD', 'appsdev')
    
    # Create connection object
    new_conn = Connection(
        conn_id='oracle_erp_dev',
        conn_type='oracle',
        host=host,
        port=int(port),
        login=username,
        password=password,
        schema=sid,  # For Oracle, schema is typically the SID
        extra={
            'service_name': sid,
            'module': 'airflow',
            'thick_mode': False  # Use thin mode for easier deployment
        }
    )
    
    # Get Airflow session
    session = settings.Session()
    
    try:
        # Check if connection already exists
        existing_conn = session.query(Connection).filter(
            Connection.conn_id == 'oracle_erp_dev'
        ).first()
        
        if existing_conn:
            print("Connection 'oracle_erp_dev' already exists. Updating...")
            existing_conn.host = host
            existing_conn.port = int(port)
            existing_conn.login = username
            existing_conn.password = password
            existing_conn.schema = sid
            existing_conn.extra = new_conn.extra
        else:
            print("Creating new connection 'oracle_erp_dev'...")
            session.add(new_conn)
        
        session.commit()
        print("✅ Oracle ERP connection created/updated successfully!")
        
        # Print connection details (without password)
        print(f"""
📋 Connection Details:
   Connection ID: oracle_erp_dev
   Host: {host}
   Port: {port}
   SID: {sid}
   Username: {username}
   Password: [HIDDEN]
        """)
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating connection: {str(e)}")
        return False
    finally:
        session.close()
    
    return True

def test_connection():
    """
    Test the Oracle connection
    """
    try:
        from airflow.providers.oracle.hooks.oracle import OracleHook
        
        print("🔍 Testing Oracle connection...")
        
        oracle_hook = OracleHook(oracle_conn_id='oracle_erp_dev')
        connection = oracle_hook.get_conn()
        cursor = connection.cursor()
        
        # Test query
        cursor.execute("SELECT SYSDATE, USER FROM DUAL")
        result = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        print(f"✅ Connection test successful!")
        print(f"   Server Time: {result[0]}")
        print(f"   Connected User: {result[1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Oracle ERP connection for Airflow...")
    print("=" * 50)
    
    # Create connection
    if create_oracle_connection():
        print("\n🧪 Testing connection...")
        test_connection()
    else:
        print("❌ Failed to create connection")
        sys.exit(1)
    
    print("\n✅ Setup completed!")
    print("""
📝 Next Steps:
1. Restart Airflow services to pick up the new connection
2. Check the Oracle ERP DAG in Airflow UI
3. Test the DAG execution
4. Monitor logs for any issues

🔒 Security Note:
- Consider using Airflow Variables or Secrets for sensitive data in production
- Implement proper access controls and network security
- Regular password rotation and monitoring
    """)
