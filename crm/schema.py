# import graphene
# from graphene_django import DjangoObjectType
# from .models import Customer, Product, Order
# from django.db import transaction
# from django.core.exceptions import ValidationError

# # GraphQL Object Types
# class CustomerType(DjangoObjectType):
#     class Meta:
#         model = Customer
#         fields = ("id", "name", "email", "phone")


# class ProductType(DjangoObjectType):
#     class Meta:
#         model = Product
#         fields = ("id", "name", "price", "stock")


# class OrderType(DjangoObjectType):
#     class Meta:
#         model = Order
#         fields = ("id", "customer", "products", "total_amount", "order_date")

# # ---------- Create Customer ----------
# class CreateCustomer(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         email = graphene.String(required=True)
#         phone = graphene.String(required=False)

#     customer = graphene.Field(CustomerType)
#     message = graphene.String()

#     def mutate(self, info, name, email, phone=None):
#         # Validation
#         if Customer.objects.filter(email=email).exists():
#             raise Exception("Email already exists")

#         if phone and not (phone.startswith("+") or "-" in phone or phone.isdigit()):
#             raise Exception("Invalid phone format")

#         customer = Customer(name=name, email=email, phone=phone)
#         customer.save()

#         return CreateCustomer(customer=customer, message="Customer created successfully")


# # ---------- Bulk Create Customers ----------
# class BulkCreateCustomers(graphene.Mutation):
#     class Arguments:
#         customers = graphene.List(
#             graphene.JSONString, required=True
#         )  # Each is {name, email, phone}

#     customers = graphene.List(CustomerType)
#     errors = graphene.List(graphene.String)

#     @transaction.atomic
#     def mutate(self, info, customers):
#         created_customers = []
#         errors = []

#         for data in customers:
#             try:
#                 if Customer.objects.filter(email=data["email"]).exists():
#                     raise ValidationError("Email already exists")

#                 c = Customer(
#                     name=data["name"],
#                     email=data["email"],
#                     phone=data.get("phone"),
#                 )
#                 c.full_clean()  # run Django model validation
#                 c.save()
#                 created_customers.append(c)
#             except Exception as e:
#                 errors.append(f"{data.get('email')}: {str(e)}")

#         return BulkCreateCustomers(customers=created_customers, errors=errors)


# # ---------- Create Product ----------
# class CreateProduct(graphene.Mutation):
#     class Arguments:
#         name = graphene.String(required=True)
#         price = graphene.Float(required=True)
#         stock = graphene.Int(required=False)

#     product = graphene.Field(ProductType)

#     def mutate(self, info, name, price, stock=0):
#         if price <= 0:
#             raise Exception("Price must be positive")
#         if stock < 0:
#             raise Exception("Stock cannot be negative")

#         product = Product(name=name, price=price, stock=stock)
#         product.save()
#         return CreateProduct(product=product)


# # ---------- Create Order ----------
# class CreateOrder(graphene.Mutation):
#     class Arguments:
#         customer_id = graphene.ID(required=True)
#         product_ids = graphene.List(graphene.ID, required=True)

#     order = graphene.Field(OrderType)

#     def mutate(self, info, customer_id, product_ids):
#         try:
#             customer = Customer.objects.get(id=customer_id)
#         except Customer.DoesNotExist:
#             raise Exception("Invalid customer ID")

#         if not product_ids:
#             raise Exception("At least one product is required")

#         products = Product.objects.filter(id__in=product_ids)
#         if products.count() != len(product_ids):
#             raise Exception("One or more product IDs are invalid")

#         order = Order(customer=customer)
#         order.save()
#         order.products.set(products)

#         total = sum(p.price for p in products)
#         order.total_amount = total
#         order.save()

#         return CreateOrder(order=order)
# class Mutation(graphene.ObjectType):
#     create_customer = CreateCustomer.Field()
#     bulk_create_customers = BulkCreateCustomers.Field()
#     create_product = CreateProduct.Field()
#     create_order = CreateOrder.Field()


# class Query(graphene.ObjectType):
#     hello = graphene.String(default_value="Hello, GraphQL!")

#     all_customers = graphene.List(CustomerType)
#     all_products = graphene.List(ProductType)
#     all_orders = graphene.List(OrderType)

#     def resolve_all_customers(root, info):
#         return Customer.objects.all()

#     def resolve_all_products(root, info):
#         return Product.objects.all()

#     def resolve_all_orders(root, info):
#         return Order.objects.all()


import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport




# ---------- GraphQL Types ----------
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
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ---------- Helper Validators ----------
def validate_phone(phone: str):
    """Check if phone matches +1234567890 or 123-456-7890 formats"""
    pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
    return re.match(pattern, phone)


# ---------- Create Customer ----------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, phone=None):
        errors = []

        if Customer.objects.filter(email=email).exists():
            errors.append("Email already exists")

        if phone and not validate_phone(phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890")

        if errors:
            return CreateCustomer(customer=None, message="Failed to create customer", errors=errors)

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully", errors=None)


# ---------- Bulk Create Customers ----------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(
            graphene.NonNull(graphene.JSONString), required=True
        )  # [{name, email, phone}, ...]

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for data in input:
            try:
                data_dict = eval(data) if isinstance(data, str) else data
                name = data_dict.get("name")
                email = data_dict.get("email")
                phone = data_dict.get("phone")

                if Customer.objects.filter(email=email).exists():
                    raise ValidationError(f"Email already exists: {email}")

                if phone and not validate_phone(phone):
                    raise ValidationError(f"Invalid phone format for {email}")

                c = Customer(name=name, email=email, phone=phone)
                c.full_clean()
                c.save()
                created_customers.append(c)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# ---------- Create Product ----------
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, price, stock=0):
        errors = []
        if price <= 0:
            errors.append("Price must be positive")
        if stock < 0:
            errors.append("Stock cannot be negative")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product, errors=None)


# ---------- Create Order ----------
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        errors = []

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrder(order=None, errors=errors)

        if not product_ids:
            errors.append("At least one product is required")
            return CreateOrder(order=None, errors=errors)

        products = Product.objects.filter(id__in=product_ids)
        if products.count() != len(product_ids):
            errors.append("One or more product IDs are invalid")
            return CreateOrder(order=None, errors=errors)

        order = Order(customer=customer, order_date=order_date or None)
        order.save()
        order.products.set(products)

        # Calculate total
        total = sum(p.price for p in products)
        order.total_amount = total
        order.save()

        return CreateOrder(order=order, errors=None)


# ---------- Root Mutation ----------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# ---------- Queries ----------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()


# ---------- GraphQL Types ----------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# ---------- Query ----------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

    # Filtered lists
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(root, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_products(root, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def resolve_all_orders(root, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
    
class ProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass  # no arguments needed

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += 10  # simulate restocking
            product.save()
            updated.append(product)

        return UpdateLowStockProducts(
            updated_products=updated,
            message="Low stock products successfully updated."
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
