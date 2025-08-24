from django.contrib import admin
from .models import Category, Product, Inventory, Review

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Review)
