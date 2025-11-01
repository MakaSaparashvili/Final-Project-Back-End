from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from shop.models import Category
from shop.serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]