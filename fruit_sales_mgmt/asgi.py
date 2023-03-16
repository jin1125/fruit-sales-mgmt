"""ASGIアプリケーションの設定ファイル"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fruit_sales_mgmt.settings')

application = get_asgi_application()
