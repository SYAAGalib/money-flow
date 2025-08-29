from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import RegistrationForm, TransactionForm, CategoryForm, StyledAuthenticationForm
from .models import Transaction, Category
from django.conf import settings
from django.db.models import Q


def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			# ensure default categories exist globally (once)
			defaults = ['Salary', 'Food', 'Rent', 'Bills', 'Shopping', 'Others']
			for name in defaults:
				Category.objects.get_or_create(name=name, user=None, defaults={'is_default': True})
			login(request, user)
			return redirect('dashboard')
	else:
		form = RegistrationForm()
	return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
	transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-id')
	total_income = transactions.filter(type=Transaction.INCOME).aggregate(total=Sum('amount'))['total'] or 0
	total_expense = transactions.filter(type=Transaction.EXPENSE).aggregate(total=Sum('amount'))['total'] or 0
	balance = total_income - total_expense
	recent = transactions[:5]
	return render(request, 'core/dashboard.html', {
		'total_income': total_income,
		'total_expense': total_expense,
		'balance': balance,
		'recent_transactions': recent,
	})


@login_required
def transaction_list(request):
	qs = Transaction.objects.filter(user=request.user)
	type_f = request.GET.get('type')
	category_f = request.GET.get('category')
	start = request.GET.get('start')
	end = request.GET.get('end')
	q = request.GET.get('q')
	if type_f in [Transaction.INCOME, Transaction.EXPENSE]:
		qs = qs.filter(type=type_f)
	if category_f:
		qs = qs.filter(category__id=category_f)
	if start:
		qs = qs.filter(date__gte=start)
	if end:
		qs = qs.filter(date__lte=end)
	if q:
		qs = qs.filter(Q(notes__icontains=q) | Q(category__name__icontains=q))
	paginator = Paginator(qs.order_by('-date', '-id'), getattr(settings, 'PAGINATION_PAGE_SIZE', 10))
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	categories = Category.objects.filter(Q(user=request.user) | Q(is_default=True)).order_by('name').distinct()
	return render(request, 'core/transaction_list.html', {
		'page_obj': page_obj,
		'categories': categories,
		'filters': {
			'type': type_f or '',
			'category': category_f or '',
			'start': start or '',
			'end': end or '',
			'q': q or '',
		}
	})


@login_required
def transaction_create(request):
	if request.method == 'POST':
		form = TransactionForm(request.POST, user=request.user)
		if form.is_valid():
			tx = form.save(commit=False)
			tx.user = request.user
			tx.save()
			return redirect('dashboard')
	else:
		initial_type = request.GET.get('type') if request.GET.get('type') in [Transaction.INCOME, Transaction.EXPENSE] else None
		form = TransactionForm(user=request.user, initial={'date': timezone.now().date(), 'type': initial_type})
	return render(request, 'core/transaction_form.html', {'form': form, 'create': True})


@login_required
def transaction_update(request, pk):
	tx = get_object_or_404(Transaction, pk=pk, user=request.user)
	if request.method == 'POST':
		form = TransactionForm(request.POST, instance=tx, user=request.user)
		if form.is_valid():
			form.save()
			return redirect('transaction_list')
	else:
		form = TransactionForm(instance=tx, user=request.user)
	return render(request, 'core/transaction_form.html', {'form': form, 'create': False})


@login_required
def transaction_delete(request, pk):
	tx = get_object_or_404(Transaction, pk=pk, user=request.user)
	if request.method == 'POST':
		tx.delete()
		return redirect('transaction_list')
	return render(request, 'core/transaction_confirm_delete.html', {'transaction': tx})


@login_required
def profile(request):
	if request.method == 'POST':
		if 'theme' in request.POST:
			request.session['theme'] = request.POST.get('theme')
		if 'name' in request.POST:
			full_name = request.POST.get('name')
			first, *rest = full_name.split(' ', 1)
			request.user.first_name = first
			request.user.last_name = rest[0] if rest else ''
			request.user.save()
		if request.POST.get('new_category'):
			form = CategoryForm(request.POST, user=request.user)
			if form.is_valid():
				cat = form.save(commit=False)
				cat.user = request.user
				cat.save()
		return redirect('profile')
	full_name = f"{request.user.first_name} {request.user.last_name}".strip()
	cat_form = CategoryForm(user=request.user)
	user_categories = Category.objects.filter(user=request.user).order_by('name')
	return render(request, 'core/profile.html', {'full_name': full_name, 'category_form': cat_form, 'user_categories': user_categories})


def about(request):
	return render(request, 'core/about.html')


class StyledLoginView(LoginView):
	template_name = 'registration/login.html'
	authentication_form = StyledAuthenticationForm

	def form_valid(self, form):
		remember = bool(self.request.POST.get('remember'))
		# Let parent log user in first
		response = super().form_valid(form)
		if remember:
			self.request.session.set_expiry(1209600)
		else:
			# Browser close: set to 0 and mark modified
			self.request.session.set_expiry(0)
		self.request.session.modified = True
		return response

# Create your views here.
