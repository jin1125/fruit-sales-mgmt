"""
ビュー定義ファイル

- リダイレクト(404)
"""
from django.urls import reverse_lazy
from django.views.generic import RedirectView


class NotFoundRedirectView(RedirectView):
    """リダイレクトのビューを定義"""

    url = reverse_lazy("mgmt:login")
