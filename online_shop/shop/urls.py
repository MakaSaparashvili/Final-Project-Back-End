from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="categories")
router.register(r"products", views.ProductViewSet, basename="products")
router.register(r"orders", views.OrderViewSet, basename="orders")


urlpatterns = [
    path("", include(router.urls)),

    # User endpoints
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),

    # Cart endpoints
    path("cart/", views.CartView.as_view(), name="cart"),
    path("cart/add/", views.add_to_cart, name="cart-add"),
    path("cart/remove/", views.remove_from_cart, name="cart-remove"),
]
