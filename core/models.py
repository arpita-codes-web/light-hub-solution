
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from decimal import Decimal
from django.conf import settings



STATUS_CHOICE=(
   ("pending", "Pending"),
   ("processing", "Processing"),
   ("shipped", "Shipped"),
   ("delivered", "Delivered"),
)



STATUS=(
    ("draft","Draft"),
    ("disabled","Disabled"),
    ("rejected","Rejected"),
    ("in_review","In_Review"),
    ("published","Published"),
)


RATING=(
    (1,"★☆☆☆☆"),
    (2,"★★☆☆☆"),
    (3,"★★★☆☆"),
    (4,"★★★★☆"),
    (5,"★★★★★"),
)


def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=8, prefix="cat")
    title = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"


    def __str__(self):
        return self.title
    
 
class Supplier(models.Model):
    sid = ShortUUIDField(unique=True, length=8, prefix="sup", alphabet="12345abc")
    name = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    contact = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.name} - {self.area}"
    
class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=8, prefix="prd")

    category = models.ForeignKey(Category,related_name="products", on_delete=models.SET_NULL, null=True)

    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="product-images/")
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock_count = models.IntegerField(default=0)
    PRODUCT_STATUS_CHOICES = (
    ("published", "Published"),
    ("in_review", "In Review"),
    ("draft", "Draft"),
)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)


    product_status = models.CharField(choices= PRODUCT_STATUS_CHOICES, max_length=15, default="in_review")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" />')

    def __str__(self):
        return self.title
    

class CartOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    paid_status = models.BooleanField(default=False)

    # Billing Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=12)

    address = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=6)

    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=20, default="Pending")

    class Meta:
        verbose_name_plural = "Orders" 

class CartOrderItems(models.Model):
    order=models.ForeignKey(CartOrder,on_delete=models.CASCADE)  
    product_status=models.CharField(max_length=200, default="processing")
    item=models.CharField(max_length=200)
    image=models.CharField(max_length=200)
    qty=models.IntegerField(default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    total=models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        verbose_name_plural=" Cart Order"

    def order_img(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" />' % (self.image)) 

class ProductReview(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews")
    review=models.TextField()
    rating=models.IntegerField(choices=RATING , default=5)
    date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating        


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    option = models.CharField(max_length=50, blank=True)  # dropdown selection
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_replied = models.BooleanField(default=False)  # admin reply status

    def __str__(self):
        return f"{self.name} - {self.email}"