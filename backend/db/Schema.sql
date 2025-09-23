-- Outlets table 
CREATE TABLE outlets (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    outlet_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    outlet_category VARCHAR(50),
    region VARCHAR(50),
    bd_season VARCHAR(20),
    is_weekend BOOLEAN,
    event TEXT,
    economic_zone VARCHAR(50),
    next_7_days_demand INT CHECK (next_7_days_demand >= 0)
);

-- Warehouses table
CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    region VARCHAR(50),
    warehouse_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    bd_season VARCHAR(20),
    is_weekend BOOLEAN,
    event TEXT,
    current_inventory INT CHECK (current_inventory >= 0),
    inbound_shipment INT CHECK (inbound_shipment >= 0),
    supplier_reliability FLOAT CHECK (supplier_reliability >= 0 AND supplier_reliability <= 1),
    supplier_capacity_index FLOAT,
    supplier_lead_time INT,
    allocation_ratio FLOAT,
    disruption_index FLOAT,
    transport_cost_index FLOAT,
    transport_capacity_factor FLOAT,
    max_storage_capacity INT CHECK (max_storage_capacity >= 0),
    optimal_inventory_level INT CHECK (optimal_inventory_level >= 0),
    feasible_max_supply INT CHECK (feasible_max_supply >= 0)
);

--Allocations (negotiation output)
CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outlet_id VARCHAR(50) NOT NULL REFERENCES outlets(outlet_id),
    warehouse_id VARCHAR(50) NOT NULL REFERENCES warehouses(warehouse_id),
    product_id VARCHAR(50) NOT NULL,
    allocated_quantity INT CHECK (allocated_quantity >= 0),
    transportation_duration INT CHECK (transportation_duration >= 0),
    reasoning TEXT, -- why this allocation was made (from AI explanation)
    CONSTRAINT unique_allocation UNIQUE (allocation_date, outlet_id, warehouse_id, product_id)
);

--  Deliveries (actual shipments)
CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    allocation_id INT REFERENCES allocations(id) ON DELETE CASCADE,
    delivery_date DATE,
    expected_arrival_date DATE,
    actual_arrival_date DATE,
    transport_mode VARCHAR(30), -- truck, rail, air
    transport_cost NUMERIC(10,2),
    delivered_quantity INT CHECK (delivered_quantity >= 0),
    status VARCHAR(30) DEFAULT 'scheduled' -- scheduled, in_transit, delivered, delayed
);


CREATE INDEX idx_outlet_product ON outlets(product_id);
CREATE INDEX idx_outlet_region ON outlets(region);
CREATE INDEX idx_warehouse_product ON warehouses(product_id);
CREATE INDEX idx_warehouse_region ON warehouses(region);
