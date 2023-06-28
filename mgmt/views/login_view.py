"""
ビュー定義ファイル

- ログイン
"""
from django.contrib.auth.views import LoginView


class UserLoginView(LoginView):
    """ログインのビューを定義"""

    template_name = "mgmt/login.html"
    redirect_authenticated_user = True
