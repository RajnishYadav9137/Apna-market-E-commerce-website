from decimal import Decimal
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Category
from .models import Cart, CartItem, Coupon, Order, OrderItem, Product, Review, Wishlist


# ============================================================
# HELPER: GET OR CREATE ACTIVE CART
# ============================================================

def get_cart(request):
    """
    Returns active cart for authenticated user or anonymous session.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        user=None
    )
    return cart


# ============================================================
# HOME PAGE (With Multi-Criteria Search, Filters & Curation)
# ============================================================

def home(request):
    search_query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "featured")
    selected_cat = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    in_stock_only = request.GET.get("in_stock", "").strip()
    discount_filter = request.GET.get("discount", "").strip()

    categories = Category.objects.filter(
        parent=None,
        is_active=True
    ).order_by("name")

    products_qs = Product.objects.filter(
        is_available=True
    ).select_related("category").prefetch_related("reviews")

    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    if selected_cat:
        products_qs = products_qs.filter(
            Q(category__slug=selected_cat) |
            Q(category__parent__slug=selected_cat)
        )

    if in_stock_only == "1":
        products_qs = products_qs.filter(stock__gt=0)

    if min_price:
        try:
            products_qs = products_qs.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products_qs = products_qs.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    if discount_filter:
        try:
            products_qs = products_qs.filter(discount__gte=Decimal(discount_filter))
        except Exception:
            pass

    # Sorting
    if sort == "price_asc":
        products_qs = products_qs.order_by("price")
    elif sort == "price_desc":
        products_qs = products_qs.order_by("-price")
    elif sort == "discount":
        products_qs = products_qs.order_by("-discount")
    elif sort == "newest":
        products_qs = products_qs.order_by("-created_at")
    elif sort == "rating":
        products_qs = products_qs.annotate(avg_r=Avg("reviews__rating")).order_by("-avg_r", "-created_at")
    else:  # featured
        products_qs = products_qs.order_by("-id")

    products = list(products_qs[:36])

    # Build Category-Wise Showcase Sections (Agriculture, Beauty, Electronics, Kirana, etc.)
    category_meta = {
        "grocery-kirana": {
            "icon": "🌾",
            "tagline": "Chakki atta, basmati rice, dals, pure spices & daily kitchen staples",
            "color": "#ea580c",
        },
        "fruits-vegetables": {
            "icon": "🥦",
            "tagline": "Farm-fresh handpicked veggies & seasonal fresh fruits directly from mandis",
            "color": "#16a34a",
        },
        "dairy-fresh-products": {
            "icon": "🥛",
            "tagline": "Pure pouch milk, fresh paneer, curd, table butter & desi cow ghee",
            "color": "#0284c7",
        },
        "agriculture-gardening": {
            "icon": "🌱",
            "tagline": "Organic kitchen garden seeds, farm trowels & gardening essentials",
            "color": "#15803d",
        },
        "beauty-personal-care": {
            "icon": "💄",
            "tagline": "Herbal soaps, pure coconut hair oil, skincare & personal wellness",
            "color": "#db2777",
        },
        "electronics-mobile-accessories": {
            "icon": "⚡",
            "tagline": "High-speed chargers, TWS wireless earbuds & durable braided cables",
            "color": "#2563eb",
        },
        "desi-mitti-handicrafts": {
            "icon": "🏺",
            "tagline": "Handcrafted earthen clay matkas, chai kulhads & festive terracotta diyas",
            "color": "#9a3412",
        },
        "puja-religious-items": {
            "icon": "🪔",
            "tagline": "Temple fragrance agarbatti, pure brass puja thali sets & holy samagri",
            "color": "#b45309",
        },
        "clothes-fashion-category": {
            "icon": "👗",
            "tagline": "Traditional Kanjivaram silk sarees & royal Lucknowi Chikankari kurtas",
            "color": "#7c3aed",
        },
        "kitchen-utensils": {
            "icon": "🍳",
            "tagline": "Heavy-gauge stainless steel kadhais, pressure cookers & cookware",
            "color": "#334155",
        },
        "books-stationery": {
            "icon": "📚",
            "tagline": "Classmate spiral registers, premium rollerball pens & bestselling books",
            "color": "#0d9488",
        },
        "footwear": {
            "icon": "👟",
            "tagline": "Comfort daily walking shoes, pastel sneakers & ergonomic women sandals",
            "color": "#4f46e5",
        },
    }

    preferred_order = [
        "grocery-kirana",
        "fruits-vegetables",
        "dairy-fresh-products",
        "agriculture-gardening",
        "beauty-personal-care",
        "electronics-mobile-accessories",
        "books-stationery",
        "footwear",
        "desi-mitti-handicrafts",
        "puja-religious-items",
        "clothes-fashion-category",
        "kitchen-utensils",
    ]

    all_parent_cats = {c.slug: c for c in Category.objects.filter(parent=None, is_active=True)}
    category_sections = []

    for c_slug in preferred_order:
        cat_obj = all_parent_cats.get(c_slug)
        if not cat_obj:
            continue
        sub_ids = list(cat_obj.subcategories.values_list("id", flat=True))
        all_cat_ids = [cat_obj.id] + sub_ids
        cat_products = list(
            Product.objects.filter(
                category_id__in=all_cat_ids,
                is_available=True
            ).select_related("category").prefetch_related("reviews")[:8]
        )
        if cat_products:
            meta = category_meta.get(c_slug, {
                "icon": "🏷️",
                "tagline": f"Best quality {cat_obj.name} products",
                "color": "#ff6b00"
            })
            category_sections.append({
                "category": cat_obj,
                "slug": cat_obj.slug,
                "name": cat_obj.name,
                "icon": meta["icon"],
                "tagline": meta["tagline"],
                "color": meta["color"],
                "products": cat_products,
                "count": len(cat_products),
            })

    # Deal products for the top savings showcase
    deal_products = Product.objects.filter(
        is_available=True,
        discount__gte=10,
        stock__gt=0
    ).select_related("category").order_by("-discount")[:8]

    return render(
        request,
        "store/home.html",
        {
            "categories": categories,
            "category_sections": category_sections,
            "products": products,
            "deal_products": deal_products,
            "search_query": search_query,
            "sort": sort,
            "selected_category": selected_cat,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock_only,
            "discount_filter": discount_filter,
            "total_results": len(products),
        }
    )


# ============================================================
# CATEGORY PRODUCTS
# ============================================================

def category_products(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    subcategories = category.subcategories.filter(
        is_active=True
    ).order_by("name")

    category_ids = [category.id] + list(
        subcategories.values_list("id", flat=True)
    )

    selected_subcat = request.GET.get("sub", "").strip()
    if selected_subcat:
        try:
            sub_obj = subcategories.get(slug=selected_subcat)
            category_ids = [sub_obj.id]
        except Category.DoesNotExist:
            pass

    sort = request.GET.get("sort", "newest")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    in_stock_only = request.GET.get("in_stock", "").strip()
    search_query = request.GET.get("q", "").strip()

    products_qs = Product.objects.filter(
        category_id__in=category_ids,
        is_available=True
    ).select_related("category").prefetch_related("reviews")

    if search_query:
        products_qs = products_qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__icontains=search_query)
        )

    if in_stock_only == "1":
        products_qs = products_qs.filter(stock__gt=0)

    if min_price:
        try:
            products_qs = products_qs.filter(price__gte=Decimal(min_price))
        except Exception:
            pass

    if max_price:
        try:
            products_qs = products_qs.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    if sort == "price_asc":
        products_qs = products_qs.order_by("price")
    elif sort == "price_desc":
        products_qs = products_qs.order_by("-price")
    elif sort == "discount":
        products_qs = products_qs.order_by("-discount")
    elif sort == "rating":
        products_qs = products_qs.annotate(avg_r=Avg("reviews__rating")).order_by("-avg_r", "-created_at")
    else:
        products_qs = products_qs.order_by("-created_at")

    products = list(products_qs)

    return render(
        request,
        "store/category.html",
        {
            "category": category,
            "subcategories": subcategories,
            "selected_subcat": selected_subcat,
            "products": products,
            "sort": sort,
            "search_query": search_query,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock_only,
            "total_results": len(products),
        }
    )


# ============================================================
# PRODUCT DETAIL (Reviews, Rating Breakdown, Wishlist & Stock)
# ============================================================

def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(
        id=product.id
    ).order_by("-created_at")[:6]

    reviews = product.reviews.select_related("user").order_by("-created_at")
    review_count = reviews.count()
    avg_rating = product.average_rating

    # Calculate rating distribution (5, 4, 3, 2, 1 stars)
    star_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        if r.rating in star_distribution:
            star_distribution[r.rating] += 1

    star_percentages = {}
    for star, count in star_distribution.items():
        pct = int((count / review_count * 100)) if review_count > 0 else 0
        star_percentages[star] = {"count": count, "percent": pct}

    # Check if logged-in user is a verified buyer of this product
    user_has_purchased = False
    is_in_wishlist = False
    user_review = None

    if request.user.is_authenticated:
        user_has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

        is_in_wishlist = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

        user_review = reviews.filter(user=request.user).first()

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
            "reviews": reviews,
            "review_count": review_count,
            "avg_rating": avg_rating,
            "star_percentages": star_percentages,
            "user_has_purchased": user_has_purchased,
            "is_in_wishlist": is_in_wishlist,
            "user_review": user_review,
        }
    )


# ============================================================
# LIVE SEARCH AUTOCOMPLETE (JSON API)
# ============================================================

def api_search_suggestions(request):
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})

    products = Product.objects.filter(
        is_available=True
    ).filter(
        Q(name__icontains=q) |
        Q(brand__icontains=q) |
        Q(category__name__icontains=q)
    ).select_related("category")[:6]

    results = []
    for p in products:
        results.append({
            "id": p.id,
            "name": p.name,
            "category": p.category.name,
            "price": str(p.discounted_price),
            "original_price": str(p.price) if p.discount > 0 else None,
            "discount": int(p.discount) if p.discount > 0 else 0,
            "image": p.image.url if p.image else None,
            "url": f"/product/{p.id}/"
        })

    return JsonResponse({"results": results})


# ============================================================
# PINCODE DELIVERY ESTIMATOR (JSON API)
# ============================================================

def api_check_pincode(request):
    pincode = request.GET.get("pincode", "").strip()
    if not pincode.isdigit() or len(pincode) != 6:
        return JsonResponse({
            "valid": False,
            "message": "Please enter a valid 6-digit Indian PIN code."
        })

    # Standard fast delivery simulation for Indian pincodes
    return JsonResponse({
        "valid": True,
        "pincode": pincode,
        "delivery_time": "⚡ Delivery by Tomorrow, 6:00 PM",
        "cod_available": True,
        "express_available": True,
        "message": f"Great news! Superfast neighborhood delivery is available for {pincode}."
    })


# ============================================================
# ADD TO CART (With AJAX & Standard HTTP Support)
# ============================================================

def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    cart = get_cart(request)

    try:
        quantity = int(
            request.POST.get("quantity") or
            request.GET.get("quantity") or
            1
        )
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    stock = int(product.stock)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("ajax") == "1"

    if stock <= 0:
        if is_ajax:
            return JsonResponse({
                "success": False,
                "message": f"Sorry, '{product.name}' is currently out of stock."
            }, status=400)
        messages.error(
            request,
            f"Sorry, '{product.name}' is currently out of stock."
        )
        return redirect("product_detail", product_id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 0}
    )

    new_quantity = int(cart_item.quantity) + quantity

    if new_quantity > stock:
        cart_item.quantity = stock
        msg = f"Only {stock} units available. Cart quantity set to maximum stock."
        msg_type = "warning"
    else:
        cart_item.quantity = new_quantity
        msg = f"Added {quantity} × '{product.name}' to your cart! 🛒"
        msg_type = "success"

    cart_item.save()

    total_cart_count = sum(int(item.quantity) for item in cart.items.all())

    if is_ajax:
        return JsonResponse({
            "success": True,
            "message": msg,
            "cart_count": total_cart_count,
            "item_id": cart_item.id,
            "product_name": product.name
        })

    if msg_type == "warning":
        messages.warning(request, msg)
    else:
        messages.success(request, msg)

    buy_now = request.POST.get("buy_now") or request.GET.get("buy_now")
    if buy_now:
        return redirect("checkout")

    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)

    referer = request.META.get("HTTP_REFERER")
    if referer and "product" in referer:
        return redirect(referer)

    return redirect("cart")


# ============================================================
# CART VIEW (Items, Free Delivery Bar, Coupons & Breakdown)
# ============================================================

def cart(request):
    cart = get_cart(request)

    items = cart.items.select_related(
        "product",
        "product__category"
    ).all()

    subtotal = Decimal("0.00")
    total_savings = Decimal("0.00")
    original_total = Decimal("0.00")

    for item in items:
        subtotal += Decimal(str(item.total_price))
        original_price = item.product.price * item.quantity
        original_total += original_price
        savings = (original_price - item.total_price)
        if savings > 0:
            total_savings += savings

    # Coupon Processing
    applied_coupon_code = request.session.get("coupon_code")
    coupon_obj = None
    coupon_discount = Decimal("0.00")

    if applied_coupon_code:
        try:
            coupon = Coupon.objects.get(code=applied_coupon_code, is_active=True)
            calculated = coupon.calculate_discount(subtotal)
            if calculated > 0:
                coupon_obj = coupon
                coupon_discount = Decimal(str(calculated))
                total_savings += coupon_discount
            else:
                # Minimum order criteria not met
                request.session.pop("coupon_code", None)
                messages.info(request, f"Coupon '{applied_coupon_code}' requires a minimum order of ₹{coupon.min_order_value}.")
        except Coupon.DoesNotExist:
            request.session.pop("coupon_code", None)

    # Free delivery logic: Free if subtotal >= 499 or FREESHIP coupon applied
    free_delivery_threshold = Decimal("499.00")
    if subtotal >= free_delivery_threshold or subtotal == 0 or (coupon_obj and coupon_obj.code == "FREESHIP"):
        delivery_charge = Decimal("0.00")
        amount_needed_for_free = Decimal("0.00")
    else:
        delivery_charge = Decimal("40.00")
        amount_needed_for_free = free_delivery_threshold - subtotal

    final_total = max(Decimal("0.00"), subtotal - coupon_discount + delivery_charge)

    # Available coupons to display in cart
    available_coupons = Coupon.objects.filter(is_active=True).order_by("-discount_percent")

    return render(
        request,
        "store/cart.html",
        {
            "cart": cart,
            "items": items,
            "subtotal": subtotal,
            "original_total": original_total,
            "total_savings": total_savings,
            "coupon_discount": coupon_discount,
            "applied_coupon": coupon_obj,
            "available_coupons": available_coupons,
            "delivery_charge": delivery_charge,
            "free_delivery_threshold": free_delivery_threshold,
            "amount_needed_for_free": amount_needed_for_free,
            "final_total": final_total,
        }
    )


# ============================================================
# APPLY & REMOVE COUPON
# ============================================================

def apply_coupon(request):
    if request.method != "POST":
        return redirect("cart")

    code = request.POST.get("coupon_code", "").strip().upper()
    cart = get_cart(request)
    subtotal = sum(Decimal(str(item.total_price)) for item in cart.items.all())

    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        if subtotal < coupon.min_order_value:
            messages.warning(
                request,
                f"Coupon '{code}' requires a minimum cart total of ₹{coupon.min_order_value}. Add more items to apply!"
            )
            return redirect("cart")

        request.session["coupon_code"] = coupon.code
        messages.success(request, f"🎉 Coupon '{code}' applied successfully!")
    except Coupon.DoesNotExist:
        messages.error(request, f"Invalid coupon code '{code}'. Please try again.")

    return redirect("cart")


def remove_coupon(request):
    if "coupon_code" in request.session:
        del request.session["coupon_code"]
        messages.info(request, "Coupon removed from your cart.")
    return redirect("cart")


# ============================================================
# UPDATE CART QUANTITY
# ============================================================

def update_cart(request, item_id):
    if request.method != "POST":
        return redirect("cart")

    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    action = request.POST.get("action")
    stock = int(item.product.stock)

    if action == "increase":
        new_qty = int(item.quantity) + 1
    elif action == "decrease":
        new_qty = int(item.quantity) - 1
    else:
        try:
            new_qty = int(request.POST.get("quantity", item.quantity))
        except (TypeError, ValueError):
            new_qty = int(item.quantity)

    if new_qty <= 0:
        name = item.product.name
        item.delete()
        messages.info(request, f"Removed '{name}' from your cart.")
        return redirect("cart")

    if new_qty > stock:
        messages.warning(
            request,
            f"Only {stock} units of '{item.product.name}' are available."
        )
        new_qty = stock

    item.quantity = new_qty
    item.save()
    messages.success(request, f"Updated quantity for '{item.product.name}'.")
    return redirect("cart")


# ============================================================
# REMOVE ITEM FROM CART
# ============================================================

def remove_from_cart(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = item.product.name
    item.delete()
    messages.info(request, f"'{name}' was removed from your cart.")
    return redirect("cart")


# ============================================================
# CLEAR ENTIRE CART
# ============================================================

def clear_cart(request):
    cart = get_cart(request)
    cart.items.all().delete()
    if "coupon_code" in request.session:
        del request.session["coupon_code"]
    messages.info(request, "Your shopping cart has been cleared.")
    return redirect("cart")


# ============================================================
# WISHLIST (List, Toggle, Move to Cart)
# ============================================================

@login_required(login_url="/login/?next=/wishlist/")
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product", "product__category").order_by("-created_at")

    return render(
        request,
        "store/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        }
    )


@login_required(login_url="/login/")
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("ajax") == "1"

    existing = Wishlist.objects.filter(user=request.user, product=product).first()
    if existing:
        existing.delete()
        wishlisted = False
        msg = f"Removed '{product.name}' from your Wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        wishlisted = True
        msg = f"Added '{product.name}' to your Wishlist! ❤️"

    total_wishlist = Wishlist.objects.filter(user=request.user).count()

    if is_ajax:
        return JsonResponse({
            "success": True,
            "wishlisted": wishlisted,
            "message": msg,
            "count": total_wishlist
        })

    if wishlisted:
        messages.success(request, msg)
    else:
        messages.info(request, msg)

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("wishlist")


@login_required(login_url="/login/")
def move_wishlist_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    Wishlist.objects.filter(user=request.user, product=product).delete()

    cart = get_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )
    if not created:
        cart_item.quantity = min(cart_item.quantity + 1, product.stock)
        cart_item.save()

    messages.success(request, f"Moved '{product.name}' from Wishlist to Cart! 🛒")
    return redirect("cart")


# ============================================================
# SUBMIT PRODUCT REVIEW
# ============================================================

@login_required(login_url="/login/")
def submit_review(request, product_id):
    if request.method != "POST":
        return redirect("product_detail", product_id=product_id)

    product = get_object_or_404(Product, id=product_id)

    try:
        rating = int(request.POST.get("rating", 5))
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5

    title = request.POST.get("title", "").strip()
    comment = request.POST.get("comment", "").strip()

    if not comment:
        messages.error(request, "Please enter your review text.")
        return redirect("product_detail", product_id=product_id)

    # Check if user actually bought this product
    verified = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()

    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            "rating": rating,
            "title": title,
            "comment": comment,
            "verified_purchase": verified
        }
    )

    messages.success(request, "Thank you! Your verified review has been published. ⭐")
    return redirect("product_detail", product_id=product_id)


# ============================================================
# CHECKOUT & ORDER CREATION
# ============================================================

@login_required(login_url="/login/?next=/checkout/")
def checkout(request):
    cart = get_cart(request)

    items = cart.items.select_related(
        "product",
        "product__category"
    ).all()

    if not items.exists():
        messages.warning(request, "Your cart is empty. Please add items to checkout.")
        return redirect("home")

    subtotal = Decimal("0.00")
    for item in items:
        subtotal += Decimal(str(item.total_price))

    # Coupon validation
    applied_coupon_code = request.session.get("coupon_code")
    coupon_obj = None
    coupon_discount = Decimal("0.00")
    if applied_coupon_code:
        try:
            coupon = Coupon.objects.get(code=applied_coupon_code, is_active=True)
            calculated = coupon.calculate_discount(subtotal)
            if calculated > 0:
                coupon_obj = coupon
                coupon_discount = Decimal(str(calculated))
        except Coupon.DoesNotExist:
            request.session.pop("coupon_code", None)

    # Delivery Charge calculation
    if subtotal >= Decimal("499.00") or (coupon_obj and coupon_obj.code == "FREESHIP"):
        delivery_charge = Decimal("0.00")
    else:
        delivery_charge = Decimal("40.00")

    final_total = max(Decimal("0.00"), subtotal - coupon_discount + delivery_charge)

    # Pre-fill address from customer profile or last order
    profile = getattr(request.user, "profile", None)
    last_order = Order.objects.filter(user=request.user).order_by("-created_at").first()

    initial_data = {
        "full_name": request.user.get_full_name() or request.user.username,
        "phone": (profile and profile.phone) or (last_order and last_order.phone) or "",
        "address": (profile and profile.address) or (last_order and last_order.address) or "",
        "city": (profile and profile.city) or (last_order and last_order.city) or "",
        "state": (profile and profile.state) or (last_order and last_order.state) or "",
        "pincode": (profile and profile.pincode) or (last_order and last_order.pincode) or "",
    }

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        payment_mode = request.POST.get("payment_mode", "cod").strip()
        order_notes = request.POST.get("order_notes", "").strip()

        if not all([full_name, phone, address, city, state, pincode]):
            return render(
                request,
                "store/checkout.html",
                {
                    "cart": cart,
                    "items": items,
                    "subtotal": subtotal,
                    "delivery_charge": delivery_charge,
                    "coupon_discount": coupon_discount,
                    "applied_coupon": coupon_obj,
                    "total": final_total,
                    "initial": initial_data,
                    "error": "Please fill in all delivery details completely.",
                }
            )

        # Check stock availability
        for item in items:
            if item.product.stock < item.quantity:
                return render(
                    request,
                    "store/checkout.html",
                    {
                        "cart": cart,
                        "items": items,
                        "subtotal": subtotal,
                        "delivery_charge": delivery_charge,
                        "coupon_discount": coupon_discount,
                        "applied_coupon": coupon_obj,
                        "total": final_total,
                        "initial": initial_data,
                        "error": f"Sorry, '{item.product.name}' only has {int(item.product.stock)} units left in stock.",
                    }
                )

        # Generate unique tracking number
        tracking_num = f"APNA-{uuid.uuid4().hex[:8].upper()}"

        # Atomically create Order and decrement stock
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                session_key=request.session.session_key or "",
                full_name=full_name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                payment_mode=payment_mode,
                payment_status="paid" if payment_mode in ["upi", "card"] else "pending",
                delivery_charge=delivery_charge,
                coupon_code=coupon_obj.code if coupon_obj else None,
                discount_amount=coupon_discount,
                order_notes=order_notes,
                tracking_number=tracking_num,
                total_amount=final_total,
                status="confirmed"
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.discounted_price,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                item.product.stock = max(
                    Decimal("0.00"),
                    item.product.stock - item.quantity
                )
                if item.product.stock <= 0:
                    item.product.is_available = False
                item.product.save()

            # Save address into user profile for future checkouts
            if profile:
                profile.phone = phone
                profile.address = address
                profile.city = city
                profile.state = state
                profile.pincode = pincode
                profile.save()

            # Clear cart and session coupon
            cart.items.all().delete()
            request.session.pop("coupon_code", None)

        messages.success(
            request,
            f"🎉 Congratulations! Your order #{order.id} has been confirmed. Tracking ID: {tracking_num}"
        )
        return redirect("order_success", order_id=order.id)

    return render(
        request,
        "store/checkout.html",
        {
            "cart": cart,
            "items": items,
            "subtotal": subtotal,
            "delivery_charge": delivery_charge,
            "coupon_discount": coupon_discount,
            "applied_coupon": coupon_obj,
            "total": final_total,
            "initial": initial_data,
        }
    )


# ============================================================
# ORDER SUCCESS PAGE
# ============================================================

@login_required(login_url="/login/")
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = order.items.select_related("product").all()

    return render(
        request,
        "store/order_success.html",
        {
            "order": order,
            "items": items,
        }
    )


# ============================================================
# MY ORDERS
# ============================================================

@login_required(login_url="/login/")
def my_orders(request):
    status_filter = request.GET.get("status", "all").strip().lower()

    orders_qs = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items",
        "items__product"
    ).order_by("-created_at")

    if status_filter == "active":
        orders_qs = orders_qs.filter(status__in=["pending", "confirmed", "packed", "shipped"])
    elif status_filter == "delivered":
        orders_qs = orders_qs.filter(status="delivered")
    elif status_filter == "cancelled":
        orders_qs = orders_qs.filter(status="cancelled")

    orders = list(orders_qs)

    return render(
        request,
        "store/my_orders.html",
        {
            "orders": orders,
            "status_filter": status_filter,
            "total_orders_count": Order.objects.filter(user=request.user).count()
        }
    )


# ============================================================
# ORDER TAX INVOICE (Printable View)
# ============================================================

@login_required(login_url="/login/")
def order_invoice(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = order.items.select_related("product").all()

    return render(
        request,
        "store/order_invoice.html",
        {
            "order": order,
            "items": items,
        }
    )


# ============================================================
# CANCEL ORDER
# ============================================================

@login_required(login_url="/login/")
def cancel_order(request, order_id):
    if request.method != "POST":
        return redirect("my_orders")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    if order.status in ["pending", "confirmed"]:
        with transaction.atomic():
            for item in order.items.all():
                if item.product:
                    item.product.stock += item.quantity
                    item.product.is_available = True
                    item.product.save()

            order.status = "cancelled"
            order.save()

        messages.info(
            request,
            f"Order #{order.id} has been cancelled and items returned to inventory."
        )
    else:
        messages.warning(
            request,
            f"Order #{order.id} cannot be cancelled because it is already {order.status}."
        )

    return redirect("my_orders")