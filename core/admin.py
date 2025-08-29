from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'is_default')
	list_filter = ('is_default',)
	search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('user', 'type', 'category', 'amount', 'date')
	list_filter = ('type', 'category')
	search_fields = ('notes',)
	date_hierarchy = 'date'

# Register your models here.
