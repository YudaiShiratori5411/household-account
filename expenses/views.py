from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Expense
from .forms import ExpenseForm
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime, timedelta
from .analytics import ExpensePrediction
from .analytics import ExpenseStatistics

import json
import pandas as pd


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

class ExpenseAnalyticsView(ListView):
    model = Expense
    template_name = 'expenses/expense_analytics.html'
    context_object_name = 'expenses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 期間を指定（デフォルトは過去6ヶ月）
        end_date = timezone.now()
        start_date = end_date - timedelta(days=180)

        # すべての支出データを取得
        expenses = Expense.objects.all().order_by('date')

        # 月別の支出合計
        monthly_expenses = (
            expenses.annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # カテゴリ別の支出合計
        category_expenses = (
            expenses.values('category')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        # グラフ用のデータを準備（JSON形式に変換）
        context.update({
            'monthly_labels': json.dumps([item['month'].strftime('%Y年%m月') for item in monthly_expenses]),
            'monthly_data': json.dumps([float(item['total']) for item in monthly_expenses]),
            'category_labels': json.dumps([item['category'] for item in category_expenses]),
            'category_data': json.dumps([float(item['total']) for item in category_expenses])
        })

        # 予測
        predictor = ExpensePrediction()
        df = predictor.prepare_data()

        if len(df) >= 3:  # 最低3ヶ月のデータがある場合のみ予測を行う
            predictor.train_model(df)
            prediction_data = predictor.get_prediction_with_confidence(df)
            context['prediction'] = prediction_data

            # 予測用の月を追加
            last_month = df['month'].iloc[-1]
            next_month = last_month + pd.DateOffset(months=1)
            prediction_month = next_month.strftime('%Y年%m月')
            context['prediction_month'] = prediction_month

        # 統計分析を実行
        stats = ExpenseStatistics(expenses)
        context.update({
            'basic_stats': stats.get_basic_stats(),
            'category_analysis': stats.get_category_analysis(),
            'time_analysis': stats.get_time_analysis(),
            'trend_analysis': stats.get_trend_analysis(),
        })

        return context