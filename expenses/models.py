from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('食費', '食費'),
        ('交通費', '交通費'),
        ('住居費', '住居費'),
        ('光熱費', '光熱費'),
        ('娯楽費', '娯楽費'),
        ('その他', 'その他'),
    ]

    date = models.DateField('日付')
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES)
    amount = models.IntegerField('金額')
    description = models.CharField('内容', max_length=200)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount}円"