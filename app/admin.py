from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Category, CategoryScroll,
    Product, ProductImage,
    Order, OrderItem,
    LikeProduct, ProductRate
)


# 🔹 USER
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "number")
    search_fields = ("name", "number")
    ordering = ("id",)


# 🔹 CATEGORY
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "sub_name")
    search_fields = ("sub_name",)


# 🔹 CATEGORY SCROLL
@admin.register(CategoryScroll)
class CategoryScrollAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image_tag")
    search_fields = ("name",)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" '
                'style="object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "❌"
    image_tag.short_description = "Rasm"


# 🔹 PRODUCT IMAGE INLINE
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# 🔹 PRODUCT
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "price", "quantity",
        "category", "category_scroll", "created_at"
    )
    list_filter = ("category", "category_scroll", "created_at")
    search_fields = ("name", "desc")
    inlines = [ProductImageInline]
    ordering = ("-created_at",)


# 🔹 PRODUCT RATE
@admin.register(ProductRate)
class ProductRateAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user_number", "rate", "created_at")
    list_filter = ("rate", "created_at")
    search_fields = ("user_number", "product__name")
    ordering = ("-created_at",)


# 🔹 ORDER
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tracking_code", "final_price", "created_at")
    search_fields = ("user__name", "user__number", "tracking_code")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


# 🔹 ORDER ITEM
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "subtotal")
    search_fields = ("order__tracking_code", "product__name")
    ordering = ("id",)


# 🔹 LIKE PRODUCT
@admin.register(LikeProduct)
class LikeProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
    search_fields = ("user__name", "product__name")
    ordering = ("id",)
