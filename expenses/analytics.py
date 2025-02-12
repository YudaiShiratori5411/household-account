import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from django.db.models import Avg, Sum, Count, Max, Min
from django.db.models.functions import TruncMonth, ExtractWeekDay
from datetime import datetime, timedelta
from .models import Expense


class ExpensePrediction:
    def __init__(self):
        self.model = LinearRegression()

    def prepare_data(self):
        # 月別の支出データを取得
        monthly_expenses = (
            Expense.objects.annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # DataFrameに変換
        df = pd.DataFrame(monthly_expenses)
        df['month_num'] = range(len(df))  # 月を数値化

        return df

    def train_model(self, df):
        X = df['month_num'].values.reshape(-1, 1)
        y = df['total'].values
        self.model.fit(X, y)

    def predict_next_month(self, df):
        next_month = len(df)
        prediction = self.model.predict([[next_month]])[0]
        return max(0, prediction)  # 負の予測を防ぐ

    def get_prediction_with_confidence(self, df):
        # 基本的な予測
        next_month_prediction = self.predict_next_month(df)

        # 過去3ヶ月の変動を考慮
        recent_std = df['total'].tail(3).std()
        confidence_range = recent_std * 1.96  # 95%信頼区間

        return {
            'prediction': int(next_month_prediction),
            'min_prediction': int(max(0, next_month_prediction - confidence_range)),
            'max_prediction': int(next_month_prediction + confidence_range)
        }

class ExpenseStatistics:
    def __init__(self, expenses):
        self.expenses = expenses
        self.df = pd.DataFrame(list(expenses.values()))
        if not self.df.empty:
            self.df['date'] = pd.to_datetime(self.df['date'])

    def get_basic_stats(self):
        """基本的な統計情報を取得"""
        if self.df.empty:
            return {}

        # まず金額の計算前に、データを確認
        print("Debug - Raw data:", self.df)
        
        # 各値を計算
        total = self.df['amount'].sum()  # 総支出
        count = len(self.df)  # 取引回数
        average = total / count if count > 0 else 0  # 平均支出
        std_dev = self.df['amount'].std() if count > 1 else 0  # 標準偏差

        print("Debug - Amount values:", list(self.df['amount']))
        print("Debug - Total:", total)
        print("Debug - Count:", count)
        print("Debug - Average:", average)
        print("Debug - Std Dev:", std_dev)

        stats = {
            'total_expense': total,
            'average_expense': average,
            'transaction_count': count,
            'std_dev': std_dev if not pd.isna(std_dev) else 0
        }

        return stats

    def get_category_analysis(self):
        """カテゴリ別の分析"""
        if self.df.empty:
            return {}

        category_stats = {}
        for category in self.df['category'].unique():
            category_data = self.df[self.df['category'] == category]
            count = len(category_data)
            total = category_data['amount'].sum()
            avg = total / count if count > 0 else 0
            std = category_data['amount'].std() if count > 1 else None

            category_stats[category] = {
                'transaction_count': count,
                'total_amount': int(total),
                'average_amount': int(avg),
                'std_dev': int(std) if std is not None and not pd.isna(std) else None
            }

        return category_stats

    def get_time_analysis(self):
        """時系列分析"""
        if self.df.empty:
            return {}

        # 月別の集計
        monthly = self.df.groupby(self.df['date'].dt.strftime('%Y-%m')).agg({
            'amount': ['count', 'sum', 'mean']
        }).round(2)

        # 曜日別の集計（日本の曜日名を使用）
        weekday_map = {
            0: '月曜日', 1: '火曜日', 2: '水曜日',
            3: '木曜日', 4: '金曜日', 5: '土曜日', 6: '日曜日'
        }
        self.df['weekday'] = self.df['date'].dt.dayofweek.map(weekday_map)
        weekday = self.df.groupby('weekday').agg({
            'amount': ['count', 'sum', 'mean']
        }).round(2)

        return {
            'monthly_stats': monthly.to_dict(),
            'weekday_stats': weekday.to_dict()
        }

    def get_trend_analysis(self):
        """トレンド分析"""
        if self.df.empty:
            return {}

        # 支出の増加率を計算
        monthly_totals = self.df.groupby(self.df['date'].dt.strftime('%Y-%m'))['amount'].sum()
        growth_rates = monthly_totals.pct_change() * 100

        # 異常値の検出（平均から2標準偏差以上離れている支出）
        mean = self.df['amount'].mean()
        std = self.df['amount'].std()
        outliers = self.df[abs(self.df['amount'] - mean) > 2 * std]

        return {
            'growth_rates': growth_rates.to_dict(),
            'outliers': outliers.to_dict('records')
        }