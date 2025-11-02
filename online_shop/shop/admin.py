from django.contrib import admin
from .models import Category, Product, CustomUser, Cart, CartItem, OrderItem, Order


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_available", "featured")
    search_fields = ("name",)
    list_filter = ("category", "color", "material", "is_available", "featured")
    list_editable = ("price", "stock", "is_available", "featured")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "phone", "city")
    search_fields = ("phone", "first_name", "last_name")
    list_filter = ("city",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    list_filter = ("user",)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "total_amount", "created_at")
    search_fields = ("order_number", "user__user__username", "user__phone")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
    readonly_fields = ("order_number",)




