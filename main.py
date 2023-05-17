import speedtest
import logging
import sqlite3
import os
from sqlite3 import Error

script_dir = os.path.dirname(os.path.abspath(__file__))

# Use the script directory to set up logging
log_filename = os.path.join(script_dir, 'logfile.log')
logging.basicConfig(filename=log_filename, level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

# Flattening the dictionary
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


# Creating a connection to the database
def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('speed.db')
        print(f'successful connection with sqlite version {sqlite3.version}')
    except Error as e:
        logging.error(e)
    return conn


# Creating a table
def create_table(conn):
    try:
        query = '''CREATE TABLE IF NOT EXISTS speed (
                        download REAL,
                        upload REAL,
                        ping REAL,
                        server_url TEXT,
                        server_lat TEXT,
                        server_lon TEXT,
                        server_name TEXT,
                        server_country TEXT,
                        server_cc TEXT,
                        server_sponsor TEXT,
                        server_id TEXT,
                        server_host TEXT,
                        server_d REAL,
                        server_latency REAL,
                        timestamp TEXT,
                        bytes_sent INTEGER,
                        bytes_received INTEGER,
                        share TEXT,
                        client_ip TEXT,
                        client_lat TEXT,
                        client_lon TEXT,
                        client_isp TEXT,
                        client_isprating TEXT,
                        client_rating TEXT,
                        client_ispdlavg TEXT,
                        client_ispulavg TEXT,
                        client_loggedin TEXT,
                        client_country TEXT
                    );'''
        conn.execute(query)
        print("Table created successfully")
    except Error as e:
        logging.error(e)


# Inserting data into the table
def insert_into_table(conn, data):
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        query = f'INSERT INTO speed ({columns}) VALUES ({placeholders})'
        conn.execute(query, list(data.values()))
        conn.commit()
        print("Data inserted successfully")
    except Error as e:
        logging.error(e)


# Can be used to test against a specific server
servers = []

threads = None

s = speedtest.Speedtest()
s.get_servers(servers)
s.get_best_server()
s.download(threads=threads)
s.upload(threads=threads)
s.results.share()

results_dict = s.results.dict()

# Flatten the data
flat_data = flatten_dict(results_dict)
# Create connection
conn = create_connection()

if conn:
    # Create table
    create_table(conn)

    # Insert data into table
    insert_into_table(conn, flat_data)

    # Close the connection
    conn.close()
