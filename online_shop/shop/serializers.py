from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Product, CustomUser, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User


User: type[User] = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(write_only=True, source="category", queryset=Category.objects.all())

    class Meta:
        model = Product
        fields = "__all__"


# User registration/login/profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data["username"], email=validated_data.get("email"), password=validated_data["password"])
        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = CustomUser
        fields = "__all__"


# Cart serializers
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, source="product", queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ("id", "product", "product_id", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "user", "updated_at", "items")


# Order serializers
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("order_number", "total_amount", "created_at", "updated_at")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def validate_email(value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


#passwordresetserializers
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    @staticmethod
    def validate_email(value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8)

    @staticmethod
    def validate_new_password(value):
        return value
