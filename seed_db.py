#!/usr/bin/env python
import os
import sys
import django

# Add project directory to path
sys.path.append('/workspaces/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

from crm.models import Customer, Product, Order
from django.utils import timezone

def seed():
    print("Starting database seeding...")

    # Create or get customers
    alice, _ = Customer.objects.get_or_create(
        email="alice@example.com",
        defaults={'name': "Alice", 'phone': "+1234567890"}
    )
    bob, _ = Customer.objects.get_or_create(
        email="bob@example.com",
        defaults={'name': "Bob", 'phone': "123-456-7890"}
    )
    carol, _ = Customer.objects.get_or_create(
        email="carol@example.com",
        defaults={'name': "Carol"}
    )

    # Create or get products
    laptop, _ = Product.objects.get_or_create(
        name="Laptop",
        defaults={'price': 999.99, 'stock': 10}
    )
    phone, _ = Product.objects.get_or_create(
        name="Phone",
        defaults={'price': 499.99, 'stock': 25}
    )
    mouse, _ = Product.objects.get_or_create(
        name="Mouse",
        defaults={'price': 19.99, 'stock': 100}
    )

    # Create orders
    order1, _ = Order.objects.get_or_create(
        customer=alice,
        total_amount=999.99,
        order_date=timezone.now()
    )
    order1.products.set([laptop])
    order2, _ = Order.objects.get_or_create(
        customer=bob,
        total_amount=519.98,
        order_date=timezone.now()
    )
    order2.products.set([phone, mouse])

    print(f"Created customers: {Customer.objects.count()}")
    print(f"Created products: {Product.objects.count()}")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
    ]
    for c in customers:
        Customer.objects.create(**c)

    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Mouse", "price": 25.50, "stock": 100},
    ]
    for p in products:
        Product.objects.create(**p)

    print("Database seeded successfully.")

if __name__ == "__main__":
    seed()
