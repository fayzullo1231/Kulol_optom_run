from rest_framework import serializers
from .models import (
    User, Category, CategoryScroll, Product, ProductImage,
    Order, OrderItem, LikeProduct, ProductRate
)

# 🔹 USER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'number', 'name']


# 🔹 CATEGORY
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'sub_name']  # agar image bo‘lsa qo‘shish mumkin


# 🔹 CATEGORY SCROLL
class CategoryScrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryScroll
        fields = ['id', 'name', 'image']


# 🔹 PRODUCT IMAGE
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


# 🔹 PRODUCT RATE
class ProductRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRate
        fields = ["id", "user_number", "product", "rate", "created_at"]
        read_only_fields = ["id", "created_at"]


# 🔹 PRODUCT
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'desc', 'price', 'quantity',
            'category', 'category_scroll',
            'created_at', 'updated_at',
            'average_rating', 'final_price', 'images'
        ]

    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            return round(sum(r.rate for r in ratings) / ratings.count(), 2)
        return None


# 🔹 ORDER ITEM
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'subtotal']


# 🔹 ORDER
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    user_number = serializers.CharField(source="user.number", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'tracking_code', 'user_number', 'final_price', 'created_at', 'items']

    def get_final_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())


# 🔹 LIKE PRODUCT
class LikeProductSerializer(serializers.ModelSerializer):
    user_number = serializers.CharField(write_only=True, required=True)
    product_id = serializers.IntegerField(write_only=True, required=True)

    user_display = serializers.CharField(source="user.number", read_only=True)
    product_display = serializers.IntegerField(source="product.id", read_only=True)

    class Meta:
        model = LikeProduct
        fields = ['id', 'user_number', 'product_id', 'user_display', 'product_display']

    def create(self, validated_data):
        user_number = validated_data.pop("user_number")
        product_id = validated_data.pop("product_id")

        try:
            user = User.objects.get(number=user_number)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_number": "Bunday foydalanuvchi topilmadi!"})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product_id": "Bunday product topilmadi!"})

        like, created = LikeProduct.objects.get_or_create(user=user, product=product)
        return like


# 🔹 ORDER ITEM CREATE
class OrderItemCreateSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order_id', 'product_id', 'quantity']

    def create(self, validated_data):
        order_id = validated_data.pop('order_id')
        product_id = validated_data.pop('product_id')

        order = Order.objects.get(id=order_id)
        product = Product.objects.get(id=product_id)

        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=validated_data['quantity']
        )
        return item


# 🔹 ORDER CREATE
class OrderCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'tracking_code', 'created_at']
        read_only_fields = ['id']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        order = Order.objects.create(
            user=user,
            tracking_code=f"TRK{user.id}{Order.objects.count() + 1:04d}"  # tracking code avtomatik
        )
        return order
