"""
ビュー定義ファイル

- 販売情報管理(一覧, 登録, 編集, 削除)
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from mgmt.forms import SalesCSVForm, SalesForm
from mgmt.models import Sales


class SalesListView(LoginRequiredMixin, ListView):
    """販売情報管理(一覧)のビューを定義"""
    context_object_name = 'sales_list'
    extra_context = {
        "table_headers": ['果物', '個数', '売り上げ', '販売日時', '', '']
    }
    queryset = Sales.objects.order_by('-sale_date')
    template_name = 'mgmt/sales.html'

    def get_context_data(self, *args, **kwargs):
        """
        SalesCSVFormをコンテキストに追加

        Returns
        -------
        context: dict
            SalesCSVFormを追加したコンテキスト
        """
        context = super().get_context_data(*args, **kwargs)
        context['form'] = SalesCSVForm()
        return context

    def post(self, request):
        """
        バリデーションに成功した場合は、CSVデータをDBに一括保存
        バリデーションに失敗した場合は、エラーメッセージを表示

        期待するCSVデータ形式 ※複数行可
            果物名(マスタ登録済み),個数(正数),値段(正数),販売日時(YYYY-MM-DD hh:mm)
            ex) リンゴ,1,270,2016-02-01 10:35

        Parameters
        ----------
        request: WSGIRequest
            POSTリクエスト

        Returns
        -------
        http_response_redirect: HttpResponseRedirect
            リダイレクト
        """
        form = SalesCSVForm(request.POST, request.FILES)

        if form.is_valid():
            csv_data = request.FILES['csv']
            form.save_csv(csv_data)

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class SalesCreateView(LoginRequiredMixin, CreateView):
    """販売情報管理(登録)のビューを定義"""
    form_class = SalesForm
    model = Sales
    success_url = reverse_lazy('mgmt:sales')
    template_name = 'mgmt/sales_form.html'

    def form_valid(self, form):
        """
        合計金額(total)をコンテキストに追加
        [合計金額 = 単価 * 個数]

        Parameters
        ----------
        form: SalesForm
            Salesフォーム

        Returns
        -------
        http_response_redirect: HttpResponseRedirect
            リダイレクト
        """
        self.object = form.save(commit=False)
        self.object.total = self.object.fruit.price * self.object.quantity
        self.object.save()
        return super().form_valid(form)


class SalesUpdateView(LoginRequiredMixin, UpdateView):
    """販売情報管理(編集)のビューを定義"""
    form_class = SalesForm
    model = Sales
    success_url = reverse_lazy('mgmt:sales')
    template_name = 'mgmt/sales_form.html'

    def form_valid(self, form):
        """
        合計金額(total)をコンテキストに追加
        [合計金額 = 単価 * 個数]

        Parameters
        ----------
        form: SalesForm
            Salesフォーム

        Returns
        -------
        http_response_redirect: HttpResponseRedirect
            リダイレクト
        """
        self.object = form.save(commit=False)
        self.object.total = self.object.fruit.price * self.object.quantity
        self.object.save()
        return super().form_valid(form)


class SalesDeleteView(LoginRequiredMixin, DeleteView):
    """販売情報管理(削除)のビューを定義"""
    model = Sales
    success_url = reverse_lazy('mgmt:sales')
