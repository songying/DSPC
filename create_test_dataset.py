import sqlite3
import json
import datetime
import uuid
import os

os.makedirs("dataset_files", exist_ok=True)

sample_file_path = "dataset_files/sample_browser_history.txt"
with open(sample_file_path, "w") as f:
    f.write("user_id,timestamp,url,duration\n")
    for i in range(100):
        f.write(f"user{i},2023-04-15T12:00:00,https://example.com/page{i},{i*10}\n")

conn = sqlite3.connect('privacy_data.db')
cursor = conn.cursor()

dataset = {
    'name': 'Browser History Dataset',
    'description': 'Sample dataset containing browser history of 1,000,000 users',
    'price': 0.5,
    'owner': '0x1234567890abcdef1234567890abcdef12345678',
    'privacy_options': json.dumps(['Homomorphic Computing', 'ZK Proof']),
    'file_path': sample_file_path,
    'file_size': '25.5 MB',
    'records': 1000000,
    'category': 'Browser History',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': datetime.datetime.now().isoformat(),
    'contract_address': '0x' + uuid.uuid4().hex[:40]
}

cursor.execute('''
INSERT INTO datasets 
(name, description, price, owner, privacy_options, file_path, file_size, records, category, created_at, updated_at, contract_address)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    dataset['name'], dataset['description'], dataset['price'], dataset['owner'], 
    dataset['privacy_options'], dataset['file_path'], dataset['file_size'], dataset['records'], 
    dataset['category'], dataset['created_at'], dataset['updated_at'], dataset['contract_address']
))

dataset2 = {
    'name': 'E-commerce Behavior Dataset',
    'description': 'Shopping patterns and behaviors of online customers',
    'price': 0.75,
    'owner': '0x1234567890abcdef1234567890abcdef12345678',
    'privacy_options': json.dumps(['Homomorphic Computing', '3rd-Party computing']),
    'file_path': 'dataset_files/ecommerce_sample.txt',
    'file_size': '42.1 MB',
    'records': 750000,
    'category': 'E-commerce',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': datetime.datetime.now().isoformat(),
    'contract_address': '0x' + uuid.uuid4().hex[:40]
}

with open(dataset2['file_path'], "w") as f:
    f.write("customer_id,product_id,timestamp,action,price\n")
    for i in range(100):
        f.write(f"cust{i},prod{i*2},2023-04-15T14:30:00,view,{i*5.99}\n")

cursor.execute('''
INSERT INTO datasets 
(name, description, price, owner, privacy_options, file_path, file_size, records, category, created_at, updated_at, contract_address)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    dataset2['name'], dataset2['description'], dataset2['price'], dataset2['owner'], 
    dataset2['privacy_options'], dataset2['file_path'], dataset2['file_size'], dataset2['records'], 
    dataset2['category'], dataset2['created_at'], dataset2['updated_at'], dataset2['contract_address']
))

conn.commit()
conn.close()

print('Test datasets created successfully')
