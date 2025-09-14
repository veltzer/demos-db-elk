# Elasticsearch Bulk Insert Exercise with Fake Data Generation

## Overview
This exercise demonstrates how to generate large amounts of fake data and efficiently bulk insert it into Elasticsearch. We'll create a realistic e-commerce dataset with customers, products, and orders, then explore different bulk insert strategies and performance optimizations.

## Prerequisites

```bash
# Install required Python packages
pip install faker elasticsearch pandas numpy python-dateutil tqdm

# Verify Elasticsearch is running
curl -X GET "localhost:9200" -u elastic:your-password
```

---

## Part 1: Fake Data Generator Script

### 1.1 Complete Data Generator
Save this as `generate_fake_data.py`:

```python
#!/usr/bin/env python3
"""
Elasticsearch Fake Data Generator
Generates realistic e-commerce data for bulk insert exercises
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from faker import Faker
from dateutil.relativedelta import relativedelta
import argparse
import gzip
import csv

# Initialize Faker with seed for reproducibility
Faker.seed(42)
fake = Faker()
random.seed(42)
np.random.seed(42)

class EcommerceDataGenerator:
    """Generate realistic e-commerce data"""
    
    def __init__(self):
        self.fake = Faker()
        
        # Product categories and their attributes
        self.categories = {
            "Electronics": {
                "brands": ["TechCorp", "ElectroMax", "DigiPro", "SmartLife", "PowerTech"],
                "adjectives": ["Wireless", "Smart", "Pro", "Ultra", "Premium"],
                "products": ["Headphones", "Speaker", "Charger", "Cable", "Adapter", "Monitor", "Keyboard", "Mouse"],
                "price_range": (19.99, 1999.99)
            },
            "Clothing": {
                "brands": ["FashionForward", "StyleCo", "TrendSet", "UrbanWear", "ClassicFit"],
                "adjectives": ["Classic", "Modern", "Vintage", "Premium", "Casual"],
                "products": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sweater", "Shirt", "Pants"],
                "price_range": (14.99, 299.99)
            },
            "Home & Garden": {
                "brands": ["HomeStyle", "GardenPro", "ComfortLiving", "NatureFirst", "CozyHome"],
                "adjectives": ["Durable", "Eco-Friendly", "Modern", "Classic", "Compact"],
                "products": ["Lamp", "Rug", "Planter", "Cushion", "Vase", "Mirror", "Clock"],
                "price_range": (9.99, 499.99)
            },
            "Sports": {
                "brands": ["SportMax", "ActiveLife", "ProAthletic", "FitGear", "EndurancePro"],
                "adjectives": ["Professional", "Lightweight", "Durable", "Advanced", "Beginner"],
                "products": ["Yoga Mat", "Dumbbells", "Running Shoes", "Water Bottle", "Resistance Bands"],
                "price_range": (12.99, 599.99)
            },
            "Books": {
                "brands": ["PublishPro", "BookWorld", "ReadMore", "LitPress", "PageTurner"],
                "adjectives": ["Bestselling", "Award-Winning", "Classic", "Modern", "Essential"],
                "products": ["Novel", "Textbook", "Guide", "Manual", "Biography", "Cookbook"],
                "price_range": (4.99, 79.99)
            }
        }
        
        # Customer segments for realistic behavior
        self.customer_segments = {
            "frequent_buyer": {"order_probability": 0.8, "items_per_order": (2, 5), "price_sensitivity": 0.3},
            "occasional_buyer": {"order_probability": 0.4, "items_per_order": (1, 3), "price_sensitivity": 0.6},
            "bulk_buyer": {"order_probability": 0.6, "items_per_order": (5, 15), "price_sensitivity": 0.4},
            "window_shopper": {"order_probability": 0.1, "items_per_order": (1, 2), "price_sensitivity": 0.9},
            "premium_buyer": {"order_probability": 0.7, "items_per_order": (1, 4), "price_sensitivity": 0.1}
        }
        
        # Payment and shipping methods
        self.payment_methods = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay", "bitcoin"]
        self.shipping_methods = ["standard", "express", "overnight", "economy", "prime"]
        
        # Review templates for realistic reviews
        self.review_sentiments = {
            5: ["Excellent", "Amazing", "Perfect", "Highly recommend", "Best purchase ever"],
            4: ["Good", "Very nice", "Satisfied", "Would buy again", "Great value"],
            3: ["Okay", "Average", "Decent", "As expected", "Fair"],
            2: ["Disappointed", "Not great", "Below expectations", "Could be better", "Mediocre"],
            1: ["Terrible", "Worst purchase", "Don't buy", "Complete waste", "Awful"]
        }

    def generate_product(self, product_id: int) -> Dict[str, Any]:
        """Generate a single product"""
        category = random.choice(list(self.categories.keys()))
        cat_info = self.categories[category]
        
        brand = random.choice(cat_info["brands"])
        adjective = random.choice(cat_info["adjectives"])
        product_type = random.choice(cat_info["products"])
        
        name = f"{brand} {adjective} {product_type}"
        sku = f"SKU-{category[:3].upper()}-{product_id:06d}"
        
        # Price with realistic distribution
        min_price, max_price = cat_info["price_range"]
        price = round(np.random.lognormal(np.log(min_price + 20), 0.5), 2)
        price = min(max(price, min_price), max_price)
        
        # Stock with realistic distribution (more items have moderate stock)
        stock = int(np.random.gamma(2, 50))
        
        # Ratings and reviews
        num_reviews = int(np.random.exponential(20))
        if num_reviews > 0:
            # Generate realistic rating distribution (tends toward 4-5 stars)
            ratings = np.random.choice([1, 2, 3, 4, 5], 
                                      size=num_reviews, 
                                      p=[0.05, 0.08, 0.17, 0.35, 0.35])
            avg_rating = round(float(np.mean(ratings)), 2)
        else:
            avg_rating = None
        
        # Product attributes
        weight = round(random.uniform(0.1, 25.0), 2)  # kg
        
        # Tags for search
        tags = [category.lower(), brand.lower(), product_type.lower()]
        if price < 50:
            tags.append("budget")
        elif price > 500:
            tags.append("premium")
        
        # Seasonal flags
        is_seasonal = random.random() < 0.2
        
        return {
            "product_id": f"PROD-{product_id:08d}",
            "sku": sku,
            "name": name,
            "description": self.fake.text(max_nb_chars=200),
            "category": category,
            "subcategory": product_type,
            "brand": brand,
            "price": price,
            "currency": "USD",
            "stock_quantity": stock,
            "in_stock": stock > 0,
            "weight_kg": weight,
            "dimensions": {
                "length_cm": round(random.uniform(5, 100), 1),
                "width_cm": round(random.uniform(5, 100), 1),
                "height_cm": round(random.uniform(5, 100), 1)
            },
            "color": self.fake.color_name() if category == "Clothing" else None,
            "size": random.choice(["S", "M", "L", "XL"]) if category == "Clothing" else None,
            "material": random.choice(["Cotton", "Polyester", "Wool"]) if category == "Clothing" else None,
            "tags": tags,
            "avg_rating": avg_rating,
            "review_count": num_reviews,
            "is_featured": random.random() < 0.1,
            "is_seasonal": is_seasonal,
            "season": random.choice(["spring", "summer", "fall", "winter"]) if is_seasonal else None,
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now").isoformat(),
            "updated_at": self.fake.date_time_between(start_date="-30d", end_date="now").isoformat(),
            "manufacturer_country": self.fake.country(),
            "warranty_months": random.choice([0, 6, 12, 24, 36]) if category == "Electronics" else 0,
            "discount_percentage": random.choice([0, 0, 0, 5, 10, 15, 20, 25]) # Most items not on discount
        }

    def generate_customer(self, customer_id: int) -> Dict[str, Any]:
        """Generate a single customer"""
        segment = random.choice(list(self.customer_segments.keys()))
        
        # Generate realistic age distribution
        age = int(np.random.normal(35, 12))
        age = max(18, min(80, age))
        
        # Generate join date (older customers more likely)
        days_ago = int(np.random.exponential(365))
        join_date = datetime.now() - timedelta(days=min(days_ago, 1095))  # Max 3 years
        
        # Location
        city = self.fake.city()
        state = self.fake.state()
        country = "United States"  # Simplify for this exercise
        
        # Customer lifetime value based on segment
        if segment == "premium_buyer":
            ltv = round(np.random.lognormal(7, 1), 2)  # Higher LTV
        elif segment == "frequent_buyer":
            ltv = round(np.random.lognormal(6, 1), 2)
        else:
            ltv = round(np.random.lognormal(5, 1), 2)
        
        # Email with realistic domains
        email_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]
        username = self.fake.user_name()
        email = f"{username}@{random.choice(email_domains)}"
        
        return {
            "customer_id": f"CUST-{customer_id:08d}",
            "email": email,
            "username": username,
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "full_name": self.fake.name(),
            "age": age,
            "gender": random.choice(["M", "F", "Other", None]),
            "phone": self.fake.phone_number(),
            "segment": segment,
            "address": {
                "street": self.fake.street_address(),
                "city": city,
                "state": state,
                "country": country,
                "postal_code": self.fake.postcode(),
                "coordinates": {
                    "lat": float(self.fake.latitude()),
                    "lon": float(self.fake.longitude())
                }
            },
            "join_date": join_date.isoformat(),
            "last_login": self.fake.date_time_between(start_date="-7d", end_date="now").isoformat(),
            "is_active": random.random() < 0.85,
            "email_verified": random.random() < 0.9,
            "newsletter_subscribed": random.random() < 0.4,
            "preferred_language": random.choice(["en", "es", "fr", "de", "zh"]),
            "preferred_currency": "USD",
            "lifetime_value": ltv,
            "total_orders": 0,  # Will be updated when generating orders
            "loyalty_points": int(ltv * 10),
            "tier": random.choice(["bronze", "silver", "gold", "platinum"]),
            "preferred_categories": random.sample(list(self.categories.keys()), k=random.randint(1, 3)),
            "device_type": random.choice(["desktop", "mobile", "tablet"]),
            "acquisition_channel": random.choice(["organic", "paid_search", "social", "email", "direct"])
        }

    def generate_order(self, order_id: int, customer: Dict, products: List[Dict]) -> Dict[str, Any]:
        """Generate a single order"""
        segment_info = self.customer_segments[customer["segment"]]
        
        # Order date (recent orders more likely)
        days_ago = int(np.random.exponential(30))
        order_date = datetime.now() - timedelta(days=min(days_ago, 365))
        
        # Number of items based on customer segment
        min_items, max_items = segment_info["items_per_order"]
        num_items = random.randint(min_items, max_items)
        
        # Select products (price sensitive customers choose cheaper items)
        if segment_info["price_sensitivity"] > 0.5:
            # Sort by price and favor cheaper products
            sorted_products = sorted(products, key=lambda x: x["price"])
            selected_products = random.sample(sorted_products[:len(sorted_products)//2], 
                                            min(num_items, len(sorted_products)//2))
        else:
            selected_products = random.sample(products, min(num_items, len(products)))
        
        # Generate order items
        order_items = []
        subtotal = 0
        total_quantity = 0
        
        for product in selected_products:
            quantity = random.randint(1, 3) if customer["segment"] != "bulk_buyer" else random.randint(5, 20)
            item_total = round(product["price"] * quantity, 2)
            
            order_items.append({
                "product_id": product["product_id"],
                "product_name": product["name"],
                "category": product["category"],
                "quantity": quantity,
                "unit_price": product["price"],
                "total_price": item_total,
                "discount_amount": round(item_total * product["discount_percentage"] / 100, 2)
            })
            
            subtotal += item_total
            total_quantity += quantity
        
        # Calculate totals
        tax_rate = round(random.uniform(0.05, 0.10), 3)
        tax_amount = round(subtotal * tax_rate, 2)
        
        shipping_costs = {
            "economy": 5.99,
            "standard": 9.99,
            "express": 19.99,
            "overnight": 39.99,
            "prime": 0
        }
        shipping_method = random.choice(self.shipping_methods)
        shipping_cost = shipping_costs.get(shipping_method, 9.99)
        
        total = round(subtotal + tax_amount + shipping_cost, 2)
        
        # Order status based on date
        days_since_order = (datetime.now() - order_date).days
        if days_since_order > 7:
            status = random.choice(["delivered", "delivered", "delivered", "returned", "cancelled"])
        elif days_since_order > 3:
            status = random.choice(["shipped", "delivered", "in_transit"])
        else:
            status = random.choice(["pending", "processing", "shipped"])
        
        # Delivery date
        if status in ["delivered", "returned"]:
            delivery_date = (order_date + timedelta(days=random.randint(2, 7))).isoformat()
        else:
            delivery_date = None
        
        return {
            "order_id": f"ORD-{order_id:010d}",
            "customer_id": customer["customer_id"],
            "customer_email": customer["email"],
            "order_date": order_date.isoformat(),
            "delivery_date": delivery_date,
            "status": status,
            "payment_method": random.choice(self.payment_methods),
            "payment_status": "paid" if status != "cancelled" else "refunded",
            "shipping_method": shipping_method,
            "shipping_address": customer["address"],
            "billing_address": customer["address"],  # Simplification
            "items": order_items,
            "item_count": len(order_items),
            "total_quantity": total_quantity,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "total_amount": total,
            "currency": "USD",
            "coupon_code": self.fake.lexify(text="????-####") if random.random() < 0.2 else None,
            "coupon_discount": round(subtotal * 0.1, 2) if random.random() < 0.2 else 0,
            "notes": self.fake.sentence() if random.random() < 0.1 else None,
            "is_gift": random.random() < 0.1,
            "gift_message": self.fake.sentence() if random.random() < 0.05 else None,
            "source": random.choice(["web", "mobile_app", "tablet", "phone"]),
            "ip_address": self.fake.ipv4(),
            "user_agent": self.fake.user_agent(),
            "refund_amount": total if status == "returned" else 0,
            "refund_reason": random.choice(["defective", "not_as_described", "changed_mind"]) if status == "returned" else None
        }

    def generate_review(self, review_id: int, customer: Dict, product: Dict, order: Dict) -> Dict[str, Any]:
        """Generate a product review"""
        # Only delivered orders get reviews, and not all of them
        if order["status"] != "delivered" or random.random() > 0.6:
            return None
        
        # Rating distribution (skewed toward positive)
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.17, 0.35, 0.35])
        
        # Review date (after delivery)
        if order["delivery_date"]:
            delivery = datetime.fromisoformat(order["delivery_date"])
            review_date = delivery + timedelta(days=random.randint(1, 30))
        else:
            review_date = datetime.now()
        
        # Review text based on rating
        sentiments = self.review_sentiments[rating]
        title = random.choice(sentiments)
        
        # Verified purchase
        verified = random.random() < 0.9
        
        # Helpful votes (higher rated reviews get more helpful votes)
        helpful_votes = int(np.random.exponential(rating * 2))
        total_votes = helpful_votes + int(np.random.exponential(2))
        
        return {
            "review_id": f"REV-{review_id:010d}",
            "product_id": product["product_id"],
            "customer_id": customer["customer_id"],
            "order_id": order["order_id"],
            "rating": rating,
            "title": title,
            "comment": self.fake.paragraph(nb_sentences=random.randint(2, 8)),
            "pros": self.fake.words(nb=random.randint(2, 5)) if rating >= 4 else [],
            "cons": self.fake.words(nb=random.randint(2, 5)) if rating <= 3 else [],
            "review_date": review_date.isoformat(),
            "verified_purchase": verified,
            "helpful_votes": helpful_votes,
            "total_votes": total_votes,
            "helpfulness_score": round(helpful_votes / total_votes, 2) if total_votes > 0 else 0,
            "has_images": random.random() < 0.15,
            "has_video": random.random() < 0.05,
            "response_from_seller": self.fake.sentence() if random.random() < 0.1 else None,
            "edited": random.random() < 0.1,
            "recommended": rating >= 4,
            "incentivized": random.random() < 0.02
        }

    def generate_cart_abandonment(self, cart_id: int, customer: Dict, products: List[Dict]) -> Dict[str, Any]:
        """Generate abandoned cart data"""
        # Cart creation date
        days_ago = int(np.random.exponential(7))
        cart_date = datetime.now() - timedelta(days=min(days_ago, 30))
        
        # Select products
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        cart_items = []
        total = 0
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            item_total = product["price"] * quantity
            
            cart_items.append({
                "product_id": product["product_id"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"],
                "total_price": round(item_total, 2)
            })
            
            total += item_total
        
        return {
            "cart_id": f"CART-{cart_id:010d}",
            "customer_id": customer["customer_id"],
            "session_id": str(uuid.uuid4()),
            "created_at": cart_date.isoformat(),
            "updated_at": (cart_date + timedelta(minutes=random.randint(1, 60))).isoformat(),
            "items": cart_items,
            "item_count": len(cart_items),
            "total_value": round(total, 2),
            "currency": "USD",
            "abandonment_reason": random.choice([
                "high_shipping",
                "found_better_price",
                "just_browsing",
                "payment_issues",
                "too_complicated",
                None
            ]),
            "recovery_email_sent": random.random() < 0.7,
            "recovered": random.random() < 0.15,
            "device_type": customer["device_type"],
            "source": customer["acquisition_channel"]
        }

    def generate_dataset(self, 
                        num_products: int = 1000,
                        num_customers: int = 5000,
                        num_orders: int = 10000,
                        num_carts: int = 2000) -> Dict[str, List]:
        """Generate complete e-commerce dataset"""
        
        print(f"Generating E-commerce Dataset:")
        print(f"  - Products: {num_products}")
        print(f"  - Customers: {num_customers}")
        print(f"  - Orders: {num_orders}")
        print(f"  - Abandoned Carts: {num_carts}")
        
        # Generate products
        print("\n1. Generating products...")
        products = []
        for i in range(num_products):
            products.append(self.generate_product(i + 1))
            if (i + 1) % 100 == 0:
                print(f"   Generated {i + 1} products...")
        
        # Generate customers
        print("\n2. Generating customers...")
        customers = []
        for i in range(num_customers):
            customers.append(self.generate_customer(i + 1))
            if (i + 1) % 500 == 0:
                print(f"   Generated {i + 1} customers...")
        
        # Generate orders
        print("\n3. Generating orders...")
        orders = []
        reviews = []
        review_id = 1
        
        for i in range(num_orders):
            # Pick a customer (some customers order more than others)
            customer = random.choice(customers)
            segment_info = self.customer_segments[customer["segment"]]
            
            # Generate order if customer would order
            if random.random() < segment_info["order_probability"]:
                order = self.generate_order(i + 1, customer, products)
                orders.append(order)
                
                # Update customer's total orders
                customer["total_orders"] += 1
                
                # Generate reviews for some order items
                for item in order["items"][:3]:  # Max 3 reviews per order
                    product = next(p for p in products if p["product_id"] == item["product_id"])
                    review = self.generate_review(review_id, customer, product, order)
                    if review:
                        reviews.append(review)
                        review_id += 1
            
            if (i + 1) % 1000 == 0:
                print(f"   Generated {i + 1} orders and {len(reviews)} reviews...")
        
        # Generate abandoned carts
        print("\n4. Generating abandoned carts...")
        carts = []
        for i in range(num_carts):
            customer = random.choice(customers)
            carts.append(self.generate_cart_abandonment(i + 1, customer, products))
            if (i + 1) % 500 == 0:
                print(f"   Generated {i + 1} abandoned carts...")
        
        print(f"\n✓ Dataset generation complete!")
        print(f"  - Products: {len(products)}")
        print(f"  - Customers: {len(customers)}")
        print(f"  - Orders: {len(orders)}")
        print(f"  - Reviews: {len(reviews)}")
        print(f"  - Abandoned Carts: {len(carts)}")
        
        return {
            "products": products,
            "customers": customers,
            "orders": orders,
            "reviews": reviews,
            "carts": carts
        }


def save_data(data: Dict[str, List], output_format: str = "json", output_dir: str = "./data"):
    """Save generated data to files"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    if output_format == "json":
        # Save as JSON files
        for data_type, records in data.items():
            filename = f"{output_dir}/{data_type}.json"
            with open(filename, 'w') as f:
                json.dump(records, f, indent=2, default=str)
            print(f"Saved {len(records)} {data_type} to {filename}")
    
    elif output_format == "ndjson":
        # Save as NDJSON (newline-delimited JSON) - better for bulk insert
        for data_type, records in data.items():
            filename = f"{output_dir}/{data_type}.ndjson"
            with open(filename, 'w') as f:
                for record in records:
                    f.write(json.dumps(record, default=str) + '\n')
            print(f"Saved {len(records)} {data_type} to {filename}")
    
    elif output_format == "compressed":
        # Save as compressed NDJSON
        for data_type, records in data.items():
            filename = f"{output_dir}/{data_type}.ndjson.gz"
            with gzip.open(filename, 'wt') as f:
                for record in records:
                    f.write(json.dumps(record, default=str) + '\n')
            print(f"Saved {len(records)} {data_type} to {filename} (compressed)")
    
    elif output_format == "csv":
        # Save as CSV (flatten nested structures)
        for data_type, records in data.items():
            if records:
                filename = f"{output_dir}/{data_type}.csv"
                # Flatten nested dictionaries for CSV
                flattened = []
                for record in records:
                    flat_record = {}
                    for key, value in record.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                flat_record[f"{key}_{sub_key}"] = sub_value
                        elif isinstance(value, list):
                            flat_record[key] = json.dumps(value)
                        else:
                            flat_record[key] = value
                    flattened.append(flat_record)
                
                # Write CSV
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened)
                print(f"Saved {len(records)} {data_type} to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Generate fake e-commerce data for Elasticsearch')
    parser.add_argument('--products', type=int, default=1000, help='Number of products to generate')
    parser.add_argument('--customers', type=int, default=5000, help='Number of customers to generate')
    parser.add_argument('--orders', type=int, default=10000, help='Number of orders to generate')
    parser.add_argument('--carts', type=int, default=2000, help='Number of abandoned carts to generate')
    parser.add_argument('--format', choices=['json', 'ndjson', 'compressed', 'csv'], 
                       default='ndjson', help='Output format')
    parser.add_argument('--output-dir', default='./data', help='Output directory')
    
    args = parser.parse_args()
    
    # Generate data
    generator = EcommerceDataGenerator()
    data = generator.generate_dataset(
        num_products=args.products,
        num_customers=args.customers,
        num_orders=args.orders,
        num_carts=args.carts
    )
    
    # Save data
    save_data(data, output_format=args.format, output_dir=args.output_dir)
    
    print(f"\n✓ All data saved to {args.output_dir}/")


if __name__ == "__main__":
    main()
```

### 1.2 Quick Data Generator (Simplified Version)
For quick testing, save this as `quick_generator.py`:

```python
#!/usr/bin/env python3
"""Quick data generator for testing bulk inserts"""

import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_simple_products(count=1000):
    """Generate simple product documents"""
    products = []
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books"]
    
    for i in range(count):
        products.append({
            "product_id": f"PROD-{i:06d}",
            "name": f"{fake.company()} {fake.catch_phrase()}",