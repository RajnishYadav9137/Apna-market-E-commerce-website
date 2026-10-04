from django.contrib import admin

from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    Wishlist,
    Coupon,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "price", "quantity", "total_price")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "discount",
        "stock",
        "unit",
        "is_available",
        "created_at",
    )
    list_filter = (
        "is_available",
        "category",
        "created_at",
    )
    search_fields = (
        "name",
        "brand",
        "description",
    )
    list_editable = (
        "price",
        "discount",
        "stock",
        "is_available",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tracking_number",
        "full_name",
        "phone",
        "city",
        "total_amount",
        "payment_mode",
        "payment_status",
        "status",
        "created_at",
    )
    list_filter = (
        "status",
        "payment_mode",
        "payment_status",
        "created_at",
    )
    search_fields = (
        "id",
        "tracking_number",
        "full_name",
        "phone",
        "city",
        "pincode",
    )
    list_editable = (
        "status",
        "payment_status",
    )
    inlines = [OrderItemInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "title",
        "verified_purchase",
        "created_at",
    )
    list_filter = (
        "rating",
        "verified_purchase",
        "created_at",
    )
    search_fields = (
        "product__name",
        "user__username",
        "title",
        "comment",
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "created_at",
    )
    search_fields = (
        "user__username",
        "product__name",
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_percent",
        "discount_amount",
        "min_order_value",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "code",
        "description",
    )
    list_editable = (
        "is_active",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "user__username",
        "session_key",
    )