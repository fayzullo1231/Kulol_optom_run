from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    CategoryViewSet,
    ProductListCreateView,
    ProductDetailView,
    ProductImageViewSet,
    OrderViewSet,
    OrderItemViewSet,
    LikeProductViewSet,
    ProductRateCreateView, OrderCreateView, OrderItemCreateView, CategoryScrollViewSet
)

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("categories", CategoryViewSet)
router.register("images", ProductImageViewSet)
router.register("orders", OrderViewSet)
router.register("order-items", OrderItemViewSet)
router.register("likes", LikeProductViewSet)

router.register("category-scrolls", CategoryScrollViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('create-order/', OrderCreateView.as_view(), name='create-order'),
    path('create-order_item/', OrderItemCreateView.as_view(), name='create-order_item'),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("ratings/", ProductRateCreateView.as_view(), name="rating-create"),
]

