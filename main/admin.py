from django.contrib import admin
from django.contrib.admin import action
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Profile, Category, Product, ProductImage, Tag, ProductTag,
    ProductSpecification, Review, Sale, Banner, Cart, Order, OrderItem,
    DeliverySettings
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()


class UserAdminExtended(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'is_active', 'profile_is_deleted')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__is_deleted')

    @admin.display(boolean=True, description='Deleted')
    def profile_is_deleted(self, obj):
        return getattr(obj, 'profile', None) and obj.profile.is_deleted

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

    def delete_model(self, request, obj):
        profile, _ = Profile.objects_with_deleted.get_or_create(user=obj)
        profile.is_deleted = True
        profile.deleted_at = timezone.now()
        profile.save()
        obj.is_active = False
        obj.save()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)


admin.site.unregister(User)
admin.site.register(User, UserAdminExtended)


@action(description='Restore selected items')
def restore_selected(modeladmin, request, queryset):
    queryset.update(is_deleted=False, deleted_at=None)


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
    actions = [restore_selected]
    list_display = ('title', 'parent', 'is_deleted')
    list_filter = ('parent', 'is_deleted')
    search_fields = ('title',)

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()

    def delete_queryset(self, request, queryset):
        queryset.delete()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [restore_selected]
    list_display = ('title', 'category', 'price', 'count', 'rating', 'limited_edition', 'is_deleted')
    list_filter = ('category', 'limited_edition', 'free_delivery', 'is_deleted')
    search_fields = ('title', 'description')
    list_editable = ('price', 'count', 'limited_edition')
    inlines = [ProductImageInline, ProductTagInline, ProductSpecificationInline, ReviewInline]

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()

    def delete_queryset(self, request, queryset):
        queryset.delete()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    actions = [restore_selected]
    list_display = ('author', 'product', 'rate', 'date', 'is_deleted')
    list_filter = ('rate', 'date', 'is_deleted')
    search_fields = ('author', 'text')

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()

    def delete_queryset(self, request, queryset):
        queryset.delete()


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
    actions = [restore_selected]
    list_display = ('id', 'full_name', 'total_cost', 'status', 'delivery_type', 'created_at', 'is_deleted')
    list_filter = ('status', 'delivery_type', 'payment_type', 'is_deleted')
    search_fields = ('full_name', 'email', 'id')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return self.model.objects_with_deleted.all()

    def delete_queryset(self, request, queryset):
        queryset.delete()


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ('free_delivery_threshold', 'delivery_cost', 'express_delivery_cost')
