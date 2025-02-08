from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Expense
from .forms import ExpenseForm

class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    ordering = ['-date']
    context_object_name = 'expenses'

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        messages.success(self.request, '支出を登録しました')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容に誤りがあります')
        return super().form_invalid(form)

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/expense_form.html'
    success_url = reverse_lazy('expense-list')

    def form_valid(self, form):
        messages.success(self.request, '支出を更新しました')
        return super().form_valid(form)

class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expenses/expense_confirm_delete.html'
    success_url = reverse_lazy('expense-list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '支出を削除しました')
        return super().delete(request, *args, **kwargs)