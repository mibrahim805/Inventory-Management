from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView
from django.views.generic import UpdateView,DeleteView
from expenses.forms import PurchaseForm, RegistrationForm, ProductForm, SaleForm
from expenses.models import Product, Purchase, Sale


class RegisterUserView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("purchases:list")
    context_object_name = "data"


class ProductCreateView(LoginRequiredMixin,CreateView):
    model=Product
    form_class = ProductForm
    template_name = "products/add_product.html"
    success_url=reverse_lazy("expenses:expense_list")

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)
    def form_invalid(self,form):
        messages.error(self.request, "Error creating product.")



class ProductUpdateView(LoginRequiredMixin,UpdateView):
    model=Product
    form_class = ProductForm
    template_name = "products/add_product.html"
    success_url=reverse_lazy("expenses:product_list")

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)



class ProductListView(LoginRequiredMixin,ListView):
    model=Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    ordering=["-date"]
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)



class ProductDeleteView(LoginRequiredMixin,DeleteView):
    model=Product
    template_name = "products/delete_product.html"
    success_url=reverse_lazy("expenses:product_list")

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)




class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "purchases/add_purchase.html"
    success_url = reverse_lazy("expenses:expense_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SaleCreateView(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "sales/add_sale.html"
    success_url = reverse_lazy("expenses:expense_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error creating sale.")
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ProductReportView(LoginRequiredMixin, TemplateView):
    template_name="products/product_list.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        user_products=Product.objects.filter(user=self.request.user)
        purchase_totals=Purchase.objects.filter(product=OuterRef("pk"),user=self.request.user).values("product").annotate(total=Sum("quantity")).values("total")
        sale_totals=Sale.objects.filter(product=OuterRef("pk"),user=self.request.user).values("product").annotate(total=Sum("quantity")).values("total")
        products=user_products.annotate(purchased=Coalesce(Subquery(purchase_totals,output_field=IntegerField()),0),sold=Coalesce(Subquery(sale_totals,output_field=IntegerField()),0))
        context["products"]=products
        return context

class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "purchases/purchase_list.html"
    context_object_name = "purchases"

    def get_queryset(self):
        return Purchase.objects.filter(user=self.request.user).select_related("product").order_by("-created_at")

class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales/sale_list.html"
    context_object_name = "sales"
    def get_queryset(self):
        return Sale.objects.filter(user=self.request.user).select_related("product").order_by("-created_at")


class StockListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/stock_list.html"
    context_object_name = "products"
    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).order_by("name")



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "purchases/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        user_products = Product.objects.filter(user=self.request.user)

        if start_date and end_date:
            purchases = Purchase.objects.filter(user=self.request.user, created_at__date__range=[start_date, end_date])
            sales = Sale.objects.filter(user=self.request.user, created_at__date__range=[start_date, end_date])
        else:
            purchases = Purchase.objects.filter(user=self.request.user)
            sales = Sale.objects.filter(user=self.request.user)

        for product in user_products:
            product.purchased = purchases.filter(product=product).aggregate(total=Sum("quantity"))["total"] or 0
            product.sold = sales.filter(product=product).aggregate(total=Sum("quantity"))["total"] or 0

        context["products"] = user_products
        context["total_products"] = user_products.count()
        context["total_purchases"] = purchases.aggregate(total=Sum("quantity"))["total"] or 0
        context["total_sales"] = sales.aggregate(total=Sum("quantity"))["total"] or 0
        context["total_stock"] = user_products.aggregate(total=Sum("stock"))["total"] or 0
        context["start_date"] = start_date
        context["end_date"] = end_date
        return context