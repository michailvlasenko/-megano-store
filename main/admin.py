from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Profile, Category, Product, ProductImage, Tag, ProductTag,
    ProductSpecification, Review, Sale, Banner, Cart, Order, OrderItem,
    DeliverySettings
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdminExtended(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdminExtended)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('author', 'email', 'text', 'rate', 'date')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')
    list_filter = ('parent',)
    search_fields = ('title',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'count', 'rating', 'limited_edition')
    list_filter = ('category', 'limited_edition', 'free_delivery')
    search_fields = ('title', 'description')
    list_editable = ('price', 'count', 'limited_edition')
    inlines = [ProductImageInline, ProductTagInline, ProductSpecificationInline, ReviewInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rate', 'date')
    list_filter = ('rate', 'date')
    search_fields = ('author', 'text')


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'sale_price', 'date_from', 'date_to')
    list_filter = ('date_from', 'date_to')
    search_fields = ('product__title',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('product',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'count')
    list_filter = ('user',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'title', 'price', 'count')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_cost', 'status', 'delivery_type', 'created_at')
    list_filter = ('status', 'delivery_type', 'payment_type')
    search_fields = ('full_name', 'email', 'id')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('free_delivery_threshold', 'delivery_cost', 'express_delivery_cost')
