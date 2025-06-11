#!/usr/bin/env python3
"""
Simple Oracle connection test script
Tests connectivity to Oracle EBS server from within the Airflow container
"""

import oracledb
import sys
import time
from datetime import datetime

def test_oracle_connection():
    """Test Oracle connection with different methods"""
    
    # Connection details
    host = "176.16.30.133"
    port = 1554
    service_name = "EBSDEV"
    username = "apps"
    password = "appsdev"
    
    print(f"🔄 Testing Oracle connection to {host}:{port}/{service_name}")
    print(f"📅 Test started at: {datetime.now()}")
    print("-" * 60)
    
    # Test 1: Basic connectivity test
    print("1️⃣ Testing basic network connectivity...")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Network connectivity to {host}:{port} - SUCCESS")
        else:
            print(f"❌ Network connectivity to {host}:{port} - FAILED (Error: {result})")
            return False
    except Exception as e:
        print(f"❌ Network test failed: {str(e)}")
        return False
    
    # Test 2: Oracle thin mode connection
    print("\n2️⃣ Testing Oracle thin mode connection...")
    try:
        # Create connection string
        dsn = f"{host}:{port}/{service_name}"
        print(f"🔗 DSN: {dsn}")
        
        # Set connection timeout
        connection = oracledb.connect(
            user=username,
            password=password,
            dsn=dsn,
            mode=oracledb.DEFAULT_AUTH
        )
        
        print("✅ Oracle connection established successfully!")
        
        # Test 3: Simple query
        print("\n3️⃣ Testing simple query...")
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("✅ Simple query test - SUCCESS")
        else:
            print("❌ Simple query test - FAILED")
            
        # Test 4: Check Oracle version
        print("\n4️⃣ Checking Oracle version...")
        cursor.execute("SELECT BANNER FROM V$VERSION WHERE ROWNUM = 1")
        version = cursor.fetchone()
        if version:
            print(f"📊 Oracle Version: {version[0]}")
        
        # Test 5: Check user privileges
        print("\n5️⃣ Checking user privileges...")
        cursor.execute("SELECT USER FROM DUAL")
        current_user = cursor.fetchone()
        if current_user:
            print(f"👤 Connected as user: {current_user[0]}")
            
        # Test 6: Check accessible tables
        print("\n6️⃣ Checking accessible tables...")
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ALL_TABLES 
                WHERE OWNER = 'APPS' 
                AND TABLE_NAME IN ('AR_CUSTOMERS', 'AR_INVOICES_ALL')
            """)
            table_count = cursor.fetchone()
            if table_count and table_count[0] > 0:
                print(f"✅ Found {table_count[0]} ERP tables accessible")
            else:
                print("⚠️ ERP tables not found or not accessible")
        except Exception as e:
            print(f"⚠️ Table check failed: {str(e)}")
        
        # Close connection
        cursor.close()
        connection.close()
        print("\n🎉 All Oracle connection tests completed successfully!")
        return True
        
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        print(f"❌ Oracle Database Error:")
        print(f"   Code: {error_obj.code}")
        print(f"   Message: {error_obj.message}")
        
        # Check for specific error types
        if "password verifier" in str(e).lower():
            print("\n💡 Suggestion: Password verifier compatibility issue detected.")
            print("   This usually happens with older Oracle versions.")
            print("   Try connecting with a different Oracle client version.")
        elif "listener" in str(e).lower():
            print("\n💡 Suggestion: Oracle listener issue detected.")
            print("   Check if the Oracle service is running on the server.")
        elif "network" in str(e).lower() or "timeout" in str(e).lower():
            print("\n💡 Suggestion: Network connectivity issue detected.")
            print("   Check firewall settings and network connectivity.")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Oracle EBS Connection Test")
    print("=" * 60)
    
    success = test_oracle_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 OVERALL RESULT: CONNECTION SUCCESSFUL!")
        print("✅ Oracle EBS server is accessible and ready for data extraction.")
        sys.exit(0)
    else:
        print("💥 OVERALL RESULT: CONNECTION FAILED!")
        print("❌ Please check the connection details and server status.")
        sys.exit(1)
