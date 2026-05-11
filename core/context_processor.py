#from django.db.models import Min, Max

from core.models import (
    Product,
    Category,
    CartOrder,
    CartOrderItems,
    Supplier,
    ProductReview,
    Wishlist,
)


def global_order(request):
    if request.user.is_authenticated:
        order = CartOrder.objects.filter(user=request.user).last()
    else:
        order = None

    return {"order": order}

def default(request):
    categories = Category.objects.all()

    return {
        "categories": categories,
    }
