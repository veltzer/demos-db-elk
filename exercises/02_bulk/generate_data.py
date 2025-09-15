#!/usr/bin/env python3
"""
Data generator for Elasticsearch bulk insert exercise
Generates fake e-commerce data for testing bulk insert performance
"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker
import argparse
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_product(product_id):
    """Generate a single product document"""
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", "Food", "Beauty"]
    brands = ["TechCorp", "StyleCo", "HomePlus", "SportMax", "BookWorld", "FunToys", "GourmetLife", "BeautyPro"]

    category = random.choice(categories)
    brand = random.choice(brands)

    price = round(random.uniform(9.99, 999.99), 2)
    stock = random.randint(0, 1000)
    rating = round(random.uniform(1.0, 5.0), 1)
    reviews = random.randint(0, 500)

    return {
        "product_id": f"PROD-{product_id:08d}",
        "name": f"{brand} {fake.catch_phrase()}",
        "description": fake.text(max_nb_chars=200),
        "category": category,
        "brand": brand,
        "price": price,
        "currency": "USD",
        "stock_quantity": stock,
        "in_stock": stock > 0,
        "rating": rating,
        "review_count": reviews,
        "tags": fake.words(nb=random.randint(3, 7)),
        "created_at": fake.date_time_between(start_date="-2y", end_date="now").isoformat(),
        "updated_at": fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
        "sku": f"SKU-{category[:3].upper()}-{product_id:06d}",
        "weight_kg": round(random.uniform(0.1, 25.0), 2),
        "is_featured": random.random() < 0.1,
        "discount_percentage": random.choice([0, 0, 0, 5, 10, 15, 20, 25])
    }

def generate_customer(customer_id):
    """Generate a single customer document"""
    segments = ["premium", "regular", "occasional", "new"]
    countries = ["United States", "Canada", "United Kingdom", "Germany", "France", "Australia", "Japan"]

    return {
        "customer_id": f"CUST-{customer_id:08d}",
        "email": fake.email(),
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "full_name": fake.name(),
        "phone": fake.phone_number(),
        "segment": random.choice(segments),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "country": random.choice(countries),
            "postal_code": fake.postcode(),
            "lat": float(fake.latitude()),
            "lon": float(fake.longitude())
        },
        "join_date": fake.date_time_between(start_date="-3y", end_date="now").isoformat(),
        "last_login": fake.date_time_between(start_date="-7d", end_date="now").isoformat(),
        "is_active": random.random() < 0.85,
        "total_spent": round(random.uniform(0, 10000), 2),
        "order_count": random.randint(0, 100),
        "loyalty_points": random.randint(0, 5000)
    }

def generate_order(order_id, num_products):
    """Generate a single order document"""
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled", "returned"]
    payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]

    num_items = random.randint(1, 5)
    items = []
    subtotal = 0

    for i in range(num_items):
        product_id = random.randint(1, num_products)
        quantity = random.randint(1, 3)
        unit_price = round(random.uniform(9.99, 499.99), 2)
        total_price = round(unit_price * quantity, 2)

        items.append({
            "product_id": f"PROD-{product_id:08d}",
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })
        subtotal += total_price

    tax = round(subtotal * 0.08, 2)
    shipping = round(random.uniform(5.99, 29.99), 2)
    total = round(subtotal + tax + shipping, 2)

    order_date = fake.date_time_between(start_date="-1y", end_date="now")

    return {
        "order_id": f"ORD-{order_id:010d}",
        "customer_id": f"CUST-{random.randint(1, 5000):08d}",
        "order_date": order_date.isoformat(),
        "status": random.choice(statuses),
        "payment_method": random.choice(payment_methods),
        "items": items,
        "item_count": len(items),
        "subtotal": subtotal,
        "tax_amount": tax,
        "shipping_cost": shipping,
        "total_amount": total,
        "currency": "USD",
        "shipping_address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "country": fake.country(),
            "postal_code": fake.postcode()
        }
    }

def save_as_ndjson(data, filename):
    """Save data as newline-delimited JSON (for bulk insert)"""
    with open(filename, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')

def save_as_bulk_format(data, index_name, filename):
    """Save data in Elasticsearch bulk format"""
    with open(filename, 'w') as f:
        for record in data:
            # Write the action line
            action = {"index": {"_index": index_name}}
            f.write(json.dumps(action) + '\n')
            # Write the document line
            f.write(json.dumps(record) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Generate fake e-commerce data for Elasticsearch')
    parser.add_argument('--products', type=int, default=10000, help='Number of products to generate')
    parser.add_argument('--customers', type=int, default=5000, help='Number of customers to generate')
    parser.add_argument('--orders', type=int, default=20000, help='Number of orders to generate')
    parser.add_argument('--format', choices=['ndjson', 'bulk'], default='bulk', help='Output format')
    parser.add_argument('--output-dir', default='./data', help='Output directory')

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating fake e-commerce data...")
    print(f"  Products: {args.products}")
    print(f"  Customers: {args.customers}")
    print(f"  Orders: {args.orders}")

    # Generate products
    print("\nGenerating products...")
    products = [generate_product(i + 1) for i in range(args.products)]

    # Generate customers
    print("Generating customers...")
    customers = [generate_customer(i + 1) for i in range(args.customers)]

    # Generate orders
    print("Generating orders...")
    orders = [generate_order(i + 1, args.products) for i in range(args.orders)]

    # Save data
    print("\nSaving data...")
    if args.format == 'ndjson':
        save_as_ndjson(products, f"{args.output_dir}/products.ndjson")
        save_as_ndjson(customers, f"{args.output_dir}/customers.ndjson")
        save_as_ndjson(orders, f"{args.output_dir}/orders.ndjson")
        print(f"Data saved as NDJSON in {args.output_dir}/")
    else:
        save_as_bulk_format(products, "products", f"{args.output_dir}/products_bulk.json")
        save_as_bulk_format(customers, "customers", f"{args.output_dir}/customers_bulk.json")
        save_as_bulk_format(orders, "orders", f"{args.output_dir}/orders_bulk.json")
        print(f"Data saved in bulk format in {args.output_dir}/")

    print("\n✓ Data generation complete!")

    # Print file sizes
    for filename in os.listdir(args.output_dir):
        filepath = os.path.join(args.output_dir, filename)
        if os.path.isfile(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  {filename}: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()