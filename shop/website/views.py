# from django.shortcuts import render
# from django.http import JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from website.models import Products

# # Home page — just render frontend, do not modify products
# def home(request):
#     return render(request, 'website/index.html')

# # Search page — just render frontend
# def search(request):
#     return render(request, 'website/index.html')

# # API: List all products / Add new product
# @csrf_exempt
# def product_list(request):
#     if request.method == 'GET':
#         # List all existing products
#         products = list(Products.objects.all().values('id', 'name', 'description', 'price'))
#         return JsonResponse(products, safe=False)
#     elif request.method == 'POST':
#         # Add new product
#         try:
#             data = json.loads(request.body)
#             product = Products.objects.create(
#                 name=data['name'],
#                 description=data.get('description', ''),
#                 price=data['price']
#             )
#             return JsonResponse({
#                 'success': True,
#                 'product': {
#                     'id': product.id,
#                     'name': product.name,
#                     'description': product.description,
#                     'price': str(product.price)
#                 }
#             })
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=400)
#     return HttpResponse(status=405)

# # API: Update or Delete an existing product
# @csrf_exempt
# def product_detail(request, product_id):
#     try:
#         product = Products.objects.get(id=product_id)
#     except Products.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

#     if request.method == 'PUT':
#         data = json.loads(request.body)
#         product.name = data.get('name', product.name)
#         product.description = data.get('description', product.description)
#         product.price = data.get('price', product.price)
#         product.save()
#         return JsonResponse({
#             'success': True,
#             'product': {
#                 'id': product.id,
#                 'name': product.name,
#                 'description': product.description,
#                 'price': str(product.price)
#             }
#         })
#     elif request.method == 'DELETE':
#         product.delete()
#         return JsonResponse({'success': True})
#     return HttpResponse(status=405)
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from website.models import Products, Cart, CartItem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, Products, CartItem
# ---------------- Home ----------------
def home(request):
    return render(request, 'website/index.html')


# ---------------- Registration ----------------
@csrf_exempt
def register(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        data = json.loads(request.body)
        if User.objects.filter(username=data["username"]).exists():
            return JsonResponse({"success": False, "error": "Username already taken"}, status=400)
        if User.objects.filter(email=data["email"]).exists():
            return JsonResponse({"success": False, "error": "Email already registered"}, status=400)

        user = User.objects.create_user(
            username=data["username"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data["email"],
            password=data["password"]
        )
        return JsonResponse({"success": True, "message": "User registered successfully"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ---------------- Login ----------------
@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        data = json.loads(request.body)
        identifier = data.get("email") or data.get("username")
        password = data.get("password")
        if not identifier or not password:
            return JsonResponse({"success": False, "error": "Email/Username and password required"}, status=400)

        # allow login with either email or username
        if "@" in identifier:
            user_obj = User.objects.filter(email=identifier).first()
        else:
            user_obj = User.objects.filter(username=identifier).first()
        if not user_obj:
            return JsonResponse({"success": False, "error": "Invalid credentials"}, status=400)

        user = authenticate(username=user_obj.username, password=password)
        if user:
            auth_login(request, user)  # creates session
            request.session.save()     # ensures cookie is saved
            return JsonResponse({"success": True, "message": "Login successful"})
        return JsonResponse({"success": False, "error": "Invalid credentials"}, status=400)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# ---------------- Logout ----------------
@csrf_exempt
def logout_view(request):
    auth_logout(request)
    return JsonResponse({"success": True, "message": "Logged out"})


# ---------------- Session Check ----------------
def session_view(request):
    return JsonResponse({
        "is_authenticated": request.user.is_authenticated,
        "is_admin": request.user.is_authenticated and request.user.is_staff,
        "username": request.user.username if request.user.is_authenticated else None,
    })


# ---------------- Products API ----------------
@csrf_exempt
def product_list(request):
    if request.method == "GET":
        products = list(Products.objects.all().values('id', 'name', 'description', 'price'))
        return JsonResponse(products, safe=False)
    elif request.method == "POST":
        # Admin only: create product
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Admin access required"}, status=403)
        try:
            data = json.loads(request.body)
            product = Products.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price']
            )
            return JsonResponse({
                "success": True,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": str(product.price)
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return HttpResponse(status=405)


@csrf_exempt
def product_detail(request, product_id):
    try:
        product = Products.objects.get(id=product_id)
    except Products.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    if request.method == 'PUT':
        # Admin only: update product
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Admin access required"}, status=403)
        data = json.loads(request.body)
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.save()
        return JsonResponse({'success': True})
    elif request.method == 'DELETE':
        # Admin only: delete product
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"success": False, "error": "Admin access required"}, status=403)
        product.delete()
        return JsonResponse({'success': True})
    return HttpResponse(status=405)


# ---------------- Cart API ----------------



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Cart, CartItem, Products

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Fetch cart details for logged-in user"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = [
            {
                "id": item.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "price": float(item.product.price),
                "quantity": item.quantity,
                "subtotal": float(item.product.price * item.quantity),
            }
            for item in cart.items.select_related("product").all()
        ]
        total = sum(item["subtotal"] for item in items)
        return Response({"cart_id": cart.id, "items": items, "total": total})

    def post(self, request):
        """Add or update an item in the cart"""
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response(
                {"success": False, "error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response(
                {"success": False, "error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response({
            "success": True,
            "message": "Item added to cart",
            "item": {
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "subtotal": float(product.price * item.quantity)
            }
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update quantity of a single cart item or remove it if quantity <= 0"""
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")
        if item_id is None or quantity is None:
            return Response({"success": False, "error": "item_id and quantity are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.select_related("cart", "product").get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"success": False, "error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantity = int(quantity)
        except ValueError:
            return Response({"success": False, "error": "quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            item.delete()
            return Response({"success": True, "message": "Item removed"}, status=status.HTTP_200_OK)

        item.quantity = quantity
        item.save()
        return Response({"success": True, "message": "Item updated", "quantity": item.quantity}, status=status.HTTP_200_OK)

    def delete(self, request):
        """Clear all items in the cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"success": True, "message": "Cart cleared"}, status=status.HTTP_200_OK)


# ---------------- Admin: Users management ----------------
@csrf_exempt
def admin_users(request):
    # Admin only
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Admin access required"}, status=403)

    if request.method == 'GET':
        users = list(User.objects.all().values('id', 'username', 'email', 'first_name', 'last_name', 'is_staff'))
        return JsonResponse({"success": True, "users": users})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if User.objects.filter(username=data['username']).exists():
                return JsonResponse({"success": False, "error": "Username already exists"}, status=400)
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({"success": False, "error": "Email already exists"}, status=400)
            user = User.objects.create_user(
                username=data['username'],
                email=data.get('email', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                password=data.get('password', 'changeme123')
            )
            return JsonResponse({"success": True, "user": {"id": user.id, "username": user.username}})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return HttpResponse(status=405)


@csrf_exempt
def admin_user_detail(request, user_id):
    # Admin only
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({"success": False, "error": "Admin access required"}, status=403)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "error": "User not found"}, status=404)

    if request.method == 'DELETE':
        # prevent self-delete for safety
        if request.user.id == user.id:
            return JsonResponse({"success": False, "error": "Cannot delete your own account"}, status=400)
        user.delete()
        return JsonResponse({"success": True})
    if request.method in ['PUT', 'PATCH']:
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        # update basic fields
        for field in ["username", "email", "first_name", "last_name"]:
            if field in data:
                setattr(user, field, data[field])
        # promote/demote admin
        if "is_staff" in data:
            user.is_staff = bool(data["is_staff"])
        # reset password
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        return JsonResponse({"success": True})
    return HttpResponse(status=405)


# ---------------- Admin: Stats ----------------
def _admin_required(request):
    return request.user.is_authenticated and request.user.is_staff

def _forbidden():
    return JsonResponse({"success": False, "error": "Admin access required"}, status=403)

@csrf_exempt
def admin_stats(request):
    if not _admin_required(request):
        return _forbidden()
    if request.method != 'GET':
        return HttpResponse(status=405)
    users_count = User.objects.count()
    staff_count = User.objects.filter(is_staff=True).count()
    products_count = Products.objects.count()
    carts_count = Cart.objects.count()
    items_count = CartItem.objects.count()
    return JsonResponse({
        "success": True,
        "users": users_count,
        "admins": staff_count,
        "products": products_count,
        "carts": carts_count,
        "cart_items": items_count,
    })


# ---------------- Profile (current user) ----------------
@csrf_exempt
def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Auth required"}, status=403)
    if request.method == 'GET':
        u = request.user
        return JsonResponse({
            "success": True,
            "user": {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "is_admin": u.is_staff,
            }
        })
    if request.method in ['PUT', 'PATCH']:
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
        u = request.user
        for field in ["username", "email", "first_name", "last_name"]:
            if field in data:
                setattr(u, field, data[field])
        u.save()
        return JsonResponse({"success": True})
    return HttpResponse(status=405)


@csrf_exempt
def change_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Auth required"}, status=403)
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        data = json.loads(request.body)
        old = data.get("old_password")
        new = data.get("new_password")
        if not old or not new:
            return JsonResponse({"success": False, "error": "Both old_password and new_password required"}, status=400)
        if not request.user.check_password(old):
            return JsonResponse({"success": False, "error": "Old password incorrect"}, status=400)
        request.user.set_password(new)
        request.user.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
