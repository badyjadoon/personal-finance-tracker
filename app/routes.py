from os import abort
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_login import current_user, login_user, login_required, logout_user
from .model import Expense, Income, User
from .forms import ExpenseForm, IncomeForm, RegisterForm, LoginForm
from . import db
from sqlalchemy import func
import csv
from io import StringIO
from flask import Response
from datetime import date


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/manage')
@login_required
def manage():
    if current_user.is_authenticated:
        return render_template('manage.html')
    else:
        flash('Please log in to track your finance!', 'info')
        return redirect(url_for('main.login'))

@main.route('/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        new_expense = Expense(
            amount = form.amount.data,
            description = form.description.data,
            category = form.category.data,
            user_id = current_user.id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('main.expenses'))
    return render_template('expense_form.html', form=form, is_edit = False)

@main.route('/income/add', methods=['GET', 'POST'])
@login_required
def add_income():
    form = IncomeForm()
    if form.validate_on_submit():
        new_income = Income(
            amount = form.amount.data,
            description = form.description.data,
            source = form.source.data,
            user_id = current_user.id)
        db.session.add(new_income)
        db.session.commit()
        return redirect(url_for('main.incomes'))
    return render_template('Income_form.html', form=form, is_edit = False)


@main.route('/dashboard')
@login_required
def dashboard():
    total_income = db.session.query(func.coalesce(func.sum(Income.amount),0) ).filter(Income.user_id == current_user.id).scalar()
    total_expense = db.session.query(func.coalesce(func.sum(Expense.amount),0)).filter(Expense.user_id == current_user.id).scalar()
    income_count = Income.query.filter_by(user_id = current_user.id).count()
    expense_count = Expense.query.filter_by(user_id = current_user.id).count()
    transaction_count = income_count + expense_count
    today = date.today()
    month_start = date(today.year, today.month, 1)
    monthly_income = db.session.query(func.coalesce(func.sum(Income.amount),0)).filter(
        current_user.id == Income.user_id,
        Income.date >= month_start
    ).scalar()
    monthly_expense = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        current_user.id == Expense.user_id,
        Expense.date >= month_start
    ).scalar()
    return render_template('dashboard.html',monthly_income=monthly_income, monthly_expense=monthly_expense , total_income=total_income, total_expense=total_expense, transaction_count=transaction_count)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.name == form.name.data),
            (User.email == form.email.data)).first()
        if user:
            flash('User name or email already exist', 'danger')
            return redirect(url_for('main.register'))
        new_user = User(
            name = form.name.data,
            email = form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=["GET", 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')

            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@main.route('/expenses')
@login_required
def expenses():
    all_expenses = Expense.query.filter_by(user_id = current_user.id).order_by(Expense.date.desc())
    return render_template('expenses.html', expenses=all_expenses)

@main.route('/incomes')
@login_required
def incomes():
    all_incomes = Income.query.filter_by(user_id = current_user.id).order_by(Income.date.desc())
    return render_template('incomes.html', incomes=all_incomes)

@main.route('/income/edit/<int:income_id>', methods=['POST', 'GET'])
@login_required
def edit_income(income_id):
    current_income = Income.query.get_or_404(income_id)
    if current_user.id != current_income.user_id:
        abort()
    form = IncomeForm(obj=current_income)
    if form.validate_on_submit():
        current_income.amount = form.amount.data
        current_income.source = form.source.data
        current_income.date = form.date.data
        current_income.description = form.description.data
        db.session.commit()
        return redirect(url_for('main.incomes'))
    return render_template('income_form.html', form=form, title='Edit Income', is_edit = True)

@main.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    current_income = Income.query.get_or_404(income_id)
    if current_user.id != current_income.user_id:
        abort()
    db.session.delete(current_income)
    db.session.commit()
    return redirect(url_for('main.incomes'))

@main.route('/expense/edit/<int:expense_id>', methods=['POST', 'GET'])
@login_required
def edit_expense(expense_id):
    current_expense = Expense.query.get_or_404(expense_id)
    if current_user.id != current_expense.user_id:
        abort()
    form = ExpenseForm(obj=current_expense)
    if form.validate_on_submit():
        current_expense.amount = form.amount.data
        current_expense.category = form.category.data
        current_expense.date = form.date.data
        current_expense.description = form.description.data
        db.session.commit()
        return redirect(url_for('main.expenses'))
    return render_template('expense_form.html', form=form, title='Edit Expense', is_edit = True)

@main.route('/expense/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    current_expense = Expense.query.get_or_404(expense_id)
    if current_user.id != current_expense.user_id:
        abort()
    db.session.delete(current_expense)
    db.session.commit()
    return redirect(url_for('main.expenses'))

@main.route('/export/csv/<int:year>/<int:month>')
@login_required
def export_csv(year, month):

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date < end_date
    ).all()

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date < end_date
    ).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(['Type', 'Date', 'Category/Source', 'Amount', 'Description'])

    for i in incomes:
        writer.writerow(['Income', i.date, i.source, i.amount, i.description])

    for e in expenses:
        writer.writerow(['Expense', e.date, e.category, e.amount, e.description])

    response = Response(
        output.getvalue(),
        mimetype='text/csv'
    )

    response.headers['Content-Disposition'] = (
        f'attachment; filename=report_{year}_{month}.csv'
    )

    return response


