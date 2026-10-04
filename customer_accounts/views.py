from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.db.models import Sum
from django.shortcuts import redirect, render

from .models import CustomerProfile


def merge_guest_cart(request, user):
    """
    Merge items from guest session cart into user's account cart
    so cart items are preserved upon sign in.
    """
    if not request.session.session_key:
        return
    try:
        from store.models import Cart, CartItem

        guest_cart = Cart.objects.filter(
            session_key=request.session.session_key,
            user=None
        ).first()

        if not guest_cart:
            return

        user_cart, _ = Cart.objects.get_or_create(user=user)

        for item in guest_cart.items.all():
            user_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={"quantity": item.quantity}
            )
            if not created:
                user_item.quantity = min(
                    user_item.quantity + item.quantity,
                    item.product.stock
                )
                user_item.save()

        # Delete guest cart after merge
        guest_cart.delete()
    except Exception:
        pass


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.POST.get("next") or request.GET.get("next") or "home"

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            merge_guest_cart(request, user)
            messages.success(
                request,
                f"Welcome to Apna Market, {user.username}! Your account has been created."
            )
            if next_url and next_url != "home" and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(
        request,
        "customer_accounts/signup.html",
        {"form": form, "next": next_url}
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.POST.get("next") or request.GET.get("next") or "home"

    if request.method == "POST":
        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            merge_guest_cart(request, user)
            messages.success(
                request,
                f"Namaste, {user.first_name or user.username}! You are now logged in."
            )
            if next_url and next_url != "home" and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(
                request,
                "Invalid username or password. Please try again."
            )
    else:
        form = AuthenticationForm()

    return render(
        request,
        "customer_accounts/login.html",
        {"form": form, "next": next_url}
    )


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out of Apna Market.")
    return redirect("home")


# ============================================================
# CUSTOMER PROFILE (View & Update Delivery Address & Personal Details)
# ============================================================

@login_required(login_url="/login/?next=/profile/")
def profile_view(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    from store.models import Order, Wishlist
    orders_count = Order.objects.filter(user=request.user).count()
    total_spent = Order.objects.filter(user=request.user, status__in=["confirmed", "delivered"]).aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal("0.00")
    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        # Update User
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update Profile
        profile.phone = phone
        profile.address = address
        profile.city = city
        profile.state = state
        profile.pincode = pincode
        profile.save()

        messages.success(request, "Your profile and default delivery details have been updated successfully! ✨")
        return redirect("profile")

    return render(
        request,
        "customer_accounts/profile.html",
        {
            "profile": profile,
            "orders_count": orders_count,
            "total_spent": total_spent,
            "wishlist_count": wishlist_count,
        }
    )


# ============================================================
# CHANGE PASSWORD
# ============================================================

@login_required(login_url="/login/")
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "customer_accounts/change_password.html",
        {"form": form}
    )