from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, F, Value
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import (
    Category, Product, Review, Sale, Banner, Cart, Order, OrderItem, Profile, DeliverySettings
)
from .serializers import (
    CategorySerializer, ProductShortSerializer, ProductFullSerializer,
    SaleSerializer, ReviewSerializer, CartSerializer, OrderSerializer
)
import json
from decimal import Decimal
from django.db.models import Avg
from django.utils import timezone
from .serializers import TagSerializer


def get_cart_items(user, session_key):
    if user.is_authenticated:
        return Cart.objects.filter(user=user).select_related('product__category')
    return Cart.objects.filter(session_key=session_key).select_related('product__category')


def get_or_create_cart_item(user, session_key, product_id):
    if user.is_authenticated:
        item, _ = Cart.objects.get_or_create(user=user, product_id=product_id)
    else:
        item, _ = Cart.objects.get_or_create(session_key=session_key, product_id=product_id)
    return item


def update_product_rating(product):
    reviews = product.reviews.all()
    if reviews.exists():
        avg = reviews.aggregate(avg=Avg('rate'))['avg']
        product.rating = round(avg, 2)
        product.save()


def get_request_data(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return request.data


@api_view(['POST'])
def sign_in(request):
    data = get_request_data(request)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'status': 'ok'})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def sign_up(request):
    data = get_request_data(request)
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, full_name=name)
    login(request, user)
    return Response({'status': 'ok'})


@api_view(['POST'])
def sign_out(request):
    logout(request)
    return Response({'status': 'ok'})


@api_view(['GET'])
def categories(request):
    cats = Category.objects.filter(parent__isnull=True)
    serializer = CategorySerializer(cats, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def catalog(request):
    products = Product.objects.all()
    filter_data = request.query_params.get('filter')
    if filter_data:
        try:
            filter_obj = json.loads(filter_data)
        except (json.JSONDecodeError, TypeError):
            filter_obj = {'name': filter_data}
        name = filter_obj.get('name', '')
        if name:
            products = products.filter(title__icontains=name)

    category = request.query_params.get('category')
    if category:
        products = products.filter(category_id=category)

    sort = request.query_params.get('sort', 'date')
    sort_type = request.query_params.get('sortType', 'dec')
    if sort == 'price':
        order = '-' if sort_type == 'dec' else ''
        products = products.order_by(f'{order}price')
    elif sort == 'rating':
        order = '-' if sort_type == 'dec' else ''
        products = products.order_by(f'{order}rating')
    elif sort == 'reviews':
        order = '' if sort_type == 'dec' else '-'
        products = products.annotate(reviews_count=Count('reviews')).order_by(f'{order}reviews_count')
    elif sort == 'date':
        order = '-' if sort_type == 'dec' else ''
        products = products.order_by(f'{order}date')

    limit = int(request.query_params.get('limit', 20))
    page = int(request.query_params.get('currentPage', 1))
    start = (page - 1) * limit
    end = start + limit
    total = products.count()
    last_page = (total + limit - 1) // limit

    page_products = products[start:end]
    serializer = ProductShortSerializer(page_products, many=True, context={'request': request})
    return Response({
        'items': serializer.data,
        'currentPage': page,
        'lastPage': last_page,
    })


@api_view(['GET'])
def products_popular(request):
    products = Product.objects.all().order_by('-sort_index', '-rating')[:8]
    serializer = ProductShortSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def products_limited(request):
    products = Product.objects.filter(limited_edition=True)[:16]
    serializer = ProductShortSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def sales(request):
    now = timezone.now().date()
    sales_qs = Sale.objects.filter(date_from__lte=now, date_to__gte=now)
    page = int(request.query_params.get('currentPage', 1))
    limit = 20
    start = (page - 1) * limit
    end = start + limit
    total = sales_qs.count()
    last_page = (total + limit - 1) // limit
    serializer = SaleSerializer(sales_qs[start:end], many=True, context={'request': request})
    return Response({
        'items': serializer.data,
        'currentPage': page,
        'lastPage': last_page,
    })


@api_view(['GET'])
def banners(request):
    banners_qs = Banner.objects.all()
    serializer = ProductShortSerializer(
        [b.product for b in banners_qs.select_related('product')],
        many=True, context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
def product_detail(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductFullSerializer(product, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
def product_review(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(product=product)
        update_product_rating(product)
        reviews = product.reviews.all()
        return Response(ReviewSerializer(reviews, many=True).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
def basket(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    if request.method == 'GET':
        items = get_cart_items(request.user, session_key)
        serializer = CartSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    product_id = request.data.get('id')
    count = request.data.get('count', 1)

    if request.method == 'POST':
        item = get_or_create_cart_item(request.user, session_key, product_id)
        item.count += count
        item.save()
        items = get_cart_items(request.user, session_key)
        serializer = CartSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'DELETE':
        items = get_cart_items(request.user, session_key)
        item = items.filter(product_id=product_id).first()
        if item:
            item.count -= count
            if item.count <= 0:
                item.delete()
            else:
                item.save()
        items = get_cart_items(request.user, session_key)
        serializer = CartSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def orders(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            qs = Order.objects.filter(user=request.user)
        else:
            qs = Order.objects.none()
        serializer = OrderSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        session_key = request.session.session_key
        cart_items = get_cart_items(request.user, session_key)
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.data.get('fullName', ''),
            email=request.data.get('email', ''),
            phone=request.data.get('phone', ''),
            delivery_type=request.data.get('deliveryType', 'free'),
            payment_type=request.data.get('paymentType', 'online_card'),
            city=request.data.get('city', ''),
            address=request.data.get('address', ''),
            comment=request.data.get('comment', ''),
        )

        total = Decimal('0.00')
        for cart_item in cart_items:
            price = cart_item.product.price * cart_item.count
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                title=cart_item.product.title,
                price=price,
                count=cart_item.count,
            )
            total += price

        delivery_settings = DeliverySettings.objects.first()
        if delivery_settings:
            if order.delivery_type == 'express':
                total += delivery_settings.express_delivery_cost
            elif total < delivery_settings.free_delivery_threshold:
                total += delivery_settings.delivery_cost

        order.total_cost = total
        order.save()

        cart_items.delete()
        return Response({'orderId': order.id})


@api_view(['GET', 'POST'])
def order_detail(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        order.full_name = request.data.get('fullName', order.full_name)
        order.email = request.data.get('email', order.email)
        order.phone = request.data.get('phone', order.phone)
        order.delivery_type = request.data.get('deliveryType', order.delivery_type)
        order.payment_type = request.data.get('paymentType', order.payment_type)
        order.city = request.data.get('city', order.city)
        order.address = request.data.get('address', order.address)
        order.comment = request.data.get('comment', order.comment)
        order.status = request.data.get('status', order.status)
        order.save()
        return Response({'status': 'ok'})


@api_view(['POST'])
def payment(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    number = request.data.get('number', '')
    if len(number) > 8:
        return Response({'error': 'Invalid number'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        num = int(number)
    except ValueError:
        return Response({'error': 'Invalid number'}, status=status.HTTP_400_BAD_REQUEST)

    if num % 2 != 0:
        order.status = 'cancelled'
        order.payment_error = 'Payment declined: invalid number'
        order.save()
        return Response({'status': 'error', 'error': 'Payment declined'})

    if number.endswith('0'):
        import random
        if random.random() < 0.5:
            order.status = 'cancelled'
            order.payment_error = 'Random payment error'
            order.save()
            return Response({'status': 'error', 'error': 'Random payment error'})

    order.status = 'paid'
    order.payment_error = None
    order.save()
    return Response({'status': 'ok'})


@api_view(['GET', 'POST'])
def profile(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    profile_obj, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return Response({
            'fullName': profile_obj.full_name,
            'email': request.user.email,
            'phone': profile_obj.phone,
            'avatar': {'src': profile_obj.avatar.url if profile_obj.avatar else '', 'alt': 'avatar'},
        })

    if request.method == 'POST':
        profile_obj.full_name = request.data.get('fullName', profile_obj.full_name)
        profile_obj.phone = request.data.get('phone', profile_obj.phone)
        profile_obj.save()
        request.user.email = request.data.get('email', request.user.email)
        request.user.save()
        return Response({
            'fullName': profile_obj.full_name,
            'email': request.user.email,
            'phone': profile_obj.phone,
            'avatar': {'src': profile_obj.avatar.url if profile_obj.avatar else '', 'alt': 'avatar'},
        })


@api_view(['POST'])
def profile_password(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    current = request.data.get('currentPassword')
    new = request.data.get('newPassword')
    if not request.user.check_password(current):
        return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.set_password(new)
    request.user.save()
    return Response({'status': 'ok'})


@api_view(['POST'])
def profile_avatar(request):
    if not request.user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if 'avatar' in request.FILES:
        profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
    return Response({'status': 'ok'})


@api_view(['GET'])
def tags(request):
    from .models import Tag
    category_id = request.query_params.get('category')
    if category_id:
        tags_qs = Tag.objects.filter(producttag__product__category_id=category_id).distinct()
    else:
        tags_qs = Tag.objects.all()
    serializer = TagSerializer(tags_qs, many=True)
    return Response(serializer.data)
