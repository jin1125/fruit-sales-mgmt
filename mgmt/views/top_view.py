"""
ビュー定義ファイル

- トップ
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class TopView(LoginRequiredMixin, TemplateView):
    """トップのビューを定義"""

    template_name = "mgmt/top.html"
