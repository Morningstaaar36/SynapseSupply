
-- Stores warehouse information
-- Static warehouse info
CREATE TABLE warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,        -- Unique warehouse identifier
    region VARCHAR(50) NOT NULL,
    max_storage_capacity INT CHECK (max_storage_capacity >= 0),
    supplier_reliability FLOAT CHECK (supplier_reliability BETWEEN 0 AND 1),
    supplier_capacity_index FLOAT,
    supplier_lead_time INT,
    disruption_index FLOAT,
    transport_cost_index FLOAT,
    transport_capacity_factor FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dynamic warehouse info per date or event
CREATE TABLE warehouse_snapshots (
    snapshot_id SERIAL PRIMARY KEY,
    warehouse_id VARCHAR(50) NOT NULL REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,               -- product for which inventory is tracked
    current_inventory INT CHECK (current_inventory >= 0),
    inbound_shipment INT CHECK (inbound_shipment >= 0),
    bd_season VARCHAR(20),
    is_weekend BOOLEAN,
    event TEXT,
    optimal_inventory_level INT CHECK (optimal_inventory_level >= 0),
    feasible_max_supply INT CHECK (feasible_max_supply >= 0),
    created_at TIMESTAMP DEFAULT NOW()
);


-- Stores outlet information (initially 4)

CREATE TABLE outlets (
    outlet_id VARCHAR(50) PRIMARY KEY,
    outlet_name TEXT,
    outlet_category VARCHAR(50),
    region VARCHAR(50),
    economic_zone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stores product information

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name TEXT NOT NULL,
    unit_of_measure VARCHAR(20),
    base_price FLOAT
);

--an outlet requests items from the warehouse.

CREATE TABLE allocation_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    outlet_id VARCHAR(50) NOT NULL REFERENCES outlets(outlet_id),
    warehouse_id VARCHAR(50) NOT NULL REFERENCES warehouses(warehouse_id),
    request_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending | approved | rejected
    event TEXT,  -- e.g. festival demand, promotion, etc.
    is_weekend BOOLEAN,
    bd_season VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Each request may have multiple products requested

CREATE TABLE allocation_request_items (
    id SERIAL PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES allocation_requests(request_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    requested_quantity INT CHECK (requested_quantity >= 0),
    next_7_days_demand INT CHECK (next_7_days_demand >= 0)
);

-- Stores allocation decisions made by the agent after negotiation and optimization

CREATE TABLE allocations (
    id SERIAL PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES allocation_requests(request_id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL REFERENCES products(product_id),
    allocated_quantity INT CHECK (allocated_quantity >= 0),
    transport_cost FLOAT,
    lead_time INT,
    negotiation_log JSONB, -- full reasoning trace from LangGraph
    created_at TIMESTAMP DEFAULT NOW()
);



