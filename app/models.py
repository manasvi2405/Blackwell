from django.db import models
from ckeditor.fields import RichTextField


# Create your models here.
class ProductCategory(models.Model):
    name=models.CharField(max_length=100, unique=True)
    image=models.ImageField(upload_to='categories/', blank=True, null=True)
    description=models.TextField(blank=True)
    parent=models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,related_name="subcategories")
    class Meta:
        verbose_name_plural="ProductCategories"
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name=models.CharField(max_length=100, unique=True)
    image1=models.ImageField(upload_to='product_images/',blank=True,null=True)
    image2=models.ImageField(upload_to='product_images/',blank=True,null=True)
    image3=models.ImageField(upload_to='product_images/',blank=True,null=True)
    image4=models.ImageField(upload_to='product_images/',blank=True,null=True)
    category=models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True)
    mrp=models.DecimalField(max_digits=10, decimal_places=2)
    selling_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    description=RichTextField(blank=True, null=True)
    stock_qty=models.PositiveIntegerField(default=0)

    @property
    def in_stock(self):
        return self.stock_qty > 0
    
    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=200)
    phone_number = models.CharField(max_length=14)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        # Orders results by newest first automatically
        ordering = ['-created_at']
    def __str__(self):
         return f'{self.name} - {self.created_at.strftime("%Y-%m-%d")}'
  
