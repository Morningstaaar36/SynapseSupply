import pandas as pd

from db.connect import get_db


def fetch_all_rows(table_name="outlets", columns="*", batch_size=1000):
    supabase = get_db()
    all_rows = []
    start = 0
    while True:
        response = (
            supabase.table(table_name)
            .select(columns)
            .range(start, start + batch_size - 1)
            .execute()
        )
        data = response.data
        if not data:
            break
        all_rows.extend(data)
        start += batch_size
    print(f"Fetched {len(all_rows)} rows from {table_name}")
    return pd.DataFrame(all_rows)


def export_outlets_csv(csv_path="bd_outlet_extended.csv"):
    allocation_requests_df = fetch_all_rows("allocation_requests")
    allocation_items_df = fetch_all_rows("allocation_request_items")
    outlets_df = fetch_all_rows("outlets")

    df = allocation_items_df.merge(allocation_requests_df, left_on="request_id", right_on="request_id", how="left")
    df = df.merge(outlets_df, left_on="outlet_id", right_on="outlet_id", how="left")

    df = df[[
        "request_date", "outlet_id", "product_id", "outlet_category", "region",
        "bd_season", "is_weekend", "event", "economic_zone", "next_7_days_demand"
    ]]
    df.rename(columns={"request_date": "date"}, inplace=True)

    df.to_csv(csv_path, index=False)
    print(f"Exported Outlets CSV: {csv_path}")


def export_warehouses_csv(csv_path="bd_warehouse_extended.csv"):
    warehouse_snapshots_df = fetch_all_rows("warehouse_snapshots")
    warehouses_df = fetch_all_rows("warehouses")

    # Merge dynamic + static warehouse info
    df = warehouse_snapshots_df.merge(warehouses_df, on="warehouse_id", how="left")

    df = df[[
        "date", "region", "warehouse_id", "product_id", "bd_season", "is_weekend",
        "event", "current_inventory", "inbound_shipment",
        "supplier_reliability", "supplier_capacity_index", "supplier_lead_time",
        "disruption_index", "transport_cost_index", "transport_capacity_factor",
        "max_storage_capacity", "optimal_inventory_level", "feasible_max_supply"
    ]]
    df.to_csv(csv_path, index=False)
    print(f"Exported Warehouse CSV: {csv_path}")

def insert_rows(table_name, rows):
    if not rows:
        print("No rows to insert.")
        return []
    if isinstance(rows, dict):
        rows = [rows]

    response = get_db().table(table_name).insert(rows).execute()
    print(f"Inserted {len(response.data)} rows into {table_name}.")
    return response.data


def update_rows(table_name: str, values: dict, filters: list):
    if not filters:
        raise ValueError("Filters are required to update data!")

    query = get_db().table(table_name).update(values)

    # filters are (column, operator, value), e.g. ("outlet_id", "eq", "outlet_001")
    for column, op, value in filters:
        query = getattr(query, op)(column, value)

    response = query.execute()
    return response.data


if __name__ == "__main__":
    export_outlets_csv()
    export_warehouses_csv()
