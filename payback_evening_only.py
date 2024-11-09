import pandas as pd

# Load the CSV file
file_path = 'data/trading-price-sa1.csv'
data = pd.read_csv(file_path, low_memory=False)

# Convert SETTLEMENTDATE to datetime for easier filtering by time
data['SETTLEMENTDATE'] = pd.to_datetime(data['SETTLEMENTDATE'], errors='coerce')

# Drop any rows where SETTLEMENTDATE or RRP might be missing due to conversion issues
data = data[['SETTLEMENTDATE', 'RRP']].dropna()
data['RRP'] = pd.to_numeric(data['RRP'], errors='coerce')
data = data.dropna()  # Drop any rows where RRP could not be converted

# Define the full capacity for a single transaction in MWh
energy_per_session_single = 3.9

# Cost of a Tesla Megapack
megapack_cost = 2414070  # in AUD

# Estimated annual maintenance cost
annual_maintenance_cost = 15000  # in AUD

# Group by hour to find the average RRP per hour across the dataset
data['hour'] = data['SETTLEMENTDATE'].dt.hour
hourly_prices = data.groupby(data['hour'])['RRP'].mean()

# Sort to identify the optimal hours for buying (lowest price) and selling (highest price)
lowest_price_hours = hourly_prices.nsmallest(1).index.tolist()  # Lowest price hour for buying
highest_price_hours = hourly_prices.nlargest(1).index.tolist()  # Highest price hour for selling

# Calculate the profit based on a single buy and single sell session with optimized times
# Buy session at the lowest price hour
buy_data_single = data[data['hour'] == lowest_price_hours[0]]
daily_buy_cost_single = buy_data_single['RRP'].mean() * energy_per_session_single

# Sell session at the highest price hour
sell_data_single = data[data['hour'] == highest_price_hours[0]]
daily_sell_revenue_single = sell_data_single['RRP'].mean() * energy_per_session_single

# Calculate total daily profit with single buy/sell optimized times
daily_profit_single = daily_sell_revenue_single - daily_buy_cost_single

# Calculate annual profit and payback period based on single daily profit
annual_profit_single = daily_profit_single * 365  # Annual profit
net_annual_profit_single = annual_profit_single - annual_maintenance_cost  # Net profit after maintenance
payback_period_single = megapack_cost / net_annual_profit_single

# Print the optimized results for the single buy/sell scenario
print("====================")
print("Evening sell only...")
print("====================")
print("Optimized Buy Hour:", lowest_price_hours[0])
print("Optimized Sell Hour:", highest_price_hours[0])
print("Daily Profit (Single Buy/Sell):", daily_profit_single)
print("Annual Profit (Single Buy/Sell):", annual_profit_single)
print("Payback Period (years, Single Buy/Sell):", payback_period_single)
print("\n")
