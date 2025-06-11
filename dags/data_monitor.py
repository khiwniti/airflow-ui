"""
## Data Monitor DAG

This DAG monitors the data_output directory and shows what files have been created
by other DAGs. It provides a summary of all stored data files.
"""

from airflow.decorators import dag, task
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import os
import json

# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='data_monitor_pipeline',
    default_args=default_args,
    description='Monitor and report on stored data files',
    schedule_interval='@hourly',
    catchup=False,
    tags=['monitoring', 'data', 'files'],
    doc_md=__doc__,
)
def data_monitor_pipeline():
    
    @task
    def scan_data_directory() -> Dict:
        """
        Scan the data_output directory and catalog all files
        """
        output_dir = "/opt/airflow/data_output"
        
        if not os.path.exists(output_dir):
            logging.warning(f"Data output directory does not exist: {output_dir}")
            return {
                'status': 'directory_not_found',
                'files': [],
                'total_files': 0,
                'scan_time': datetime.now().isoformat()
            }
        
        files_info = []
        total_size = 0
        
        try:
            for filename in os.listdir(output_dir):
                file_path = os.path.join(output_dir, filename)
                if os.path.isfile(file_path):
                    stat_info = os.stat(file_path)
                    file_info = {
                        'filename': filename,
                        'size_bytes': stat_info.st_size,
                        'size_mb': round(stat_info.st_size / (1024 * 1024), 2),
                        'created_time': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                        'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                        'file_type': filename.split('.')[-1] if '.' in filename else 'unknown'
                    }
                    files_info.append(file_info)
                    total_size += stat_info.st_size
            
            # Sort by creation time (newest first)
            files_info.sort(key=lambda x: x['created_time'], reverse=True)
            
            result = {
                'status': 'success',
                'files': files_info,
                'total_files': len(files_info),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'scan_time': datetime.now().isoformat(),
                'directory': output_dir
            }
            
            logging.info(f"📁 Scanned data directory: {output_dir}")
            logging.info(f"📊 Found {len(files_info)} files, total size: {result['total_size_mb']} MB")
            
            return result
            
        except Exception as e:
            logging.error(f"Error scanning directory: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'files': [],
                'total_files': 0,
                'scan_time': datetime.now().isoformat()
            }
    
    @task
    def generate_file_summary(scan_result: Dict) -> Dict:
        """
        Generate a summary report of the files
        """
        if scan_result['status'] != 'success':
            return {
                'summary': 'No files to summarize',
                'error': scan_result.get('error', 'Unknown error')
            }
        
        files = scan_result['files']
        
        # Group by file type
        file_types = {}
        for file_info in files:
            file_type = file_info['file_type']
            if file_type not in file_types:
                file_types[file_type] = {
                    'count': 0,
                    'total_size_mb': 0,
                    'files': []
                }
            file_types[file_type]['count'] += 1
            file_types[file_type]['total_size_mb'] += file_info['size_mb']
            file_types[file_type]['files'].append(file_info['filename'])
        
        # Group by data source (based on filename patterns)
        data_sources = {}
        for file_info in files:
            filename = file_info['filename']
            if 'customer' in filename:
                source = 'customer_data'
            elif 'sales' in filename:
                source = 'sales_data'
            elif 'analytics' in filename:
                source = 'analytics_data'
            elif 'oracle' in filename:
                source = 'oracle_data'
            else:
                source = 'other'
            
            if source not in data_sources:
                data_sources[source] = {
                    'count': 0,
                    'total_size_mb': 0,
                    'latest_file': None
                }
            data_sources[source]['count'] += 1
            data_sources[source]['total_size_mb'] += file_info['size_mb']
            
            # Track latest file
            if (data_sources[source]['latest_file'] is None or 
                file_info['created_time'] > data_sources[source]['latest_file']['created_time']):
                data_sources[source]['latest_file'] = file_info
        
        summary = {
            'total_files': scan_result['total_files'],
            'total_size_mb': scan_result['total_size_mb'],
            'file_types': file_types,
            'data_sources': data_sources,
            'latest_files': files[:5],  # Show 5 most recent files
            'generated_at': datetime.now().isoformat()
        }
        
        # Save summary to file
        output_dir = "/opt/airflow/data_output"
        summary_file = f"{output_dir}/data_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            logging.info(f"💾 Summary saved to: {summary_file}")
        except Exception as e:
            logging.error(f"Failed to save summary: {str(e)}")
        
        # Log summary information
        logging.info("📊 DATA SUMMARY REPORT 📊")
        logging.info(f"Total Files: {summary['total_files']}")
        logging.info(f"Total Size: {summary['total_size_mb']} MB")
        logging.info("File Types:")
        for file_type, info in file_types.items():
            logging.info(f"  - {file_type}: {info['count']} files ({info['total_size_mb']} MB)")
        logging.info("Data Sources:")
        for source, info in data_sources.items():
            latest = info['latest_file']['filename'] if info['latest_file'] else 'None'
            logging.info(f"  - {source}: {info['count']} files, latest: {latest}")
        
        return summary
    
    @task
    def cleanup_old_files(scan_result: Dict) -> Dict:
        """
        Clean up files older than 7 days (optional)
        """
        if scan_result['status'] != 'success':
            return {'status': 'skipped', 'reason': 'scan failed'}
        
        cutoff_time = datetime.now() - timedelta(days=7)
        files_to_delete = []
        
        for file_info in scan_result['files']:
            file_created = datetime.fromisoformat(file_info['created_time'])
            if file_created < cutoff_time:
                files_to_delete.append(file_info)
        
        # For safety, we'll just log what would be deleted rather than actually deleting
        if files_to_delete:
            logging.info(f"🗑️ Found {len(files_to_delete)} files older than 7 days:")
            for file_info in files_to_delete:
                logging.info(f"  - {file_info['filename']} (created: {file_info['created_time']})")
            logging.info("ℹ️ Files not deleted automatically. Manual cleanup required if needed.")
        else:
            logging.info("✅ No old files found for cleanup")
        
        return {
            'status': 'completed',
            'old_files_found': len(files_to_delete),
            'files_deleted': 0,  # We're not actually deleting
            'cleanup_time': datetime.now().isoformat()
        }
    
    # Define task dependencies
    scan_result = scan_data_directory()
    summary = generate_file_summary(scan_result)
    cleanup_result = cleanup_old_files(scan_result)
    
    # Set dependencies
    scan_result >> [summary, cleanup_result]

# Instantiate the DAG
data_monitor_pipeline()
