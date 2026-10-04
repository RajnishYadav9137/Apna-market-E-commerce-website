from django.db import models
from catalog.models import Category


class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    unit = models.CharField(
        max_length=30,
        default="piece"
    )

    weight = models.CharField(
        max_length=50,
        blank=True
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def discounted_price(self):
        if self.discount and self.discount > 0:
            discount_amount = (self.price * self.discount) / 100
            return round(self.price - discount_amount, 2)
        return self.price

    @property
    def savings(self):
        if self.discount and self.discount > 0:
            return round((self.price * self.discount) / 100, 2)
        return 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return round(float(avg), 1) if avg else 4.8

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def rating_percentage(self):
        return int((self.average_rating / 5.0) * 100)

    def __str__(self):
        return self.name


class Cart(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts"
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        if self.user:
            return f"Cart - {self.user.username}"

        return f"Guest Cart - {self.session_key}"


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            )
        ]

    @property
    def total_price(self):
        return round(self.product.discounted_price * self.quantity, 2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("packed", "Packed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    PAYMENT_CHOICES = [
        ("cod", "Cash on Delivery (COD)"),
        ("upi", "UPI / QR Code"),
        ("card", "Credit / Debit Card"),
        ("netbanking", "Net Banking"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    payment_mode = models.CharField(
        max_length=30,
        choices=PAYMENT_CHOICES,
        default="cod"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    delivery_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    order_notes = models.TextField(
        blank=True,
        default=""
    )

    tracking_number = models.CharField(
        max_length=50,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def subtotal(self):
        return self.total_amount - self.delivery_charge + self.discount_amount

    @property
    def is_cancellable(self):
        return self.status in ["pending", "confirmed"]

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="product_reviews"
    )

    rating = models.PositiveSmallIntegerField(
        default=5
    )

    title = models.CharField(
        max_length=150,
        blank=True
    )

    comment = models.TextField()

    verified_purchase = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


class Wishlist(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.name}"


class Coupon(models.Model):

    code = models.CharField(
        max_length=30,
        unique=True
    )

    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    description = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def calculate_discount(self, order_amount):
        if not self.is_active:
            return 0
        if order_amount < self.min_order_value:
            return 0
        if self.discount_percent > 0:
            discount = (order_amount * self.discount_percent) / 100
            return round(discount, 2)
        if self.discount_amount > 0:
            return min(self.discount_amount, order_amount)
        return 0

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% / ₹{self.discount_amount} OFF)"