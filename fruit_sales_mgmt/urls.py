"""
URLマッピング定義ファイル

- 管理サイト
- mgmtアプリケーション
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        settings.ADMIN_PATH,
        admin.site.urls,
    ),
    path(
        '',
        include('mgmt.urls'),
    ),
]
