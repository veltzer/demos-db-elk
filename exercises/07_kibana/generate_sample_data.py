#!/usr/bin/env python

import os
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import argparse

fake = Faker()

def generate_web_log_entry():
    """Generate a realistic web server log entry"""
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    status_codes = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'curl/7.68.0',
        'Python-requests/2.25.1'
    ]
    
    return {
        'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
        'ip_address': fake.ipv4(),
        'method': random.choice(methods),
        'url': fake.uri_path(),
        'status_code': random.choice(status_codes),
        'response_size': random.randint(200, 50000),
        'response_time_ms': random.randint(10, 5000),
        'user_agent': random.choice(user_agents),
        'referer': fake.url() if random.random() > 0.3 else '-',
        'country': fake.country_code(),
        'city': fake.city()
    }

def generate_ecommerce_transaction():
    """Generate an e-commerce transaction"""
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports', 'Beauty']
    payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay']
    
    return {
        'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
        'transaction_id': fake.uuid4(),
        'customer_id': fake.uuid4(),
        'customer_email': fake.email(),
        'customer_age': random.randint(18, 80),
        'customer_gender': random.choice(['M', 'F', 'Other']),
        'product_name': fake.catch_phrase(),
        'product_category': random.choice(categories),
        'quantity': random.randint(1, 5),
        'unit_price': round(random.uniform(10.0, 500.0), 2),
        'total_amount': 0,  # Will be calculated
        'payment_method': random.choice(payment_methods),
        'shipping_country': fake.country(),
        'shipping_city': fake.city(),
        'is_mobile': random.choice([True, False]),
        'promotion_code': fake.word() if random.random() > 0.7 else None
    }

def generate_system_metrics():
    """Generate system performance metrics"""
    return {
        'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
        'server_name': f"server-{random.randint(1, 10):02d}",
        'cpu_usage_percent': round(random.uniform(10.0, 95.0), 2),
        'memory_usage_percent': round(random.uniform(20.0, 90.0), 2),
        'disk_usage_percent': round(random.uniform(30.0, 85.0), 2),
        'network_in_mbps': round(random.uniform(0.1, 100.0), 2),
        'network_out_mbps': round(random.uniform(0.1, 100.0), 2),
        'active_connections': random.randint(50, 1000),
        'load_average': round(random.uniform(0.1, 4.0), 2),
        'uptime_hours': random.randint(1, 8760)
    }

def generate_application_logs():
    """Generate application log entries"""
    log_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
    services = ['auth-service', 'user-service', 'payment-service', 'notification-service', 'api-gateway']
    
    return {
        'timestamp': fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
        'level': random.choice(log_levels),
        'service': random.choice(services),
        'message': fake.sentence(),
        'user_id': fake.uuid4() if random.random() > 0.3 else None,
        'session_id': fake.uuid4(),
        'request_id': fake.uuid4(),
        'duration_ms': random.randint(1, 2000),
        'thread': f"thread-{random.randint(1, 20)}",
        'class_name': f"{fake.word().capitalize()}Service",
        'method_name': fake.word()
    }

def main():
    parser = argparse.ArgumentParser(description='Generate sample data for Kibana exercises')
    parser.add_argument('--type', choices=['web_logs', 'ecommerce', 'metrics', 'app_logs', 'all'], 
                       default='all', help='Type of data to generate')
    parser.add_argument('--count', type=int, default=1000, help='Number of records to generate per type')
    parser.add_argument('--output', default='sample_data.json', help='Output file name')
    
    args = parser.parse_args()
    
    data = []
    
    if args.type == 'all':
        types_to_generate = ['web_logs', 'ecommerce', 'metrics', 'app_logs']
    else:
        types_to_generate = [args.type]
    
    for data_type in types_to_generate:
        print(f"Generating {args.count} {data_type} records...")
        
        for _ in range(args.count):
            if data_type == 'web_logs':
                record = generate_web_log_entry()
                record['data_type'] = 'web_log'
            elif data_type == 'ecommerce':
                record = generate_ecommerce_transaction()
                record['total_amount'] = round(record['quantity'] * record['unit_price'], 2)
                record['data_type'] = 'ecommerce'
            elif data_type == 'metrics':
                record = generate_system_metrics()
                record['data_type'] = 'system_metrics'
            elif data_type == 'app_logs':
                record = generate_application_logs()
                record['data_type'] = 'application_log'
            
            data.append(record)
    
    # Sort by timestamp
    data.sort(key=lambda x: x['timestamp'])
    
    # Write to file in Elasticsearch bulk format
    with open(args.output, 'w') as f:
        for record in data:
            # Write the index action
            index_action = {'index': {'_index': 'sample-data'}}
            f.write(json.dumps(index_action) + '\n')
            # Write the document
            f.write(json.dumps(record) + '\n')
    
    print(f"Generated {len(data)} records and saved to {args.output}")
    print(f"To import into Elasticsearch use:")
    os.system(f"curl -X POST 'localhost:9200/sample-data/_bulk' -H 'Content-Type: application/json' --data-binary @{args.output}")

if __name__ == '__main__':
    main()
