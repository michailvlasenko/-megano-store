from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True, unique=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.username


class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    limited_edition = models.BooleanField(default=False)
    sort_index = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.title}"


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'tag')

    def __str__(self):
        return f"{self.product.title} - {self.tag.name}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=255)
    email = models.EmailField()
    text = models.TextField()
    rate = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Review by {self.author}"


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return f"Sale on {self.product.title}"


class Banner(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='banners')
    image = models.ImageField(upload_to='banners/')
    alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Banner for {self.product.title}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product.title} x {self.count}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    DELIVERY_CHOICES = [
        ('free', 'Free'),
        ('express', 'Express'),
    ]
    PAYMENT_CHOICES = [
        ('online_card', 'Online Card'),
        ('online_account', 'Online Account'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='free')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='online_card')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted')
    city = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    payment_error = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.title} x {self.count}"


class DeliverySettings(models.Model):
    free_delivery_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    express_delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=500)

    class Meta:
        verbose_name_plural = 'Delivery settings'

    def __str__(self):
        return f"Delivery settings (free from {self.free_delivery_threshold})"
