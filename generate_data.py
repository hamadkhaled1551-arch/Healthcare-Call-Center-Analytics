import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import urllib
from sqlalchemy import create_engine

# 1. Database Connection Setup
server_name = '.' 
database_name = 'CallCenterDB' # Ensure this database exists in SSMS

params = urllib.parse.quote_plus(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;TrustServerCertificate=yes;')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
print("Successfully connected to SQL Server!")

# 2. Data Generation
np.random.seed(42)
num_records = 50000

start_date = datetime.now() - timedelta(days=180)
dates = [start_date + timedelta(minutes=int(x)) for x in np.random.randint(0, 180*24*60, num_records)]
dates.sort()

call_types = ['Consultation', 'Complaint', 'Appointment Booking', 'Emergency', 'General Inquiry']
call_probabilities = [0.4, 0.1, 0.3, 0.05, 0.15]
types = np.random.choice(call_types, num_records, p=call_probabilities)

wait_times = np.random.gamma(shape=2, scale=15, size=num_records).astype(int) 
talk_times = np.random.gamma(shape=3, scale=80, size=num_records).astype(int)

statuses = np.random.choice(['Answered', 'Abandoned'], num_records, p=[0.85, 0.15])

wait_times = np.where(statuses == 'Abandoned', np.random.gamma(shape=3, scale=30, size=num_records).astype(int), wait_times)
talk_times = np.where(statuses == 'Abandoned', 0, talk_times)

agents = [f'Agent {i:02d}' for i in range(1, 26)]
assigned_agents = np.where(statuses == 'Answered', np.random.choice(agents, num_records), 'None')

df_calls = pd.DataFrame({
    'Call_ID': range(100001, 100001 + num_records),
    'Call_Timestamp': dates,
    'Call_Type': types,
    'Call_Status': statuses,
    'Wait_Time_Sec': wait_times,
    'Talk_Time_Sec': talk_times,
    'Agent_Name': assigned_agents
})

# 3. Upload to SQL Server
print("Loading table to the database...")

df_calls.to_sql('Calls', con=engine, if_exists='replace', index=False)

print("All data loaded successfully!")