from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import Count,Avg
from core.models import Product, Category,Supplier,CartOrder,CartOrderItems ,ProductReview,Wishlist,ContactMessage
from core.form import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages
import stripe
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.core.mail import send_mail

def index(request):
     products=Product.objects.filter(product_status="published")

     context={
        "products":products
     }
    
     return render(request,'core/index.html',context) 

class CustomPasswordResetView(PasswordResetView):
    template_name = 'ragistration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('core:password_reset_done')

def product_list_view(request):
    categories=Category.objects.prefetch_related("products").all()
    products=Product.objects.filter(product_status="published")

    context={
        "products":products,
    
    }
    
    return render(request,'core/product-list.html',context) 


def category_product_list_view(request,cid):

    category=Category.objects.get(cid=cid)
    products=Product.objects.filter(product_status="published",category=category)

    context={
        "category":category,
        "products":products,
    }
    return render(request,"core/category-product-list.html",context)



def product_detail_view(request, pid):
    product = get_object_or_404(Product, pid=pid)

    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    reviews = ProductReview.objects.filter(product=product).order_by("date")

    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    review_form = ProductReviewForm()

    make_review = True
    has_bought = False

    if request.user.is_authenticated:

        # ✅ check purchase
        has_bought = CartOrderItems.objects.filter(
            order__user=request.user,
            item=product,
            order__product_status="delivered"
        ).exists()

        # ✅ check already reviewed
        user_review_count = ProductReview.objects.filter(
            user=request.user,
            product=product
        ).count()

        if user_review_count > 0:
            make_review = False

    context = {
        "p": product,
        "make_review": make_review,
        "has_bought": has_bought,
        "review_form": review_form,
        "average_rating": average_rating,
        "reviews": reviews,
        "products": products,
    }

    return render(request, "core/product-detail.html", context)








def ajax_add_review(request,pid):
    product=Product.objects.get(pid=pid) 
    user=request.user

    if request.method == "POST":

        has_bought = CartOrderItems.objects.filter(
        order__user=user,
        item=product.title,
        # order__product_status="delivered"
    ).exists()

    if not has_bought:
        return JsonResponse({
            'bool': False,
            'msg': 'You can only review purchased product'
        })

    review=ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST["review"],
        rating=request.POST["rating"],
    )

    context={
        'user':user.username,
        'review':request.POST["review"],
        'rating':request.POST["rating"],
        'date': review.date.strftime("%d %B %Y"),
    }
 
    average_reviews=ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool':True,
            'context':context,
            'average_reviews':average_reviews,
        }
    )


def search_view(request):
    query=request.GET.get("q")
    
    products=Product.objects.filter(title__icontains=query).order_by("-created_at")

    context={
        "products":products,
        "query":query,
    }
    return render(request,"core/search.html",context)

def search_suggestions(request):

    query = request.GET.get("q")
    data = []

    if query:
        products = Product.objects.filter(title__icontains=query)[:5]
        for p in products:
            data.append({
                "title": p.title,
                "url": f"/product/{p.pid}/"
            })

    return JsonResponse(data, safe=False)

@login_required
def add_to_cart(request):

    product_id = request.GET.get("id")
    product = get_object_or_404(Product, id=product_id)

    cart_product = {
        str(product.id): {
            'title': product.title,
            'qty': 1,
            'price': float(product.price),
            'image': product.image.url,
            'pid':product.pid,
        }
    }

    if "cart_data_obj" in request.session:
        cart_data = request.session["cart_data_obj"]
        cart_data.update(cart_product)
        request.session["cart_data_obj"] = cart_data
    else:
        request.session["cart_data_obj"] = cart_product

    return JsonResponse({
        "totalcartitems": len(request.session["cart_data_obj"])
    })


@login_required             
def cart_view(request):

    cart_total_amount = 0

    if 'cart_data_obj' in request.session:

        for p_id, item in request.session['cart_data_obj'].items():
            item['subtotal'] = int(item['qty']) * float(item['price'])
            cart_total_amount += item['subtotal']

        # shipping logic
        if cart_total_amount >= 500:
            shipping = 0
            shipping_message = "🎉 You got Free Shipping!"
        else:
            shipping = 50
            shipping_message = "Free shipping available on orders above ₹500"

        total = cart_total_amount + shipping

        context = {
            "cart_data": request.session['cart_data_obj'],
            "totalcartitems": len(request.session['cart_data_obj']),
            "cart_total_amount": cart_total_amount,
            "shipping": shipping,
            "total": total,
            "shipping_message": shipping_message
        }

        return render(request, "core/cart.html", context)

    else:
        messages.warning(request, "your cart is empty")
        return redirect("core:index")
    



@login_required
def delete_item_from_cart(request):
    product_id=str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:    
           cart_data=request.session['cart_data_obj']
           del request.session['cart_data_obj'][product_id]
           request.session['cart_data_obj']=cart_data
    
    cart_total_amount=0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context=render_to_string("core/cart-list.html",{"cart_data":request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']),"cart_total_amount":cart_total_amount},request=request)
    return JsonResponse({"data":context, 'totalcartitems':len(request.session['cart_data_obj'])})

@login_required
def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        cart_data = request.session['cart_data_obj']

        if product_id in cart_data:
            cart_data[product_id]['qty'] = product_qty

        request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0

    for p_id, item in request.session['cart_data_obj'].items():
        item['subtotal'] = int(item['qty']) * float(item['price'])
        cart_total_amount += item['subtotal']

    context = render_to_string(
        "core/cart-list.html",
        {
            "cart_data": request.session['cart_data_obj'],
            "totalcartitems": len(request.session['cart_data_obj']),
            "cart_total_amount": cart_total_amount
        },
        request=request
    )

    return JsonResponse({
        "data": context,
        "totalcartitems": len(request.session['cart_data_obj'])
    })


@login_required
def checkout_view(request):

    user = request.user
    cart_total_amount = 0

    cart_data = request.session.get('cart_data_obj', {})

    for p_id, item in cart_data.items():
        cart_total_amount += int(item['qty']) * float(item['price'])

    # shipping logic
    if cart_total_amount >= 500:
        shipping = 0
        shipping_message = "🎉 Free Shipping Applied"
    else:
        shipping = 50
        shipping_message = "Flat Rate ₹50 Applied"

    total = cart_total_amount + shipping

    context = {
        "user": user,
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount,
        "shipping": shipping,
        "total": total,
        "shipping_message": shipping_message
    }

    return render(request, "core/checkout.html", context)

import razorpay
from django.conf import settings
from django.shortcuts import render

def payment_view(request):
    import razorpay
    from django.conf import settings

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    cart_total_amount = 0
    cart_data = request.session.get('cart_data_obj', {})

    # subtotal calculate
    for p_id, item in cart_data.items():
        cart_total_amount += int(item['qty']) * float(item['price'])

    # shipping logic
    if cart_total_amount >= 500:
        shipping = 0
    else:
        shipping = 50

    total = cart_total_amount + shipping

    # Razorpay amount (paise me)
    amount = int(total * 100)

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "total": total
    }

    return render(request, "core/payment.html", context)


from .models import CartOrder, CartOrderItems

def payment_completed_view(request):
    payment_id = request.GET.get("payment_id")

    cart_data = request.session.get('cart_data_obj', {})

    cart_total_amount = 0

    for p_id, item in cart_data.items():
        cart_total_amount += int(item['qty']) * float(item['price'])

    # 🔥 CREATE CART ORDER (NOT Order)
    # cart_order = CartOrder.objects.create(
    #     user=request.user if request.user.is_authenticated else None,
    #     payment_id=payment_id,
    #     total_amount=cart_total_amount,
    #     paid_status=True
    cart_order = CartOrder.objects.create(
    user=request.user if request.user.is_authenticated else None,
    price=cart_total_amount,   # ✅ ONLY THIS FIELD IS CORRECT

    paid_status=True,

    first_name=request.user.first_name if request.user.is_authenticated else "Guest",
    last_name=request.user.last_name if request.user.is_authenticated else "",
    email=request.user.email if request.user.is_authenticated else "guest@example.com",
    phone="0000000000",
    address="Online Order",
    area="Online",
    zipcode="000000"
)

    # 🔥 CREATE ITEMS
    # for p_id, item in cart_data.items():
    #     CartOrderItems.objects.create(
    #         order=cart_order,
    #         product_id=p_id,
    #         qty=item['qty'],
    #         price=item['price']
    #     )
    for p_id, item in cart_data.items():
        CartOrderItems.objects.create(
        order=cart_order,
        item=item['title'],      # ✅ change here
        image=item['image'],     # ✅ change here
        qty=item['qty'],
        price=item['price'],
        total=int(item['qty']) * float(item['price'])
    )
    request.session['cart_data_obj'] = {}

    return render(request, "core/payment-success.html", {
        "payment_id": payment_id,
        "cart_total_amount": cart_total_amount,
        "order": cart_order
    })

# ✅ FAILED VIEW
def payment_failed_view(request):
    return render(request, "core/payment-failed.html")               


from .models import CartOrder, CartOrderItems


def order_detail(request, id):

    order = CartOrder.objects.get(id=id)
    items = CartOrderItems.objects.filter(order=order)

    subtotal = 0

    for item in items:
        item.total = item.price * item.qty
        subtotal += item.total

    # shipping = 50
    # grand_total = subtotal + shipping
    
    
    if subtotal >= 500:
        shipping = 0
    else:
        shipping = 50

    grand_total = subtotal + shipping

    context = {
        "order": order,
        "items": items,
        "order_status": order.product_status,
        "subtotal": subtotal,
        "shipping": shipping,
        "grand_total": grand_total
    }

    return render(request, "core/order-detail.html", context)
@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)

    context = {
        "wishlist": wishlist,
    }
    return render(request,'core/wishlist.html',context)


@login_required
def add_to_wishlist(request):

    product_id = request.GET.get("id")
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return JsonResponse({"status":"added"})

@login_required
def remove_from_wishlist(request, id):
    wishlist_item = get_object_or_404(Wishlist, id=id, user=request.user)
    wishlist_item.delete()
    return redirect("core:wishlist")

@login_required
def track_order_view(request):
    return render(request, "core/track_order.html")

def place_order(request):

    if request.method == "POST":

        cart = request.session.get("cart_data_obj", {})
        total = 0

        for p_id, item in cart.items():
            total += int(item['qty']) * float(item['price'])

        order = CartOrder.objects.create(
            user=request.user,
            price=total,
            address=request.POST.get("address"),
            area=request.POST.get("area"),
            zipcode=request.POST.get("zipcode"),
            phone=request.POST.get("phone"),
        )

        for p_id, item in cart.items():
            CartOrderItems.objects.create(
                order=order,
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=int(item['qty']) * float(item['price'])
            )

        request.session['cart_data_obj'] = {}

        return redirect("core:order-detail", id=order.id)

    return redirect("core:checkout")  # अगर GET आए तो वापस checkout

def order_success(request):
    return render(request,"core/order_success.html")

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        option = request.POST.get("option")  # dropdown
        message_text = request.POST.get("message")

        # Save message in database
        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            option=option,
            message=message_text
        )
        send_mail(
            subject=f"New Contact Message - {option}",
            message=f"""
Name: {name}
Email: {email}
Phone: {phone}

Message:
{message_text}
""",
            from_email=email,
            recipient_list=['arpitakachiya005@gmail.com'],
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('core:contact')  # wapas contact page

    return render(request, "core/contact.html")


def privacy_policy(request):
    return render(request, "core/privacy-policy.html")


def terms_conditions(request):
    return render(request, "core/term-condition.html")

def return_policy(request):
    return render(request, "core/return-policy.html")