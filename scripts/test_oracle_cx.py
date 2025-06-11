#!/usr/bin/env python3
"""
Oracle connection test using cx_Oracle (older library)
This may work better with older Oracle database versions
"""

import sys
from datetime import datetime

def test_cx_oracle_connection():
    """Test Oracle connection using cx_Oracle library"""
    
    try:
        import cx_Oracle
        print("✅ cx_Oracle library is available")
    except ImportError:
        print("❌ cx_Oracle library not found")
        return False
    
    # Connection details
    host = "176.16.30.133"
    port = 1554
    service_name = "EBSDEV"
    username = "apps"
    password = "appsdev"
    
    print(f"🔄 Testing Oracle connection using cx_Oracle to {host}:{port}/{service_name}")
    print(f"📅 Test started at: {datetime.now()}")
    print("-" * 60)
    
    try:
        # Create connection string
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        print(f"🔗 DSN: {dsn}")
        
        # Connect to Oracle
        connection = cx_Oracle.connect(
            user=username,
            password=password,
            dsn=dsn
        )
        
        print("✅ cx_Oracle connection established successfully!")
        
        # Test simple query
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Simple query test - SUCCESS")
        
        # Check Oracle version
        cursor.execute("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1")
        version = cursor.fetchone()
        if version:
            print(f"📊 Oracle Version: {version[0]}")
        
        # Check user
        cursor.execute("SELECT USER FROM DUAL")
        current_user = cursor.fetchone()
        if current_user:
            print(f"👤 Connected as user: {current_user[0]}")
        
        # Close connection
        cursor.close()
        connection.close()
        print("\n🎉 cx_Oracle connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ cx_Oracle connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Oracle EBS Connection Test (cx_Oracle)")
    print("=" * 60)
    
    success = test_cx_oracle_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 OVERALL RESULT: cx_Oracle CONNECTION SUCCESSFUL!")
        sys.exit(0)
    else:
        print("💥 OVERALL RESULT: cx_Oracle CONNECTION FAILED!")
        sys.exit(1)
