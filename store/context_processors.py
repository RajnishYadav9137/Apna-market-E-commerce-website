from django.db.models import Count, Q
from catalog.models import Category
from store.models import Cart, Wishlist, Coupon


def cart_and_categories_context(request):
    """
    Context processor providing cart statistics, wishlist count, active coupons,
    and categories globally to all templates.
    """
    cart_count = 0
    cart_total = 0
    wishlist_count = 0
    user_wishlist_ids = []
    nav_categories = []
    active_coupons = []

    try:
        nav_categories = list(
            Category.objects.filter(
                parent=None,
                is_active=True
            ).annotate(
                prod_count=Count('products', filter=Q(products__is_available=True)) +
                           Count('subcategories__products', filter=Q(subcategories__products__is_available=True))
            ).order_by("-prod_count", "name")[:12]
        )
    except Exception:
        pass

    try:
        active_coupons = list(
            Coupon.objects.filter(is_active=True).order_by("-discount_percent")[:4]
        )
    except Exception:
        pass

    try:
        if request.user.is_authenticated:
            wishlist_items = Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)
            user_wishlist_ids = list(wishlist_items)
            wishlist_count = len(user_wishlist_ids)
    except Exception:
        pass

    try:
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(
                session_key=request.session.session_key,
                user=None
            ).first()

        if cart:
            items = cart.items.select_related("product").all()
            for item in items:
                cart_count += int(item.quantity)
                cart_total += item.total_price
    except Exception:
        pass

    return {
        "global_cart_count": cart_count,
        "global_cart_total": cart_total,
        "global_wishlist_count": wishlist_count,
        "user_wishlist_ids": user_wishlist_ids,
        "nav_categories": nav_categories,
        "active_coupons": active_coupons,
    }
