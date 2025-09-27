# from django.urls import path
# from website import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('search/', views.search, name='search'),
#     path('api/products/', views.product_list, name='product_list'),               # GET / POST
#     path('api/products/<int:product_id>/', views.product_detail, name='product_detail'),  # PUT / DELETE
# ]
from django.urls import path
from website import views
from website.views import CartView
urlpatterns = [
    path('', views.home, name='home'),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/products/', views.product_list, name='product_list'),
    path('api/cart/', CartView.as_view(), name='cart'),
    path('api/products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/session/', views.session_view, name='session'),
    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    path('api/me/', views.me, name='me'),
    path('api/change-password/', views.change_password, name='change_password'),
    # Admin-only
    path('api/admin/users/', views.admin_users, name='admin_users'),
    path('api/admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
]
