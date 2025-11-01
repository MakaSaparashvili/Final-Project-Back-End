from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shop.models import CustomUser, Cart, Product, CartItem
from shop.serializers import CartSerializer


class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        profile, _ = CustomUser.objects.get_or_create(user=self.request.user)
        cart, _ = Cart.objects.get_or_create(user=profile)
        return cart


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
        return Response({"detail": "Product not in cart"}, status=200)