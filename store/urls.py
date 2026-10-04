from django.urls import path

from .views import (
    home,
    category_products,
    product_detail,
    api_search_suggestions,
    api_check_pincode,
    add_to_cart,
    cart,
    update_cart,
    remove_from_cart,
    clear_cart,
    apply_coupon,
    remove_coupon,
    wishlist_view,
    toggle_wishlist,
    move_wishlist_to_cart,
    submit_review,
    checkout,
    order_success,
    my_orders,
    order_invoice,
    cancel_order,
)


urlpatterns = [

    # =========================
    # HOME & SEARCH
    # =========================

    path(
        "",
        home,
        name="home"
    ),

    path(
        "api/search-suggestions/",
        api_search_suggestions,
        name="api_search_suggestions"
    ),

    path(
        "api/check-pincode/",
        api_check_pincode,
        name="api_check_pincode"
    ),


    # =========================
    # CATEGORY
    # =========================

    path(
        "category/<slug:slug>/",
        category_products,
        name="category_products"
    ),


    # =========================
    # PRODUCT DETAIL & REVIEWS
    # =========================

    path(
        "product/<int:product_id>/",
        product_detail,
        name="product_detail"
    ),

    path(
        "product/<int:product_id>/review/",
        submit_review,
        name="submit_review"
    ),


    # =========================
    # WISHLIST ACTIONS
    # =========================

    path(
        "wishlist/",
        wishlist_view,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        toggle_wishlist,
        name="toggle_wishlist"
    ),

    path(
        "wishlist/move-to-cart/<int:product_id>/",
        move_wishlist_to_cart,
        name="move_wishlist_to_cart"
    ),


    # =========================
    # CART ACTIONS
    # =========================

    path(
        "cart/add/<int:product_id>/",
        add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/",
        cart,
        name="cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        update_cart,
        name="update_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/clear/",
        clear_cart,
        name="clear_cart"
    ),

    path(
        "cart/apply-coupon/",
        apply_coupon,
        name="apply_coupon"
    ),

    path(
        "cart/remove-coupon/",
        remove_coupon,
        name="remove_coupon"
    ),


    # =========================
    # CHECKOUT & ORDER
    # =========================

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),

    path(
        "order-success/<int:order_id>/",
        order_success,
        name="order_success"
    ),

    path(
        "my-orders/",
        my_orders,
        name="my_orders"
    ),

    path(
        "order/invoice/<int:order_id>/",
        order_invoice,
        name="order_invoice"
    ),

    path(
        "order/cancel/<int:order_id>/",
        cancel_order,
        name="cancel_order"
    ),

]