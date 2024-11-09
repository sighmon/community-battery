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
# Buy session at the lowest price hour (midday)
buy_data_single = data[data['hour'] == lowest_price_hours[0]]
daily_buy_cost_single = buy_data_single['RRP'].mean() * energy_per_session_single

# Sell session at the highest price hour (evening)
sell_data_single = data[data['hour'] == highest_price_hours[0]]
daily_sell_revenue_single = sell_data_single['RRP'].mean() * energy_per_session_single

# Define the overnight buy session (12 AM - 6 AM) and set the buy threshold
overnight_buy_data = data[(data['hour'] >= 0) & (data['hour'] < 6)]
overnight_buy_price = overnight_buy_data['RRP'].mean()
buy_threshold = 100  # Price threshold in AUD/MWh (10c/kWh)

# Check if overnight buy price is below the threshold
overnight_charge = False
overnight_buy_cost = 0

if overnight_buy_price < buy_threshold:
    # Buy at the overnight price using 3.9 MWh
    overnight_buy_cost = overnight_buy_price * energy_per_session_single
    overnight_charge = True

# Define the morning sell session (6-8 AM)
morning_sell_data = data[(data['hour'] >= 6) & (data['hour'] < 8)]
morning_sell_price = morning_sell_data['RRP'].mean()

# Calculate the morning sell revenue only if the battery was charged overnight
morning_sell_revenue = 0
if overnight_charge:
    morning_sell_revenue = morning_sell_price * energy_per_session_single

# Calculate the profit from the morning session (if applicable)
morning_profit = morning_sell_revenue - overnight_buy_cost if overnight_charge else 0

# Calculate total daily profit including the optional morning sell session
total_daily_revenue = daily_sell_revenue_single + morning_sell_revenue
total_daily_profit = total_daily_revenue - (daily_buy_cost_single + overnight_buy_cost)

# Calculate the updated annual profit and payback period
annual_profit_updated = total_daily_profit * 365
net_annual_profit_updated = annual_profit_updated - annual_maintenance_cost
payback_period_updated = megapack_cost / net_annual_profit_updated

# Print the results including the new overnight charging logic
print("=========================================================================")
print("Evening sell, and morning if the price overnight is less than $100/MWh...")
print("=========================================================================")
print("Optimized Buy Hour (Midday):", lowest_price_hours[0])
print("Optimized Sell Hour (Evening):", highest_price_hours[0])
print("Overnight Charging:", overnight_charge)
print("Daily Profit (Including Morning Sell):", total_daily_profit)
print("Annual Profit:", annual_profit_updated)
print("Payback Period (years):", payback_period_updated)
print("\n")
