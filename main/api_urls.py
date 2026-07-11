from django.urls import path
from . import views_api

urlpatterns = [
    path('sign-in', views_api.sign_in, name='sign-in'),
    path('sign-up', views_api.sign_up, name='sign-up'),
    path('sign-out', views_api.sign_out, name='sign-out'),
    path('categories', views_api.categories, name='categories'),
    path('catalog', views_api.catalog, name='catalog'),
    path('products/popular', views_api.products_popular, name='products-popular'),
    path('products/limited', views_api.products_limited, name='products-limited'),
    path('sales', views_api.sales, name='sales'),
    path('banners', views_api.banners, name='banners'),
    path('product/<int:id>', views_api.product_detail, name='product-detail'),
    path('product/<int:id>/review', views_api.product_review, name='product-review'),
    path('basket', views_api.basket, name='basket'),
    path('orders', views_api.orders, name='orders'),
    path('orders/<int:id>', views_api.order_detail, name='order-detail'),
    path('order/<int:id>', views_api.order_detail, name='order-detail-singular'),
    path('product/<int:id>/reviews', views_api.product_review, name='product-review-plural'),
    path('payment/<int:id>', views_api.payment, name='payment'),
    path('profile', views_api.profile, name='profile'),
    path('profile/password', views_api.profile_password, name='profile-password'),
    path('profile/avatar', views_api.profile_avatar, name='profile-avatar'),
    path('tags', views_api.tags, name='tags'),
]
