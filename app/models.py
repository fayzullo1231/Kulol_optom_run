from django.conf import settings
from django.db import models

class User(models.Model):
    number = models.CharField(max_length=20, unique=True)  # phone number
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.number})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   # ✅ add this

    @property
    def final_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.rate for r in ratings) / ratings.count(), 2)
        return 0


    def __str__(self):
        return self.name

class ProductRate(models.Model):
    RATE_CHOICES = [(i, str(i)) for i in range(1, 6)]  # ⭐ 1–5 rating

    user_number = models.IntegerField()  # just a number, not FK
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    rate = models.IntegerField(choices=RATE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_number", "product")  #

    def __str__(self):
        return f"User #{self.user_number} rated {self.product} → {self.rate}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)  # cover image

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    number = models.CharField(max_length=20)  # order number / tracking code
    created_at = models.DateTimeField(auto_now_add=True)
    final_price = models.IntegerField(default=0)

    def __str__(self):
        return f"Order #{self.id} - {self.user.name}"




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class LikeProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.name} likes {self.product.name}"
