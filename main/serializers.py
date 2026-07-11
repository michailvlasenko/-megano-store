from rest_framework import serializers
from .models import (
    Category, Product, ProductImage, Tag, ProductTag,
    ProductSpecification, Review, Sale, Banner, Cart, Order, OrderItem, Profile
)


class ImageSerializer(serializers.Serializer):
    src = serializers.CharField()
    alt = serializers.CharField()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'subcategories')

    def get_image(self, obj):
        if obj.image:
            return {'src': obj.image.url, 'alt': obj.image_alt}
        return {'src': '', 'alt': ''}

    def get_subcategories(self, obj):
        subs = Category.objects.filter(parent=obj)
        return CategorySerializer(subs, many=True, context=self.context).data


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.CharField(source='image.url')
    alt = serializers.CharField()

    class Meta:
        model = ProductImage
        fields = ('src', 'alt')


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('name', 'value')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('author', 'email', 'text', 'rate', 'date')
        read_only_fields = ('date',)


class ProductShortSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(source='category_id')
    images = ProductImageSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    freeDelivery = serializers.BooleanField(source='free_delivery')
    date = serializers.DateTimeField()

    class Meta:
        model = Product
        fields = ('id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'freeDelivery', 'images', 'tags', 'reviews', 'rating')

    def get_tags(self, obj):
        return [{'id': pt.tag_id, 'name': pt.tag.name} for pt in obj.tags.select_related('tag')]

    def get_reviews(self, obj):
        return obj.reviews.count()

    def get_rating(self, obj):
        return float(obj.rating)


class ProductFullSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(source='category_id')
    images = ProductImageSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    freeDelivery = serializers.BooleanField(source='free_delivery')
    fullDescription = serializers.CharField(source='full_description')
    date = serializers.DateTimeField()

    class Meta:
        model = Product
        fields = ('id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'fullDescription', 'freeDelivery', 'images',
                  'tags', 'reviews', 'specifications', 'rating')

    def get_tags(self, obj):
        return [pt.tag_id for pt in obj.tags.select_related('tag')]

    def get_rating(self, obj):
        return float(obj.rating)


class SaleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product_id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    salePrice = serializers.DecimalField(source='sale_price', max_digits=10, decimal_places=2)
    title = serializers.CharField(source='product.title')
    dateFrom = serializers.DateField(source='date_from')
    dateTo = serializers.DateField(source='date_to')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ('id', 'price', 'salePrice', 'dateFrom', 'dateTo', 'title', 'images')

    def get_images(self, obj):
        images = obj.product.images.all()
        return ProductImageSerializer(images, many=True, context=self.context).data


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('product', 'image', 'alt')


class CartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_id')
    category = serializers.IntegerField(source='product.category_id', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    title = serializers.CharField(source='product.title', read_only=True)
    description = serializers.CharField(source='product.description', read_only=True)
    freeDelivery = serializers.BooleanField(source='product.free_delivery', read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateTimeField(source='product.date', read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'freeDelivery', 'images', 'tags', 'reviews', 'rating')

    def get_images(self, obj):
        images = obj.product.images.all()
        return ProductImageSerializer(images, many=True, context=self.context).data

    def get_tags(self, obj):
        return [{'id': pt.tag_id, 'name': pt.tag.name} for pt in obj.product.tags.select_related('tag')]

    def get_reviews(self, obj):
        return obj.product.reviews.count()

    def get_rating(self, obj):
        return float(obj.product.rating)


class OrderProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_id')
    category = serializers.IntegerField(source='product.category_id', read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(source='product.description', read_only=True)
    freeDelivery = serializers.BooleanField(source='product.free_delivery', read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    reviews = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)
    date = serializers.DateTimeField(source='product.date', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'category', 'price', 'count', 'date', 'title',
                  'description', 'freeDelivery', 'images', 'tags', 'reviews', 'rating')

    def get_images(self, obj):
        images = obj.product.images.all()
        return ProductImageSerializer(images, many=True, context=self.context).data

    def get_tags(self, obj):
        return [{'id': pt.tag_id, 'name': pt.tag.name} for pt in obj.product.tags.select_related('tag')]

    def get_reviews(self, obj):
        return obj.product.reviews.count()

    def get_rating(self, obj):
        return float(obj.product.rating)


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    createdAt = serializers.DateTimeField(source='created_at')
    fullName = serializers.CharField(source='full_name')
    deliveryType = serializers.CharField(source='delivery_type')
    paymentType = serializers.CharField(source='payment_type')
    totalCost = serializers.DecimalField(source='total_cost', max_digits=10, decimal_places=2)

    class Meta:
        model = Order
        fields = ('id', 'createdAt', 'fullName', 'email', 'phone',
                  'deliveryType', 'paymentType', 'totalCost', 'status',
                  'city', 'address', 'products')


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None

    def get_avatar(self, obj):
        profile = getattr(obj, 'profile', None)
        if profile and profile.avatar:
            return {'src': profile.avatar.url, 'alt': 'avatar'}
        return {'src': '', 'alt': ''}
