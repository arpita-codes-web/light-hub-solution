from django.urls import path,include
from core.views import index
from core.views import *
from django.contrib.auth import views as auth_views
from .views import order_detail


from django.urls import reverse_lazy



app_name="core"


urlpatterns=[

    path('accounts/', include('django.contrib.auth.urls')),
    path("",index,name="index"),
    path("products/",product_list_view,name="product-list"),
    path("product/<pid>/",product_detail_view,name="product-detail"),

    #forgotpasword
    

    path(
    'password_reset_form/',
    auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_email.txt',
        success_url='/password_reset/done/'
    ),
    name='password_reset_form'
),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(success_url='/password_reset_complete/done'), name='password_reset_confirm'),
    path('password_reset_complete/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
   

    #category

    path("category/<cid>/",category_product_list_view,name="category-product-list"),



    # Add Review
    path("ajax-add-review/<pid>/",ajax_add_review,name="ajax-add-review"),

    #search
    path("search/",search_view,name="search"),
    path("search-suggestions/",search_suggestions, name="search-suggestions"),

    #add to cart

    path("add-to-cart/",add_to_cart, name="add-to-cart"),
    
    #cart page
    path("cart/",cart_view,name="cart"),

    # remove cart
    path("delete-from-cart/",delete_item_from_cart,name="delete-from-cart"),

    #update
    path("update-cart/",update_cart,name="update_cart"),

    #checkout
    path("checkout/",checkout_view,name="checkout"),

    path("payment/", payment_view, name="payment"),
    path("payment-completed/", payment_completed_view, name="payment-completed"),
    path("payment-failed/", payment_failed_view, name="payment-failed"),

 
    path("wishlist/",wishlist_view,name="wishlist"),

path("add-to-wishlist/",add_to_wishlist, name="add-to-wishlist"),


path("remove-from-wishlist/<int:id>/", remove_from_wishlist, name="remove-from-wishlist"),

path("contact/", contact_view, name="contact"),

path("place-order/",place_order, name="place-order"),
path("order/<int:id>/",order_detail, name="order-detail"),


path("privacy-policy/", privacy_policy, name="privacy-policy"),
path("terms-conditions/", terms_conditions, name="term-condition"),
path("return-policy/", return_policy, name="return-policy"),

path("track-order/", track_order_view, name="track_order"),
path("order-success/",order_success, name="order-success"),

]