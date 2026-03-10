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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "purchases/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_products = Product.objects.filter(user=self.request.user)
        purchase_totals = Purchase.objects.filter(product=OuterRef("pk"), user=self.request.user).values("product").annotate(total=Sum("quantity")).values("total")
        sale_totals = Sale.objects.filter(product=OuterRef("pk"), user=self.request.user).values("product").annotate(total=Sum("quantity")).values("total")
        products = user_products.annotate(purchased=Coalesce(Subquery(purchase_totals, output_field=IntegerField()), 0),sold=Coalesce(Subquery(sale_totals, output_field=IntegerField()),0))
        context["total_products"] = user_products.count()
        context["total_purchases"] = Purchase.objects.filter(user=self.request.user).aggregate(total=Coalesce(Sum("quantity"), 0))["total"]
        context["total_sales"] = Sale.objects.filter(user=self.request.user).aggregate(total=Coalesce(Sum("quantity"), 0))["total"]
        context["total_stock"] = user_products.aggregate(total=Coalesce(Sum("stock"), 0))["total"]
        context["products"] = products
        return context


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