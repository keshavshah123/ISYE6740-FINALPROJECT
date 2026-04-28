import pandas as pd

# 1. Load the filtered small manufacturing facilities
facilities_df = pd.read_csv('ECHO_Filtered_Small_Manufacturing.csv')

# 2. Load the enforcement case files using the exact schema columns
case_facilities = pd.read_csv('case_downloads/CASE_FACILITIES.csv', 
                              usecols=['REGISTRY_ID', 'ACTIVITY_ID'], 
                              low_memory=False)

# Using ACTIVITY_STATUS_DATE as our primary temporal marker for the enforcement action
enforcements = pd.read_csv('case_downloads/CASE_ENFORCEMENTS.csv', 
                           usecols=['ACTIVITY_ID', 'ACTIVITY_STATUS_DATE'], 
                           low_memory=False)

# Convert the date column to actual datetime objects for filtering
enforcements['ACTIVITY_STATUS_DATE'] = pd.to_datetime(enforcements['ACTIVITY_STATUS_DATE'], errors='coerce')

# 3. Merge the enforcement dates to the facilities involved
case_dates = case_facilities.merge(enforcements, on='ACTIVITY_ID', how='inner')

# 4. Filter for the Target Prediction Window (Jan 1, 2025 - Dec 31, 2025)
target_window_mask = (case_dates['ACTIVITY_STATUS_DATE'] >= '2025-01-01') & \
                     (case_dates['ACTIVITY_STATUS_DATE'] <= '2025-12-31')

# Get a unique list of REGISTRY_IDs that had an enforcement action in this specific window
violating_facilities = case_dates[target_window_mask]['REGISTRY_ID'].unique()

# 5. Create the Binary Target Variable 
# If the REGISTRY_ID is in our violating_facilities list, they receive a 1 (Violation), else 0 (No Violation)
facilities_df['TARGET_VIOLATION_12M'] = facilities_df['REGISTRY_ID'].isin(violating_facilities).astype(int)

# Check the initial class distribution to compare against your 5-20% estimate
print("Target Variable Distribution:")
print(facilities_df['TARGET_VIOLATION_12M'].value_counts(normalize=True) * 100)

facilities_df.to_csv('ECHO_Dataset_With_Target.csv', index=False)