"""
モデル定義ファイル

- Fruitモデル
- Salesモデル
"""
from django.db import models
from django.utils import timezone


class Fruit(models.Model):
    """Fruitモデルを定義"""

    name = models.CharField(
        max_length=20,
        verbose_name="名前",
    )
    price = models.PositiveIntegerField(
        verbose_name="単価",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="登録日時",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="削除",
    )

    def __str__(self):
        """
        管理サイトのレコードを判別するための名前を定義

        Returns
        -------
        record_name: str
            管理サイトでレコードを判別するための名前
        """
        return self.name


class Sales(models.Model):
    """Salesモデルを定義"""

    fruit = models.ForeignKey(
        Fruit,
        on_delete=models.PROTECT,
        verbose_name="果物",
    )
    quantity = models.PositiveIntegerField(
        verbose_name="個数",
    )
    total = models.PositiveIntegerField(
        blank=True,
        null=False,
        verbose_name="合計金額",
    )
    sale_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="販売日時",
    )

    def __str__(self):
        """
        管理サイトのレコードを判別するための名前を定義

        Returns
        -------
        record_name: str
            管理サイトでレコードを判別するための名前
        """
        return timezone.localtime(self.sale_date).strftime("%Y-%m-%d %H:%M")
