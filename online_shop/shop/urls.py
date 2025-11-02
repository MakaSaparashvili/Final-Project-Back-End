from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.password_reset_views import PasswordResetRequestAPIView, PasswordResetConfirmAPIView
from .views.auth_views import RegisterView, login_view, ProfileView
from .views.cart_views import CartView, add_to_cart, remove_from_cart
from .views.category_views import CategoryViewSet
from .views.order_views import OrderViewSet
from .views.product_views import ProductViewSet


router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="products")
router.register(r"orders", OrderViewSet, basename="orders")


urlpatterns = [
    path("", include(router.urls)),

    # User endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),

    # Cart endpoints
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/", add_to_cart, name="cart-add"),
    path("cart/remove/", remove_from_cart, name="cart-remove"),

    #Password reset/confirmation endpoints
    path('password-reset-request/', PasswordResetRequestAPIView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(),
         name='password_reset_confirm'),
]

