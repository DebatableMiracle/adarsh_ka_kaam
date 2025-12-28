import pandas as pd

# Load data
file_path = '/home/anubhav/development/adarsh_ka_kaam/shipment_booking_data_2021_2025.csv'
try:
    df = pd.read_csv(file_path)
    print("Dataset Loaded Successfully")
    print("-" * 30)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

# Initial Inspection
print("Shape:", df.shape)
print("\nColumns and Types:\n")
print(df.dtypes)
print("\nFirst 5 rows:\n")
print(df.head())

# Missing Values
print("\nMissing Values:\n")
print(df.isnull().sum())

# Duplicates
print(f"\nDuplicates: {df.duplicated().sum()}")

# Date Conversion and Analysis
try:
    df['booking_date'] = pd.to_datetime(df['booking_date'])
    print("\nDate Conversion Successful")
    print(f"Date Range: {df['booking_date'].min()} to {df['booking_date'].max()}")
except Exception as e:
    print(f"\nDate Conversion Failed: {e}")

# Categorical Analysis
print("\nUnique Companies:", df['company_name'].nunique())
print("Unique Shipment Types:", df['shipment_type'].nunique())

print("\nValue Counts for Companies:\n")
print(df['company_name'].value_counts())

print("\nValue Counts for Shipment Types:\n")
print(df['shipment_type'].value_counts())

# Temporal check (gaps)
daily_counts = df.groupby('booking_date').size()
print("\nDaily Booking Stats:\n")
print(daily_counts.describe())

# Check for anomalies in dates
print("\nChecking for future dates (assuming 'current' is end of 2025):")
future_dates = df[df['booking_date'] > '2025-12-31']
if not future_dates.empty:
    print(f"Found {len(future_dates)} records after 2025-12-31")
else:
    print("No dates after 2025-12-31")

print("\nChecking for date gaps per company:")
for company in df['company_name'].unique():
    company_df = df[df['company_name'] == company].sort_values('booking_date')
    dates = company_df['booking_date'].unique()
    date_range = pd.date_range(start=dates.min(), end=dates.max())
    missing_dates = date_range.difference(dates)
    if len(missing_dates) > 0:
        print(f"Company {company} has {len(missing_dates)} missing dates.")
    else:
        print(f"Company {company} has continuous daily bookings from {dates.min().date()} to {dates.max().date()}.")
