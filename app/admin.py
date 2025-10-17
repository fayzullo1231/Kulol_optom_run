from django.contrib import admin
from .models import User, Category, Product, ProductImage, Order, OrderItem, LikeProduct
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "number")
    search_fields = ("name", "number")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "parent_name", "sub_name", "parent", "image_tag")
    search_fields = ("parent_name", "sub_name")

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" />', obj.image.url)
        return "❌"
    image_tag.short_description = "Rasm"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "discount", "quantity", "category", "created_at")
    list_filter = ("category",)
    search_fields = ("name", "desc")
    inlines = [ProductImageInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "number", "created_at")
    search_fields = ("user__name", "number")
    list_filter = ("created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity")
    search_fields = ("order__id", "product__name")


@admin.register(LikeProduct)
class LikeProductAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
    search_fields = ("user__name", "product__name")
