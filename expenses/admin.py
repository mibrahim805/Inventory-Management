from django.contrib import admin
from expenses.models import Purchase, Product


@admin.register(Purchase)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "quantity", "user", "total_amount", "created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description", "default_price", "price"]