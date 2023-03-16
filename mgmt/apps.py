"""アプリケーション設定ファイル"""
from django.apps import AppConfig


class MgmtConfig(AppConfig):
    """アプリケーション構成を設定"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mgmt'
