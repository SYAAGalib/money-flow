from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
	name = models.CharField(max_length=50)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
	is_default = models.BooleanField(default=False)

	class Meta:
		unique_together = ('name', 'user')
		ordering = ['name']

	def __str__(self):
		return self.name


class Transaction(models.Model):
	INCOME = 'income'
	EXPENSE = 'expense'
	TYPE_CHOICES = [
		(INCOME, 'Income'),
		(EXPENSE, 'Expense'),
	]
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
	type = models.CharField(max_length=7, choices=TYPE_CHOICES)
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	date = models.DateField()
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-date', '-id']

	def __str__(self):
		return f"{self.user} {self.type} {self.amount} on {self.date}"

# Create your models here.
