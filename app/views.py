from rest_framework import viewsets, generics, filters, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    User, Category, CategoryScroll, Product, ProductImage,
    Order, OrderItem, LikeProduct, ProductRate
)
from .serializers import (
    UserSerializer, CategorySerializer, CategoryScrollSerializer,
    ProductSerializer, ProductImageSerializer,
    OrderSerializer, OrderItemSerializer,
    LikeProductSerializer, ProductRateSerializer,
    OrderCreateSerializer, OrderItemCreateSerializer
)


# 🔹 USER
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'number': ['exact'],
    }


# 🔹 CATEGORY
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# 🔹 CATEGORY SCROLL
class CategoryScrollViewSet(viewsets.ModelViewSet):
    queryset = CategoryScroll.objects.all()
    serializer_class = CategoryScrollSerializer


# 🔹 PRODUCT LIST / CREATE
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all().select_related("category").prefetch_related("images")
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # Filtering fields
    filterset_fields = ['category', 'price', 'quantity']

    # Searching
    search_fields = ['name', 'desc']

    # Ordering
    ordering_fields = ['price', 'quantity', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering by final_price manually
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = [p for p in queryset if float(p.final_price) >= float(min_price)]
        if max_price:
            queryset = [p for p in queryset if float(p.final_price) <= float(max_price)]

        return queryset


# 🔹 PRODUCT DETAIL
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# 🔹 PRODUCT RATE
class ProductRateCreateView(generics.CreateAPIView):
    queryset = ProductRate.objects.all()
    serializer_class = ProductRateSerializer


# 🔹 PRODUCT IMAGE
class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


# 🔹 ORDER
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related("items__product")
    serializer_class = OrderSerializer


# 🔹 ORDER ITEM
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


# 🔹 LIKE PRODUCT
class LikeProductViewSet(viewsets.ModelViewSet):
    queryset = LikeProduct.objects.all()
    serializer_class = LikeProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'user__number': ['exact'],
        'product': ['exact'],
    }

    @action(detail=False, methods=['post'])
    def toggle_like(self, request):
        user_number = request.data.get("user_number")
        product_id = request.data.get("product")

        if not user_number or not product_id:
            return Response({"error": "user_number va product majburiy!"}, status=400)

        # User tekshirish
        try:
            user = User.objects.get(number=user_number)
        except User.DoesNotExist:
            return Response({"error": "User topilmadi!"}, status=404)

        # Product tekshirish
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product topilmadi!"}, status=404)

        # Like mavjudmi?
        like = LikeProduct.objects.filter(user=user, product=product).first()

        if like:
            like.delete()
            likes_count = LikeProduct.objects.filter(product=product).count()
            return Response({
                "status": "unliked",
                "product_id": product.id,
                "likes_count": likes_count
            })
        else:
            like = LikeProduct.objects.create(user=user, product=product)
            serializer = self.get_serializer(like)
            likes_count = LikeProduct.objects.filter(product=product).count()
            return Response({
                "status": "liked",
                "like": serializer.data,
                "likes_count": likes_count
            })


# 🔹 ORDER ITEM CREATE
class OrderItemCreateView(CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemCreateSerializer


# 🔹 ORDER CREATE
class OrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
