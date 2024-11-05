import pandas as pd

# Load the CSV file
file_path = 'data/trading-price-sa1.csv'
data = pd.read_csv(file_path)

# Convert SETTLEMENTDATE to datetime for easier filtering by time
data['SETTLEMENTDATE'] = pd.to_datetime(data['SETTLEMENTDATE'], errors='coerce')

# Drop any rows where SETTLEMENTDATE or RRP might be missing due to conversion issues
data = data[['SETTLEMENTDATE', 'RRP']].dropna()
data['RRP'] = pd.to_numeric(data['RRP'], errors='coerce')
data = data.dropna()  # Drop any rows where RRP could not be converted

# Define energy to be traded per session in MWh
energy_per_session = 2

# Filter data by specific buy and sell time ranges
data['hour'] = data['SETTLEMENTDATE'].dt.hour
data['date'] = data['SETTLEMENTDATE'].dt.date

# Buy sessions: 12-2 PM, 10 PM-12 AM
buy_data_session1 = data[(data['hour'] >= 12) & (data['hour'] < 14)]
buy_data_session2 = data[(data['hour'] >= 22) & (data['hour'] < 24)]
daily_buy_cost = (buy_data_session1['RRP'].mean() + buy_data_session2['RRP'].mean()) * energy_per_session

# Sell sessions: 6-8 AM, 6-8 PM
sell_data_session1 = data[(data['hour'] >= 6) & (data['hour'] < 8)]
sell_data_session2 = data[(data['hour'] >= 18) & (data['hour'] < 20)]
daily_sell_revenue = (sell_data_session1['RRP'].mean() + sell_data_session2['RRP'].mean()) * energy_per_session

# Calculate total daily profit
daily_profit_adjusted = daily_sell_revenue - daily_buy_cost

# Calculate annual profit based on the adjusted daily profit
annual_profit_adjusted = daily_profit_adjusted * 365  # Annual profit
annual_maintenance_cost = 15000  # Estimated annual maintenance cost
net_annual_profit_adjusted = annual_profit_adjusted - annual_maintenance_cost  # Net profit after maintenance

# Cost of a Tesla Megapack
megapack_cost = 2414070

# Calculate payback period in years
payback_period_adjusted = megapack_cost / net_annual_profit_adjusted

# Print the results
print("===========================")
print("Morning and evening sell...")
print("===========================")
print("Daily Profit:", daily_profit_adjusted)
print("Annual Profit:", annual_profit_adjusted)
print("Payback Period (years):", payback_period_adjusted)
print("\n")
