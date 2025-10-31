from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, serializers, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Category, Product, CartItem, Order, OrderItem, CustomUser, Cart
from .serializers import CategorySerializer, ProductSerializer, RegisterSerializer, ProfileSerializer, CartSerializer, \
    OrderSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'color', 'material']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['name']

# Auth endpoints
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

# Cart endpoints
class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        return self.request.user.profile.cart

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    profile, _ = CustomUser.objects.get_or_create(user=request.user)
    cart, _ = Cart.objects.get_or_create(user=profile)

    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    return Response({"detail": "Added"}, status=200)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    profile = request.user.profile
    cart = profile.cart
    product_id = request.data.get("product_id")
    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

    try:
        item = CartItem.objects.get(cart=cart, product_id=product_id)
        item.delete()
        return Response({"detail": "Removed"}, status=200)
    except CartItem.DoesNotExist:
        return Response({"detail": "Product not in cart"}, status=200)  # არ აგდებს 404


# Orders
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.profile)

    @action(detail=False, methods=["post"], url_path="create")
    @transaction.atomic
    def create_order(self, request, *args, **kwargs):
        profile = request.user.profile
        cart = profile.cart
        if cart.items.count() == 0:
            return Response({"detail": "Cart empty"}, status=status.HTTP_400_BAD_REQUEST)

        shipping_address = request.data.get("shipping_address", profile.address or "")
        phone = request.data.get("phone", profile.phone or "")
        notes = request.data.get("notes", "")

        order = Order.objects.create(
            user=profile,
            shipping_address=shipping_address,
            phone=phone,
            notes=notes,
        )
        total = 0
        for ci in cart.items.all():
            oi = OrderItem.objects.create(
                order=order,
                product=ci.product,
                quantity=ci.quantity,
                price=ci.product.price
            )
            total += oi.get_total_price()
            # reduce stock
            if ci.product.stock >= ci.quantity:
                ci.product.stock -= ci.quantity
            else:
                # if not enough stock, rollback
                raise serializers.ValidationError(f"Not enough stock for {ci.product.name}")
            ci.product.save()

        order.total_amount = total
        order.save()
        # clear cart
        cart.items.all().delete()

        # (optional) trigger Celery email task here
        from .tasks import send_order_confirmation_email
        send_order_confirmation_email.delay(order.id)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


