"""Synthetic Bangladesh retail supply-chain data.

Generates two tables:
  * outlet table    - one row per (date, outlet, product) with a 7-day demand target
  * warehouse table - one row per (date, product) for the central warehouse, with
                      optimal_inventory_level and feasible_max_supply targets

Demand is driven by product seasonality, Bangladeshi seasons, Eid / Ramadan,
hartal, monsoon and load-shedding events, region and outlet size.
"""
import argparse
from datetime import datetime

import numpy as np
import pandas as pd


class SupplyChainDataGenerator:
    def __init__(self, start_date="2022-01-01", end_date="2024-12-31"):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        
        self.products = {
            'electronics': {'base_demand': 45, 'volatility': 0.35, 'seasonality': 1.4},
            'clothing': {'base_demand': 75, 'volatility': 0.45, 'seasonality': 1.6},
            'groceries': {'base_demand': 180, 'volatility': 0.25, 'seasonality': 0.9},
            'books': {'base_demand': 25, 'volatility': 0.30, 'seasonality': 1.1},
            'home_goods': {'base_demand': 35, 'volatility': 0.40, 'seasonality': 1.2},
            'sports': {'base_demand': 30, 'volatility': 0.50, 'seasonality': 1.3},
            'beauty': {'base_demand': 40, 'volatility': 0.35, 'seasonality': 1.1},
            'automotive': {'base_demand': 15, 'volatility': 0.25, 'seasonality': 0.8},
            'toys': {'base_demand': 35, 'volatility': 0.55, 'seasonality': 1.8},
            'pharmacy': {'base_demand': 50, 'volatility': 0.20, 'seasonality': 0.9}
        }
        
        self.outlet_types = {
            'shopping_mall': {'size_factor': 2.5, 'product_variety': 0.9},
            'departmental_store': {'size_factor': 1.8, 'product_variety': 0.8},
            'bazaar_shop': {'size_factor': 1.2, 'product_variety': 0.6},
            'neighborhood_shop': {'size_factor': 1.0, 'product_variety': 0.5},
            'village_store': {'size_factor': 0.6, 'product_variety': 0.4}
        }
        
        self.regions = ['dhaka', 'chittagong', 'sylhet', 'rajshahi', 'khulna', 'barisal', 'rangpur', 'mymensingh']
        
        self.bd_events = {
            'eid_ul_fitr': {'probability': 0.02, 'demand_boost': 2.5},
            'eid_ul_adha': {'probability': 0.015, 'demand_boost': 2.0},
            'ramadan': {'probability': 0.08, 'demand_boost': 0.7},
            'hartal': {'probability': 0.03, 'demand_boost': 0.3},
            'heavy_monsoon': {'probability': 0.15, 'demand_boost': 0.6},
            'load_shedding': {'probability': 0.2, 'demand_boost': 0.8}
        }
        
        np.random.seed(42)
    
    def get_bd_season(self, month):
        seasons = {
            (12, 1, 2): 'sheet',
            (3, 4): 'basanta',
            (5, 6): 'grishma',
            (7, 8): 'borsha',
            (9, 10): 'sharat',
            (11,): 'hemanta'
        }
        for months, season in seasons.items():
            if month in months:
                return season
        return 'hemanta'
    
    def generate_seasonal_factor(self, date, product_id):
        day_of_year = date.timetuple().tm_yday
        month = date.month
        base_seasonal = self.products[product_id]['seasonality']
        seasonal = 1 + (base_seasonal - 1) * 0.4 * np.sin(2 * np.pi * day_of_year / 365)
        
        if product_id == 'clothing' and month in [10,11,12,1]:
            seasonal *= 1.4
        elif product_id == 'electronics' and month in [11,12]:
            seasonal *= 1.6
        elif product_id in ['groceries','toys'] and month in [4,11]:
            seasonal *= 1.5
        
        return max(0.3, seasonal)
    
    def _pick_compact_event(self, daily_events):
        event_priority = ['eid_ul_fitr', 'eid_ul_adha', 'ramadan', 'hartal', 'heavy_monsoon', 'load_shedding']
        for event in event_priority:
            if daily_events.get(event):
                if 'eid' in event:
                    return 'eid'
                return event.replace('_', '')
        return 'none'
    
    def generate_outlet_dataset(self, num_outlets=30):
        outlet_data = []
        outlet_types_list = list(self.outlet_types.keys())
        products_list = list(self.products.keys())
        
        outlet_info = {}
        for i in range(num_outlets):
            outlet_id = f"outlet_{i+1:03d}"
            outlet_type = np.random.choice(outlet_types_list)
            region = np.random.choice(self.regions)
            variety_rate = self.outlet_types[outlet_type]['product_variety']
            sells_products = {p for p in products_list if np.random.random() < variety_rate}
            while len(sells_products) < 2:
                sells_products.add(np.random.choice(products_list))
            
            econ = 'high' if region in ['dhaka','chittagong'] else 'medium' if region in ['sylhet','rajshahi'] else 'low'
            outlet_info[outlet_id] = {
                'outlet_type': outlet_type,
                'region': region,
                'economic_zone': econ,
                'sells_products': sells_products
            }
        
        region_factors = {
            'dhaka': 1.5, 'chittagong': 1.3, 'sylhet': 1.1, 'rajshahi': 1.0,
            'khulna': 0.9, 'barisal': 0.8, 'rangpur': 0.8, 'mymensingh': 0.8
        }
        
        for date in self.date_range:
            daily_events = {ev: (1 if np.random.random() < cfg['probability'] else 0) 
                            for ev, cfg in self.bd_events.items()}
            event_label = self._pick_compact_event(daily_events)
            
            day_of_week = date.weekday()
            is_weekend = int(day_of_week in [4, 5])
            bd_season = self.get_bd_season(date.month)
            
            for outlet_id, info in outlet_info.items():
                outlet_type = info['outlet_type']
                region = info['region']
                econ = info['economic_zone']
                sells_products = info['sells_products']
                size_factor = self.outlet_types[outlet_type]['size_factor']
                region_factor = region_factors.get(region, 1.0)
                
                for product_id in products_list:
                    if product_id in sells_products:
                        base_demand = self.products[product_id]['base_demand']
                        volatility = self.products[product_id]['volatility']
                        seasonal_factor = self.generate_seasonal_factor(date, product_id)
                        
                        event_factor = 1.0
                        if event_label == 'eid' and product_id in ['clothing','toys','electronics']:
                            event_factor = 2.0
                        elif event_label == 'ramadan' and product_id == 'groceries':
                            event_factor = 1.4
                        elif event_label == 'hartal':
                            event_factor = 0.4
                        elif event_label in ['heavymonsoon', 'monsoon']:
                            event_factor = 0.7
                        elif event_label in ['loadshedding', 'shedding']:
                            event_factor = 0.8
                        
                        weekend_factor = 1.4 if is_weekend else 1.0
                        
                        weekly_demand = (base_demand * size_factor * region_factor * seasonal_factor *
                                         event_factor * weekend_factor * 7 * np.random.normal(1, volatility))
                        weekly_demand = max(0, int(weekly_demand))
                    else:
                        weekly_demand = 0
                    
                    outlet_category = f"{outlet_type}_{econ}"
                    
                    outlet_data.append({
                        'date': date,
                        'outlet_id': outlet_id,
                        'product_id': product_id,
                        'outlet_category': outlet_category,
                        'region': region,
                        'bd_season': bd_season,
                        'is_weekend': is_weekend,
                        'event': event_label,
                        'economic_zone': econ,
                        'next_7_days_demand': weekly_demand
                    })
        
        df = pd.DataFrame(outlet_data)
        for c in ['outlet_category', 'region', 'bd_season', 'event', 'economic_zone', 'product_id']:
            df[c] = df[c].astype('category')
        return df

    def generate_warehouse_dataset(self, outlet_df):
        warehouse_data = []
        products_list = list(self.products.keys())
        inventory_levels = {prod: np.random.randint(8000, 20000) for prod in products_list}
        reliability_map = {'high': 1.2, 'medium': 1.0, 'low': 0.7}
        
        for date in self.date_range:
            daily_outlet_data = outlet_df[outlet_df['date'] == date]
            daily_events = {ev: (1 if np.random.random() < cfg['probability'] else 0) 
                            for ev, cfg in self.bd_events.items()}
            event_label = self._pick_compact_event(daily_events)
            
            is_weekend = int(date.weekday() in [4, 5])
            bd_season = self.get_bd_season(date.month)
            
            for product_id in products_list:
                product_data = daily_outlet_data[daily_outlet_data['product_id'] == product_id]
                expected_7_day_demand = int(product_data['next_7_days_demand'].sum()) if not product_data.empty else 0
                
                current_inventory = inventory_levels[product_id]
                
                inbound = 0
                shipment_prob = 0.25
                if daily_events.get('hartal'):
                    shipment_prob *= 0.1
                if daily_events.get('heavy_monsoon'):
                    shipment_prob *= 0.3
                if is_weekend:
                    shipment_prob *= 0.6
                    
                if np.random.random() < shipment_prob:
                    inbound = int(expected_7_day_demand * np.random.uniform(3, 7))
                
                new_inventory = max(0, current_inventory + inbound)
                inventory_levels[product_id] = new_inventory
                
                safety_stock = expected_7_day_demand * 0.5
                optimal_inventory = int(expected_7_day_demand + safety_stock)
                max_storage_capacity = np.random.randint(20000, 50000)
                
                supplier_reliability = np.random.choice(['high','medium','low'])
                supplier_capacity_index = round(np.random.uniform(0.7, 1.5), 2)
                supplier_lead_time = np.random.randint(2, 14)
                allocation_ratio = round(np.random.uniform(0.3, 1.0), 2)
                
                disruption_index = 1.0
                if event_label == 'hartal':
                    disruption_index *= 0.5
                elif event_label in ['heavymonsoon', 'monsoon']:
                    disruption_index *= 0.7
                elif event_label in ['loadshedding', 'shedding']:
                    disruption_index *= 0.85
                disruption_index *= round(np.random.uniform(0.85, 1.05), 3)
                
                supplier_reliability_val = reliability_map[supplier_reliability]
                transport_cost_index = round(np.random.uniform(0.8, 1.5) * (1.0 + (1 - disruption_index) * 0.2), 3)
                
                buffer_factor = 1.1 if supplier_reliability == 'high' else 1.0
                raw_feasible = int(expected_7_day_demand * supplier_capacity_index * allocation_ratio * 
                                 supplier_reliability_val * buffer_factor * disruption_index)
                feasible_max_supply = max(0, min(max_storage_capacity, raw_feasible))
                
                if expected_7_day_demand == 0:
                    feasible_max_supply = int(min(max_storage_capacity, supplier_capacity_index * allocation_ratio * 1000 * disruption_index))
                
                warehouse_data.append({
                    'date': date,
                    'product_id': product_id,
                    'bd_season': bd_season,
                    'is_weekend': is_weekend,
                    'event': event_label,
                    'current_inventory': current_inventory,
                    'inbound_shipment': inbound,
                    'supplier_reliability': supplier_reliability,
                    'supplier_capacity_index': supplier_capacity_index,
                    'supplier_lead_time': supplier_lead_time,
                    'allocation_ratio': allocation_ratio,
                    'disruption_index': round(disruption_index, 3),
                    'transport_cost_index': transport_cost_index,
                    'max_storage_capacity': max_storage_capacity,
                    'optimal_inventory_level': optimal_inventory,
                    'feasible_max_supply': int(feasible_max_supply)
                })
        
        df = pd.DataFrame(warehouse_data)
        for c in ['product_id', 'bd_season', 'event', 'supplier_reliability']:
            df[c] = df[c].astype('category')
        return df

    def generate_datasets(self, num_outlets=30):
        outlet_df = self.generate_outlet_dataset(num_outlets)
        warehouse_df = self.generate_warehouse_dataset(outlet_df)
        return outlet_df, warehouse_df


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start", default="2022-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--outlets", type=int, default=30)
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    generator = SupplyChainDataGenerator(args.start, args.end)
    outlet_df, warehouse_df = generator.generate_datasets(num_outlets=args.outlets)

    outlet_df.to_csv(f"{args.out_dir}/bd_outlet_compact.csv", index=False)
    warehouse_df.to_csv(f"{args.out_dir}/bd_warehouse_central.csv", index=False)
    print(f"outlet rows: {len(outlet_df):,}  warehouse rows: {len(warehouse_df):,}")


if __name__ == "__main__":
    main()
