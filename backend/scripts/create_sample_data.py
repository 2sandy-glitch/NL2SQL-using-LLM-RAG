"""
Script to create sample data files for testing.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_data():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating sample data files...")
    
    np.random.seed(42)
    
    customers = pd.DataFrame({
        "customer_id": range(1, 101),
        "first_name": [f"FirstName_{i}" for i in range(1, 101)],
        "last_name": [f"LastName_{i}" for i in range(1, 101)],
        "email": [f"customer{i}@example.com" for i in range(1, 101)],
        "city": np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], 100),
        "state": np.random.choice(["NY", "CA", "IL", "TX", "AZ"], 100),
        "registration_date": [datetime.now() - timedelta(days=int(np.random.randint(1, 365))) for _ in range(100)],
        "is_active": np.random.choice([True, False], 100, p=[0.8, 0.2])
    })
    
    products = pd.DataFrame({
        "product_id": range(1, 51),
        "product_name": [f"Product_{i}" for i in range(1, 51)],
        "category": np.random.choice(["Electronics", "Clothing", "Books", "Home", "Sports"], 50),
        "price": np.round(np.random.uniform(10, 500, 50), 2),
        "stock_quantity": np.random.randint(0, 1000, 50),
        "supplier": [f"Supplier_{np.random.randint(1, 10)}" for _ in range(50)]
    })
    
    orders = pd.DataFrame({
        "order_id": range(1, 201),
        "customer_id": np.random.randint(1, 101, 200),
        "product_id": np.random.randint(1, 51, 200),
        "quantity": np.random.randint(1, 10, 200),
        "order_date": [datetime.now() - timedelta(days=int(np.random.randint(1, 90))) for _ in range(200)],
        "status": np.random.choice(["pending", "shipped", "delivered", "cancelled"], 200, p=[0.2, 0.3, 0.4, 0.1]),
        "total_amount": np.round(np.random.uniform(20, 1000, 200), 2)
    })
    
    employees = pd.DataFrame({
        "employee_id": range(1, 31),
        "name": [f"Employee_{i}" for i in range(1, 31)],
        "department": np.random.choice(["Sales", "Marketing", "Engineering", "HR", "Finance"], 30),
        "position": np.random.choice(["Manager", "Senior", "Junior", "Intern"], 30),
        "salary": np.round(np.random.uniform(30000, 120000, 30), 2),
        "hire_date": [datetime.now() - timedelta(days=int(np.random.randint(30, 1825))) for _ in range(30)],
        "email": [f"employee{i}@company.com" for i in range(1, 31)]
    })
    
    excel_path = os.path.join(output_dir, "sample_data.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        customers.to_excel(writer, sheet_name="customers", index=False)
        products.to_excel(writer, sheet_name="products", index=False)
        orders.to_excel(writer, sheet_name="orders", index=False)
        employees.to_excel(writer, sheet_name="employees", index=False)
    print(f"  [OK] Created: {excel_path}")
    
    for name, df in [("customers", customers), ("products", products), ("orders", orders), ("employees", employees)]:
        csv_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  [OK] Created: {csv_path}")
    
    print()
    print(f"  - Customers: {len(customers)} rows")
    print(f"  - Products: {len(products)} rows")
    print(f"  - Orders: {len(orders)} rows")
    print(f"  - Employees: {len(employees)} rows")


if __name__ == "__main__":
    create_sample_data()
