from rest_framework import serializers
from .models import User, Category, Product, ProductImage, Order, OrderItem, LikeProduct, ProductRate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'number', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRate
        fields = ["id", "user_number", "product", "rate", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)  # shu qo‘shildi
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'desc', 'price', 'discount', 'quantity',
            'category', 'created_at', 'updated_at',
            'average_rating', 'final_price', 'images'  # images qo‘shildi
        ]


    def get_user_rating(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            rating = obj.ratings.filter(user=user).first()
            return rating.rate if rating else None
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'number', 'final_price', 'created_at', 'items']

    def get_final_price(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())

class LikeProductSerializer(serializers.ModelSerializer):
    # foydalanuvchi raqamini yozish uchun
    user_number = serializers.CharField(write_only=True, required=True)
    # product id yuborish uchun
    product_id = serializers.IntegerField(write_only=True, required=True)

    # o‘qishda qulay bo‘lishi uchun ham qaytaramiz
    user_display = serializers.CharField(source="user.number", read_only=True)
    product_display = serializers.IntegerField(source="product.id", read_only=True)

    class Meta:
        model = LikeProduct
        fields = ['id', 'user_number', 'product_id', 'user_display', 'product_display']

    def create(self, validated_data):
        user_number = validated_data.pop("user_number")
        product_id = validated_data.pop("product_id")

        from django.contrib.auth import get_user_model
        User = get_user_model()

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


from rest_framework import serializers
from .models import Order, OrderItem


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
            quantity = validated_data['quantity']
        )

        order.final_price += item.subtotal
        order.save()

        return item



class OrderCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user_id', 'number', 'created_at']
        read_only_fields = ['id', 'user_id']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)

        order = Order.objects.create(
            user=user,
            number=user.number,
        )
        return order
