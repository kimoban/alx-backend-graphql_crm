import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Order
from crm.models import Product
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from decimal import Decimal
from django.utils import timezone

# Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    def validate_phone(self, phone):
        if not phone:
            return True
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return re.match(pattern, phone)

    def mutate(self, info, name, email, phone=None):
        # Email validation
        try:
            validate_email(email)
        except DjangoValidationError:
            return CreateCustomer(success=False, message="Invalid email format.")
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="Email already exists.")
        if phone and not self.validate_phone(phone):
            return CreateCustomer(success=False, message="Invalid phone format.")
        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, success=True, message="Customer created.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        customers = graphene.List(graphene.JSONString, required=True)
    created = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, customers):
        created = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(customers):
                name = data.get("name")
                email = data.get("email")
                phone = data.get("phone")
                try:
                    validate_email(email)
                    if Customer.objects.filter(email=email).exists():
                        raise Exception(f"Email already exists: {email}")
                    if phone and not re.match(r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$", phone):
                        raise Exception(f"Invalid phone format: {phone}")
                    customer = Customer(name=name, email=email, phone=phone)
                    customer.save()
                    created.append(customer)
                except Exception as e:
                    errors.append(f"Row {idx+1}: {str(e)}")
        return BulkCreateCustomers(created=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, name, price, stock=0):
        try:
            price = Decimal(price)
            if price <= 0:
                return CreateProduct(success=False, message="Price must be positive.")
            if stock is not None and stock < 0:
                return CreateProduct(success=False, message="Stock cannot be negative.")
            product = Product(name=name, price=price, stock=stock or 0)
            product.save()
            return CreateProduct(product=product, success=True, message="Product created.")
        except Exception as e:
            return CreateProduct(success=False, message=str(e))

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()


    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder()
        products = Product.objects.filter(pk__in=product_ids)
        if not products or len(products) != len(product_ids):
            return CreateOrder()
        if not product_ids:
            return CreateOrder()
        order = Order(customer=customer, order_date=order_date or timezone.now())
        order.save()
        order.products.set(products)
        total = sum([p.price for p in products], Decimal("0"))
        order.total_amount = Decimal(total)
        order.save()
        return CreateOrder()

# Main Mutation class

# Mutation to update low-stock products
class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)
        msg = f"{len(updated)} products restocked." if updated else "No products needed restocking."
        return UpdateLowStockProducts(updated_products=updated, message=msg)


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


# Query with filtering and ordering
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter, order_by=graphene.List(of_type=graphene.String))

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info, **kwargs):
        qs = Customer.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(self, info, **kwargs):
        qs = Product.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(self, info, **kwargs):
        qs = Order.objects.all()
        order_by = kwargs.get('order_by')
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
