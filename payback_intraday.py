import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'data/trading-price-sa1.csv'
data = pd.read_csv(file_path, low_memory=False)

# Convert SETTLEMENTDATE to datetime for easier filtering by time
data['SETTLEMENTDATE'] = pd.to_datetime(data['SETTLEMENTDATE'], errors='coerce')

# Drop any rows where SETTLEMENTDATE or RRP might be missing due to conversion issues
data = data[['SETTLEMENTDATE', 'RRP']].dropna()
data['RRP'] = pd.to_numeric(data['RRP'], errors='coerce')
data = data.dropna()

# Define parameters
energy_per_session_single = 3.9
megapack_cost = 2414070  # in AUD
annual_maintenance_cost = 15000  # in AUD
buy_threshold = 100  # Price threshold in AUD/MWh (10c/kWh)
sell_threshold = 150  # Sell threshold in AUD/MWh

# Extract hour and date from SETTLEMENTDATE
data['hour'] = data['SETTLEMENTDATE'].dt.hour
data['date'] = data['SETTLEMENTDATE'].dt.date

# Group by date for the fixed-threshold strategy
overnight_prices = data[(data['hour'] >= 0) & (data['hour'] < 6)].groupby('date')['RRP'].mean()
morning_prices = data[(data['hour'] >= 6) & (data['hour'] < 8)].groupby('date')['RRP'].mean()
midday_prices = data[data['hour'] == 12].groupby('date')['RRP'].mean()
evening_prices = data[data['hour'] == 18].groupby('date')['RRP'].mean()

# Align the data by merging grouped results
overnight_df = overnight_prices.to_frame(name='Overnight Price').reset_index()
morning_df = morning_prices.to_frame(name='Morning Price').reset_index()
midday_df = midday_prices.to_frame(name='Midday Price').reset_index()
evening_df = evening_prices.to_frame(name='Evening Price').reset_index()

# Merge all dataframes on the 'date' column
merged_df = overnight_df.merge(morning_df, on='date', how='inner') \
                        .merge(midday_df, on='date', how='inner') \
                        .merge(evening_df, on='date', how='inner')

# Calculate overnight buy costs
merged_df['Overnight Buy Cost'] = np.where(merged_df['Overnight Price'] < buy_threshold,
                                           merged_df['Overnight Price'] * energy_per_session_single, 0)

# Calculate morning sell revenue if overnight charging occurred
merged_df['Morning Sell Revenue'] = np.where(merged_df['Overnight Buy Cost'] > 0,
                                             merged_df['Morning Price'] * energy_per_session_single, 0)

# Calculate midday buy costs and evening sell revenue
merged_df['Midday Buy Cost'] = merged_df['Midday Price'] * energy_per_session_single
merged_df['Evening Sell Revenue'] = merged_df['Evening Price'] * energy_per_session_single

# Calculate total daily profit for the fixed-threshold strategy
merged_df['Daily Profit'] = (merged_df['Evening Sell Revenue'] + merged_df['Morning Sell Revenue']) - \
                            (merged_df['Midday Buy Cost'] + merged_df['Overnight Buy Cost'])

# Intraday Arbitrage Strategy
# Enhanced Intraday Arbitrage Strategy with Detailed Logging

# Define parameters for logging
intraday_buy_percentile = 10
intraday_sell_percentile = 90
battery_state = 0
battery_capacity = 3.9
total_intraday_profit = 0
intraday_daily_profits = []

# Initialize lists for logging details
buy_log = []
sell_log = []
daily_summary_log = []

# Group data by date for intraday analysis
dates = data['date'].unique()

for date in dates:
    daily_data = data[data['date'] == date]
    buy_threshold = np.percentile(daily_data['RRP'], intraday_buy_percentile)
    sell_threshold = np.percentile(daily_data['RRP'], intraday_sell_percentile)
    daily_profit = 0
    total_buy_amount = 0
    total_sell_amount = 0
    total_buy_cost = 0
    total_sell_revenue = 0

    # print(f"\nProcessing date: {date}")
    # print(f"Buy Threshold: {buy_threshold:.2f}, Sell Threshold: {sell_threshold:.2f}")

    # Iterate over the intraday price data
    for price in daily_data['RRP']:
        # Buy if the price is below the buy threshold and battery is not full
        if price < buy_threshold and battery_state < battery_capacity:
            buy_amount = min(battery_capacity - battery_state, battery_capacity / 5)
            buy_cost = price * buy_amount
            battery_state += buy_amount
            daily_profit -= buy_cost
            total_buy_amount += buy_amount
            total_buy_cost += buy_cost
            buy_log.append(f"Buy at {price:.2f} AUD/MWh, Amount: {buy_amount:.2f} MWh, Battery State: {battery_state:.2f} MWh")

        # Sell if the price is above the sell threshold and battery is not empty
        if price > sell_threshold and battery_state > 0:
            sell_amount = min(battery_state, battery_capacity / 5)
            sell_revenue = price * sell_amount
            battery_state -= sell_amount
            daily_profit += sell_revenue
            total_sell_amount += sell_amount
            total_sell_revenue += sell_revenue
            sell_log.append(f"Sell at {price:.2f} AUD/MWh, Amount: {sell_amount:.2f} MWh, Battery State: {battery_state:.2f} MWh")

    # Log the daily summary
    daily_summary_log.append(
        f"Date: {date}, Total Buy: {total_buy_amount:.2f} MWh, Total Buy Cost: {total_buy_cost:.2f} AUD, "
        f"Total Sell: {total_sell_amount:.2f} MWh, Total Sell Revenue: {total_sell_revenue:.2f} AUD, "
        f"Daily Profit: {daily_profit:.2f} AUD"
    )

    intraday_daily_profits.append(daily_profit)
    total_intraday_profit += daily_profit

# Calculate annual profit and payback period for the intraday arbitrage strategy
annual_profit_intraday = total_intraday_profit * 365 / len(dates)
net_annual_profit_intraday = annual_profit_intraday - annual_maintenance_cost
payback_period_intraday = megapack_cost / net_annual_profit_intraday

# Output the detailed logs
print("\nBuy Actions Log (first 10):")
for log in buy_log[:10]:  # Display the first 10 buy actions for brevity
    print(log)

print("\nSell Actions Log (first 10):")
for log in sell_log[:10]:  # Display the first 10 sell actions for brevity
    print(log)

print("\nDaily Summary Log (first 10):")
for log in daily_summary_log[:10]:  # Display the first 10 daily summaries for brevity
    print(log)

# Create a DataFrame for intraday daily profits
intraday_profit_df = pd.DataFrame({
    'Date': pd.to_datetime(dates),
    'Daily Profit': intraday_daily_profits
})

# Plot the daily profit for the intraday arbitrage strategy
plt.figure(figsize=(12, 6))
plt.plot(intraday_profit_df['Date'], intraday_profit_df['Daily Profit'], label='Intraday Daily Profit', color='green')
plt.xlabel('Date')
plt.ylabel('Profit (AUD)')
plt.title('Daily Profit Using Intraday Arbitrage Strategy')
plt.legend()
plt.grid()
plt.show()

# Output the results of the intraday arbitrage strategy
print("====================================")
print("Intraday Arbitrage Strategy Results:")
print("====================================")
print(f"Total Profit: ${total_intraday_profit:.2f}")
print(f"Annual Profit: ${annual_profit_intraday:.2f}")
print(f"Payback Period: {payback_period_intraday:.2f} years")
