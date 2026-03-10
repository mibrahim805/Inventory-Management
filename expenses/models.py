from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name=models.CharField(max_length=255)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="products",null=True,blank=True)
    description=models.TextField(blank=True,null=True)
    default_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    stock=models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="purchases")
    quantity=models.PositiveIntegerField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_purchases",null=True,blank=True)
    # date=models.DateField()
    total_amount=models.DecimalField(max_digits=12,decimal_places=2,editable=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.pk:  # Only run this for new purchases
            self.total_amount=self.product.price*self.quantity
            self.product.stock+=self.quantity
            self.product.save()
        super().save(*args,**kwargs)
    def __str__(self):
        return f"Expense {self.id}"

class Sale(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="sales")
    quantity=models.PositiveIntegerField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_sales",null=True,blank=True)
    # date=models.DateField()
    total_amount=models.DecimalField(max_digits=12,decimal_places=2,editable=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.quantity > self.product.stock:
                raise ValueError("Not enough stock")
            self.total_amount = self.product.price * self.quantity
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Sale {self.id}"