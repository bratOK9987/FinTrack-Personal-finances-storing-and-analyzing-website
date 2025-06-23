from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.db.models import F
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
from datetime import datetime
from .models import Budget
from django.shortcuts import get_object_or_404

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict
import calendar

from .models import FinancialRecord, Tag


def landing_page(request):
    return render(request, 'fintrack/landing.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('signup')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password, email=email)
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'fintrack/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'fintrack/login.html')


@login_required
def add_record_view(request):
    if request.method == 'POST':
        record_type = request.POST.get('record_type', '').strip()
        amount_raw = request.POST.get('amount', '').strip()
        description = request.POST.get('description', '').strip()
        date_raw = request.POST.get('date', '').strip()
        tags_raw = request.POST.get('tags', '')

        # Validation
        if record_type not in ['income', 'expense']:
            messages.error(request, "Invalid record type.")
            return redirect('add_record')

        try:
            amount = Decimal(amount_raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            messages.error(request, "Amount must be a positive number.")
            return redirect('add_record')

        try:
            date = datetime.strptime(date_raw, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date format.")
            return redirect('add_record')

        if len(description) > 1000:
            messages.error(request, "Description is too long.")
            return redirect('add_record')

        # Save record
        record = FinancialRecord.objects.create(
            user=request.user,
            record_type=record_type,
            amount=amount,
            description=description,
            date=date
        )

        tag_names = [tag.strip().lower() for tag in tags_raw.split(',') if tag.strip()]
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            record.tags.add(tag)

        messages.success(request, "Record created successfully.")
        return redirect('dashboard')

    return render(request, 'fintrack/add_record.html')

@login_required
def edit_record_view(request, record_id):
    record = get_object_or_404(FinancialRecord, id=record_id, user=request.user)

    if request.method == 'POST':
        record_type = request.POST.get('record_type', '').strip()
        amount_raw = request.POST.get('amount', '').strip()
        description = request.POST.get('description', '').strip()
        date_raw = request.POST.get('date', '').strip()
        tags_raw = request.POST.get('tags', '')

        try:
            record.record_type = record_type
            record.amount = Decimal(amount_raw)
            record.description = description
            record.date = datetime.strptime(date_raw, '%Y-%m-%d').date()

            record.tags.clear()
            tag_names = [tag.strip().lower() for tag in tags_raw.split(',') if tag.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                record.tags.add(tag)

            record.save()
            messages.success(request, "Record updated successfully.")
            return redirect('dashboard')

        except (InvalidOperation, ValueError):
            messages.error(request, "Invalid input. Please correct the form.")

    tags_string = ', '.join(tag.name for tag in record.tags.all())

    return render(request, 'fintrack/edit_record.html', {
        'record': record,
        'tags_string': tags_string,
    })


@login_required
def delete_record_view(request, record_id):
    record = get_object_or_404(FinancialRecord, id=record_id, user=request.user)
    record.delete()
    messages.success(request, "Record deleted successfully.")
    return redirect('dashboard')


@login_required
def dashboard_view(request):
    records = FinancialRecord.objects.filter(user=request.user)

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    tag_search = request.GET.get('tag_search', '')
    search = request.GET.get('search', '')

    if start_date:
        records = records.filter(date__gte=parse_date(start_date))
    if end_date:
        records = records.filter(date__lte=parse_date(end_date))
    if search:
        records = records.filter(description__icontains=search)
    if tag_search:
        records = records.filter(tags__name__icontains=tag_search)

    # Sorting
    sort = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    allowed_sort_fields = ['date', 'record_type', 'amount']
    if sort not in allowed_sort_fields:
        sort = 'date'

    if order == 'asc':
        records = records.order_by(F(sort).asc())
    else:
        records = records.order_by(F(sort).desc())

    # Pagination
    paginator = Paginator(records, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'fintrack/dashboard.html', {
        'records': page_obj,
        'page_obj': page_obj,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'sort': sort,
        'order': order,
        'search': search,
        'tag_search': tag_search
    })

@login_required
def summary_view(request):
    records = FinancialRecord.objects.filter(user=request.user)

    total_income = records.filter(record_type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expense = records.filter(record_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    balance = total_income - total_expense

    # Расходы и доходы по месяцам
    monthly_summary = records.annotate(month=TruncMonth('date')).values('month', 'record_type') \
                             .annotate(total=Sum('amount')).order_by('month')

    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
    for entry in monthly_summary:
        month_name = entry['month'].strftime('%B %Y')
        monthly_data[month_name][entry['record_type']] = entry['total']

    sorted_months = sorted(monthly_data.items(), key=lambda x: datetime.strptime(x[0], '%B %Y'))

    abs_balance = abs(balance)

    return render(request, 'fintrack/summary.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'abs_balance': abs_balance,
        'monthly_data': sorted_months,
    })

@login_required
def budget_view(request):
    current_month = datetime.today().replace(day=1).date()

    budget, created = Budget.objects.get_or_create(
        user=request.user,
        month=current_month,
        defaults={
            'expense_limit': Decimal('0.00'),
            'income_target': Decimal('0.00')
        }
    )

    if request.method == 'POST':
        expense_limit = request.POST.get('expense_limit', '').strip()
        income_target = request.POST.get('income_target', '').strip()

        try:
            budget.expense_limit = Decimal(expense_limit)
            budget.income_target = Decimal(income_target) if income_target else None
            budget.save()
            messages.success(request, "Budget updated successfully!")
        except (InvalidOperation, ValueError):
            messages.error(request, "Please enter valid numbers.")
        return redirect('budget')

    # расходы за текущий месяц
    from calendar import monthrange
    last_day = datetime.today().replace(day=monthrange(current_month.year, current_month.month)[1]).date()
    current_expenses = FinancialRecord.objects.filter(
        user=request.user,
        record_type='expense',
        date__gte=current_month,
        date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # доходы за месяц
    current_income = FinancialRecord.objects.filter(
        user=request.user,
        record_type='income',
        date__gte=current_month,
        date__lte=last_day
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Расчёт прогресса доходов
    if budget.income_target and budget.income_target > 0:
        income_progress_percent = (current_income / budget.income_target) * 100
    else:
        income_progress_percent = None

    # Расчёт прогресса расходов
    if budget.expense_limit > 0:
        progress_percent = (current_expenses / budget.expense_limit) * 100
    else:
        progress_percent = None

    today = datetime.today().date()
    days_in_month = monthrange(today.year, today.month)[1]
    days_passed = today.day
    
    if days_passed > 0:
        daily_average = current_expenses / days_passed
        predicted_expense = daily_average * days_in_month
    else:
        predicted_expense = current_expenses

    return render(request, 'fintrack/budget.html', {
        'budget': budget,
        'month_label': current_month.strftime('%B %Y'),
        'current_expenses': current_expenses,
        'progress_percent': progress_percent,
        'current_income': current_income,
        'income_progress_percent': income_progress_percent,
        'days_in_month': days_in_month,
        'days_passed': days_passed,
        'predicted_expense': predicted_expense,
    })