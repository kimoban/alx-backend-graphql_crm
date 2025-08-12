from crm.models import Customer, Product, Order
from django.utils import timezone

def seed():
    # Create customers
    alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    bob = Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")
    carol = Customer.objects.create(name="Carol", email="carol@example.com")

    # Create products
    laptop = Product.objects.create(name="Laptop", price=999.99, stock=10)
    phone = Product.objects.create(name="Phone", price=499.99, stock=25)
    mouse = Product.objects.create(name="Mouse", price=19.99, stock=100)

    # Create orders
    order1 = Order.objects.create(customer=alice, total_amount=999.99, order_date=timezone.now())
    order1.products.set([laptop])
    order2 = Order.objects.create(customer=bob, total_amount=519.98, order_date=timezone.now())
    order2.products.set([phone, mouse])
    print("Database seeded!")

if __name__ == "__main__":
    seed()
