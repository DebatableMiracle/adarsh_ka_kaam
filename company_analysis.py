
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load Data
file_path = 'shipment_booking_data_2021_2025.csv'
try:
    df = pd.read_csv(file_path)
    df['booking_date'] = pd.to_datetime(df['booking_date'])
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

print("Data Loaded. Shape:", df.shape)

# 1. Inter-Booking Gap Analysis
print("\n--- Inter-Booking Gap Analysis ---")
df_sorted = df.sort_values(['company_name', 'booking_date'])
df_sorted['prev_booking_date'] = df_sorted.groupby('company_name')['booking_date'].shift(1)
df_sorted['days_gap'] = (df_sorted['booking_date'] - df_sorted['prev_booking_date']).dt.days

# Remove NaNs (first booking) and 0 days gap (multiple bookings same day - irrelevant for periodicity)
# Actually, 0 days gap is fine, it means multiple bookings per day. But for periodicity we usually care about days *between* active days.
# Let's keep 0 for now as it indicates high frequency.
gaps = df_sorted.dropna(subset=['days_gap'])

avg_gaps = gaps.groupby('company_name')['days_gap'].agg(['mean', 'median', 'std', 'max'])
print(avg_gaps)

# Visualize Gaps for Top Companies
top_companies = df['company_name'].value_counts().nlargest(5).index
plt.figure(figsize=(12, 6))
for company in top_companies:
    company_gaps = gaps[gaps['company_name'] == company]['days_gap']
    # Filter extreme outliers for visualization if needed, but KDE handles it okay usually
    sns.kdeplot(company_gaps, label=company, clip=(0, 30)) # Clip to 0-30 days to see immediate patterns

plt.title('Distribution of Days Between Bookings (Top 5 Companies)')
plt.xlabel('Days Gap')
plt.xlim(0, 15) # Zoom in on the first two weeks
plt.legend()
plt.savefig('booking_gaps_kde.png')
print("Saved booking_gaps_kde.png")


# 2. Shipment Type Transition Matrix
print("\n--- Shipment Type Transition Matrix ---")
# Determine next shipment type per company
df_sorted['next_shipment_type'] = df_sorted.groupby('company_name')['shipment_type'].shift(-1)

# Filter out last booking per company
transitions = df_sorted.dropna(subset=['next_shipment_type'])

# Create crosstab (transition matrix)
transition_matrix = pd.crosstab(transitions['shipment_type'], transitions['next_shipment_type'], normalize='index')
print("Transition Probabilities (Row = Current, Col = Next):")
print(transition_matrix)

plt.figure(figsize=(10, 8))
sns.heatmap(transition_matrix, annot=True, fmt=".2f", cmap="YlGnBu")
plt.title('Shipment Type Transition Probabilities')
plt.ylabel('Current Shipment Type')
plt.xlabel('Next Shipment Type')
plt.savefig('transition_matrix.png')
print("Saved transition_matrix.png")

# 3. Time-Based Transition? (Day of Week dependent?)
# Maybe certain companies ship Air on Fridays?
df_sorted['day_of_week'] = df_sorted['booking_date'].dt.day_name()
print("\n--- Shipment Type by Day of Week (Top 3 Companies) ---")
for company in top_companies[:3]:
    print(f"\n{company}:")
    print(pd.crosstab(df_sorted[df_sorted['company_name']==company]['day_of_week'], 
                      df_sorted[df_sorted['company_name']==company]['shipment_type'], 
                      normalize='index').round(2))
