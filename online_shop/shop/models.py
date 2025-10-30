from decimal import Decimal
from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User

from shop.choices import COLOR_CHOICES, MATERIAL_CHOICES, STATUS_CHOICES


#Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Photo")
    is_active = models.BooleanField(default=True, verbose_name="Active?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

#Product Model
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")
    is_available = models.BooleanField(default=True, verbose_name="Available?")
    featured = models.BooleanField(default=False, verbose_name="Featured?")
    color = models.CharField(max_length=30, choices=COLOR_CHOICES, default="white")
    material = models.CharField(max_length=30, choices=MATERIAL_CHOICES, default="wood")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_2 = models.ImageField(upload_to="products/", blank=True, null=True)
    image_3 = models.ImageField(upload_to="products/", blank=True, null=True)
    image_4 = models.ImageField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


#CustomUser Model
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="first Name")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="last Name")
    phone = models.CharField(max_length=30, blank=True, verbose_name="phone")
    birth_date = models.DateField(null=True, blank=True, verbose_name="birth Date")
    city = models.CharField(max_length=150, blank=True, verbose_name="vity")
    address = models.TextField(blank=True, null=True, verbose_name="address")

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.email = None

    def __str__(self):
        return self.get_full_name() or self.user.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


#Cart Model
class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="user")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart({self.user})"

    def get_total_price(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.get_price()
        return total

    def get_total_items(self):
        return list(self.items.all())

    def get_total_items_count(self):
        return sum(item.quantity for item in self.items.all())


#CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="quantity")

    class Meta:
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_price(self):
        return self.product.price * self.quantity


# Orders
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="items")
    order_number = models.CharField(max_length=100, unique=True, verbose_name="order number")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="total amount")
    shipping_address = models.TextField(verbose_name="shipping address")
    phone = models.CharField(max_length=30, verbose_name="phone")
    notes = models.TextField(blank=True, null=True, verbose_name="notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.order_number} ({self.user})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{timezone.now().strftime('%Y%m%d%H%M%S')}-{self.id or 'TEMP'}"
        super().save(*args, **kwargs)

    def recalc_total(self):
        total = sum([oi.get_total_price() for oi in self.items.all()])
        self.total_amount = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="product")
    quantity = models.PositiveIntegerField(default=1, verbose_name="quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="price", default=0)

    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price or self.price == 0:
            self.price = self.product.price
        super().save(*args, **kwargs)