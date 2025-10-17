from rest_framework import viewsets, generics, filters, status, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import LikeProduct, User, Product
from .serializers import LikeProductSerializer


from .models import User, Category, Product, ProductImage, Order, OrderItem, LikeProduct, ProductRate
from .serializers import (
    UserSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    OrderSerializer,
    OrderItemSerializer,
    LikeProductSerializer,
    ProductRateSerializer, OrderCreateSerializer, OrderItemCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'number': ['exact'],   # faqat aniq mos bo‘lsa qaytaradi
    }


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]

    # Allow filtering by category, price, discount, quantity
    filterset_fields = ['category', 'price', 'discount', 'quantity']

    # Allow searching by product name or description
    search_fields = ['name', 'desc']

    # Allow ordering by price, discount, quantity, created_at
    ordering_fields = ['price', 'discount', 'quantity', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering by final_price manually (since it's not a DB field)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            queryset = [p for p in queryset if p.final_price >= float(min_price)]
        if max_price:
            queryset = [p for p in queryset if p.final_price <= float(max_price)]

        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductRateCreateView(generics.CreateAPIView):
    queryset = ProductRate.objects.all()
    serializer_class = ProductRateSerializer

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related("items__product")
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

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

        try:
            user = User.objects.get(number=user_number)
        except User.DoesNotExist:
            return Response({"error": "User topilmadi!"}, status=404)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product topilmadi!"}, status=404)

        # Like mavjudligini tekshirish
        like, created = LikeProduct.objects.get_or_create(user=user, product=product)
        if not created:
            # Like mavjud bo'lsa o'chirish
            like.delete()
            return Response({"status": "unliked"})
        else:
            # Like saqlandi
            serializer = self.get_serializer(like)
            return Response(serializer.data)


class OrderItemCreateView(CreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemCreateSerializer

class OrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
