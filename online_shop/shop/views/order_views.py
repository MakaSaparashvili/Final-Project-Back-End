from django.db import transaction
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shop.models import Order, OrderItem
from shop.serializers import OrderSerializer


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
            
            if ci.product.stock >= ci.quantity:
                ci.product.stock -= ci.quantity
            else:
                raise serializers.ValidationError(f"Not enough stock for {ci.product.name}")
            ci.product.save()

        order.total_amount = total
        order.save()
        cart.items.all().delete()

        from ..tasks import send_order_confirmation_email
        send_order_confirmation_email.delay(order.id)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)