from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDeleteView, ProductUpdateView, RegisterUserView, \
    DashboardView, PurchaseCreateView, SaleCreateView, ProductReportView, PurchaseListView, SaleListView, StockListView


app_name="expenses"

urlpatterns=[
    path("list/",DashboardView.as_view(),name="expense_list"),
    path('add_product/',ProductCreateView.as_view(),name="add_product"),
    path("register/",RegisterUserView.as_view(),name="register"),
    path("product_list/", ProductReportView.as_view(),name="product_list"),
    path("delete/<int:pk>/",ProductDeleteView.as_view(),name="delete_product"),
    path("update/<int:pk>/",ProductUpdateView.as_view(),name="update_product"),
    path("add_purchase/",PurchaseCreateView.as_view(),name="add_purchase"),
    path("add_sale/",SaleCreateView.as_view(),name="add_sale"),
    path("purchase_report/",PurchaseListView.as_view(),name="purchase_report"),
    path("sale_report/",SaleListView.as_view(),name="sale_report"),
    path("stock_report/",StockListView.as_view(),name="stock_report"),
]

