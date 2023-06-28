"""
ビュー定義ファイル

- 果物マスタ管理(一覧, 登録, 編集, 論理削除)
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from mgmt.forms import FruitForm
from mgmt.models import Fruit


class FruitListView(LoginRequiredMixin, ListView):
    """果物マスタ管理(一覧)のビューを定義"""

    context_object_name = "fruit_list"
    extra_context = {"table_headers": ["ID", "名称", "単価", "登録日時", ""]}
    queryset = Fruit.objects.filter(is_deleted=False).order_by("-updated_at")
    template_name = "mgmt/fruit.html"


class FruitCreateView(LoginRequiredMixin, CreateView):
    """果物マスタ管理(登録)のビューを定義"""

    form_class = FruitForm
    model = Fruit
    success_url = reverse_lazy("mgmt:fruit")
    template_name = "mgmt/fruit_form.html"


class FruitUpdateView(LoginRequiredMixin, UpdateView):
    """果物マスタ管理(編集)のビューを定義"""

    form_class = FruitForm
    model = Fruit
    success_url = reverse_lazy("mgmt:fruit")
    template_name = "mgmt/fruit_form.html"


class FruitDeleteView(LoginRequiredMixin, UpdateView):
    """果物マスタ管理(論理削除)のビューを定義"""

    fields = ("is_deleted",)
    model = Fruit
    success_url = reverse_lazy("mgmt:fruit")

    def form_valid(self, form):
        """
        論理削除

        Parameters
        ----------
        form: FruitForm
            Fruitフォーム

        Returns
        -------
        http_response_redirect: HttpResponseRedirect
            リダイレクト
        """
        self.object = form.save(commit=False)
        self.object.is_deleted = True
        self.object.save()
        return super().form_valid(form)
