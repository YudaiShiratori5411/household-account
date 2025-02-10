import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from django.db.models import Sum
from django.db.models.functions import TruncMonth
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