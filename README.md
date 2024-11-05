# Community battery project
Assessing the feasibility of installing a big community battery.

## Project goals
* Soak up South Australian daytime solar
* Reduce morning/evening grid load
* Encourage local community rooftop solar installation
* Reduce energy inequity

## Documentation
* [How to run a Neighbourhood Battery project](https://www.energy.vic.gov.au/grants/neighbourhood-batteries/how-to-run-a-neighbourhood-battery-project)
* [Community Batteries for Household Solar program](https://www.dcceew.gov.au/energy/renewable/community-batteries)
* [Neighbourhood batteries in Australia: Anticipating questions of value conflict and (in)justice](https://www.researchgate.net/publication/359314754_Neighbourhood_batteries_in_Australia_Anticipating_questions_of_value_conflict_and_injustice)
* [2024 Megapack pricing down 44%](https://www.pv-magazine-australia.com/2024/07/08/tesla-battery-deployment-up-157-megapack-pricing-down-44/)

## Finance
Upfront costs, power costs, and payback time estimates.

### Electricity price
[AEMO dashboard](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/data-nem/data-dashboard-nem) average monthly prices for 2024 in South Australia:
* Low: AUD$32.74/MWh January 2024
* High: AUD$241.22/MWh July 2024
* Average: AUD$78.56/MWh 2024

### Tesla Megapack cost
Upfront cost: 5/11/2024
* [1.9 MW, 3.9 MWh pack](https://www.tesla.com/megapack/design) US$1.03M == ~AUD$1.56M
* Annual maintenance: US$8,830 == ~AUD$13,400
* 92% round trip efficiency

### Payback estimate
Based on 2x manual two-hour Charge/discharge cycles via [Open Electricity](https://explore.openelectricity.org.au/energy/sa1/?range=7d&interval=30m&view=discrete-time&group=Detailed) for October 2024.

**Sell**:
* 6-8am ~AUD$75/MWh = AUD$150
* 6-8pm ~AUD$75/MWh = AUD$150

**Buy**:
* 12-2pm ~AUD$-100/MWh = AUD$200
* 10pm-12am ~AUD$50/MWh = AUD$-100

**Total**:
* ~AUD$400/day == AUD$146,000/year

**Payback time**:
* AUD$1,574,000 / AUD$146,000 = **10.8 years**

#### 2024 data so far
* Source: [AEMO archive](https://visualisations.aemo.com.au/aemo/nemweb/index.html#mms-data-model)
* Download the archived CSVs: [./download.sh](data/download.sh)
* Data directory: [data](data)
* SA1 combined: [trading-price-sa1.csv.zip](data/trading-price-sa1.csv.zip)
* Run the scripts: `make setup` and `make run`

**Output**:

```bash
===========================
Morning and evening sell...
===========================
Daily Profit: 666.927851688655
Annual Profit: 243428.66586635908
Payback Period (years): 10.568156981717602

====================
Evening sell only...
====================
Optimized Buy Hour: 12
Optimized Sell Hour: 18
Daily Profit (Single Buy/Sell): 1405.2969927562633
Annual Profit (Single Buy/Sell): 512933.4023560361
Payback Period (years, Single Buy/Sell): 4.848178468400627
```

#### Hornsdale battery
Payback period was [under 3 years](https://reneweconomy.com.au/tesla-big-battery-recoups-cost-of-construction-in-little-over-two-years-25265/#:~:text=It%20also%20means%20that%20total,began%20operations%20in%20late%202017).

## Hardware
Community battery hardware options:
* [Tesla Megapack](https://www.tesla.com/en_au/megapack)

## Software
Control software options:
* [Tesla Energy Software](https://www.tesla.com/en_au/support/energy/tesla-software)
* Is there a commercial version of the [Tesla Fleet API](https://developer.tesla.com/docs/fleet-api/endpoints/energy)
* [Energy Autopilot](https://energyautopilot.com) when it launches?
