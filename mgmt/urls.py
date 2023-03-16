"""
URLマッピング定義ファイル

- ログイン
- トップ
- 果物マスタ管理(一覧, 登録, 編集, 論理削除)
- 販売情報管理(一覧, 登録, 編集, 削除)
- 販売統計情報
- リダイレクト(404)
"""
from django.urls import path, re_path

from mgmt.views import (
    fruit_view,
    login_view,
    redirect_view,
    sales_view,
    statistics_view,
    top_view
)


app_name = 'mgmt'

urlpatterns = [
    path(
        'login/',
        login_view.UserLoginView.as_view(),
        name='login',
    ),
    path(
        'top/',
        top_view.TopView.as_view(),
        name='top',
    ),
    path(
        'fruit/',
        fruit_view.FruitListView.as_view(),
        name='fruit',
    ),
    path(
        'fruit/create/',
        fruit_view.FruitCreateView.as_view(),
        name='fruit_create',
    ),
    path(
        'fruit/update/<int:pk>/',
        fruit_view.FruitUpdateView.as_view(),
        name='fruit_update',
    ),
    path(
        'fruit/delete/<int:pk>/',
        fruit_view.FruitDeleteView.as_view(),
        name='fruit_delete',
    ),
    path(
        'sales/',
        sales_view.SalesListView.as_view(),
        name='sales',
    ),
    path(
        'sales/create/',
        sales_view.SalesCreateView.as_view(),
        name='sales_create',
    ),
    path(
        'sales/update/<int:pk>/',
        sales_view.SalesUpdateView.as_view(),
        name='sales_update',
    ),
    path(
        'sales/delete/<int:pk>/',
        sales_view.SalesDeleteView.as_view(),
        name='sales_delete',
    ),
    path(
        'statistics/',
        statistics_view.StatisticsListView.as_view(),
        name='statistics',
    ),
    re_path(
        r'^.*$',
        redirect_view.NotFoundRedirectView.as_view(),
        name='redirect',
    ),
]
