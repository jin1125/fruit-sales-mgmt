"""管理サイト設定ファイル"""
from django.contrib import admin

from mgmt.models import Fruit, Sales


class SalesInline(admin.TabularInline):
    """Fruitモデルのインライン表示設定(Salesモデル)"""
    extra = 2
    model = Sales
    verbose_name = '販売情報'
    verbose_name_plural = '販売情報'


class FruitAdmin(admin.ModelAdmin):
    """管理サイトでのFruitモデル表示設定"""
    fieldsets = [
        ('果物マスタ', {'fields': (('name', 'price', 'is_deleted'),)}),
    ]
    inlines = [SalesInline]
    search_fields = ['name']


admin.site.register(Fruit, FruitAdmin)
