"""
ビュー定義ファイル

- 販売統計情報
"""
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView

from mgmt.models import Sales


class StatisticsListView(LoginRequiredMixin, ListView):
    """販売統計情報のビューを定義"""
    context_object_name = 'statistics_list'
    extra_context = {
        "monthly_table_headers": ['月', '売り上げ', '内訳'],
        "daily_table_headers": ['日', '売り上げ', '内訳'],
    }
    model = Sales
    template_name = 'mgmt/statistics.html'

    def get_target_start_month(self):
        """
        当月を含む3ヶ月前の年月日(月初)を取得
        ※relativedeltaを使う場合は当メソッドは不要

        Returns
        -------
        two_months_ago_first_day: date
            当月を含む3ヶ月前の年月日(月初)
        """
        today = datetime.date.today()
        current_month_first_day = today.replace(day=1)
        last_month_last_day = (
            current_month_first_day - datetime.timedelta(days=1)
        )
        last_month_first_day = last_month_last_day.replace(day=1)
        two_months_ago_last_day = (
            last_month_first_day - datetime.timedelta(days=1)
        )
        return two_months_ago_last_day.replace(day=1)

    def get_monthly_sales(self, sales_list):
        """
        月別の販売統計情報を取得

        Parameters
        ----------
        sales_list: list
            Salesリスト

        Returns
        -------
        monthly_sales: dict
            月別の販売統計情報
        """
        target_start_month = self.get_target_start_month()
        monthly_sales_list = [
            sales for sales in sales_list
            if sales.sale_date.date() >= target_start_month
        ]
        monthly_sales = {}

        for sales in monthly_sales_list:
            date = datetime.datetime.strftime(sales.sale_date, '%Y/%m')
            fruit_name = sales.fruit.name

            if date not in monthly_sales:
                monthly_sales[date] = {
                    'period_total': 0,
                    'breakdown': {}
                }

            if fruit_name not in monthly_sales[date]['breakdown']:
                monthly_sales[date]['breakdown'][fruit_name] = {
                    'total': 0,
                    'quantity': 0
                }

            monthly_sales[date]['period_total']\
                += sales.total
            monthly_sales[date]['breakdown'][fruit_name]['total']\
                += sales.total
            monthly_sales[date]['breakdown'][fruit_name]['quantity']\
                += sales.quantity
        return monthly_sales

    def get_daily_sales(self, sales_list):
        """
        日別の販売統計情報を取得

        Parameters
        ----------
        sales_list: list
            Salesリスト

        Returns
        -------
        daily_sales: dict
            日別の販売統計情報
        """
        target_start_date = datetime.date.today() - datetime.timedelta(days=2)
        daily_sales_list = [
            sales for sales in sales_list
            if sales.sale_date.date() >= target_start_date
        ]
        daily_sales = {}

        for sales in daily_sales_list:
            date = datetime.datetime.strftime(sales.sale_date, '%Y/%m/%d')
            fruit_name = sales.fruit.name

            if date not in daily_sales:
                daily_sales[date] = {
                    'period_total': 0,
                    'breakdown': {}
                }

            if fruit_name not in daily_sales[date]['breakdown']:
                daily_sales[date]['breakdown'][fruit_name] = {
                    'total': 0,
                    'quantity': 0
                }

            daily_sales[date]['period_total']\
                += sales.total
            daily_sales[date]['breakdown'][fruit_name]['total']\
                += sales.total
            daily_sales[date]['breakdown'][fruit_name]['quantity']\
                += sales.quantity
        return daily_sales

    def get_context_data(self, *args, **kwargs):
        """
        累計、月別、日別の販売統計情報をコンテキストに追加
            累計: 全期間(合計金額)
            月別: 当月を含む過去3ヶ月間(販売統計情報)
            日別: 当日を含む過去3日間(販売統計情報)

        Returns
        -------
        context: dict
            累計、月別、日別の販売統計情報を追加したコンテキスト
        """
        context = super().get_context_data(*args, **kwargs)
        sales_list = context['object_list']

        for sales in sales_list:
            sales.sale_date = timezone.localtime(sales.sale_date)

        all_period_total = sum(sales.total for sales in sales_list)
        monthly_sales = self.get_monthly_sales(sales_list)
        daily_sales = self.get_daily_sales(sales_list)

        context['all_period_total'] = all_period_total
        context['monthly_sales'] = monthly_sales
        context['daily_sales'] = daily_sales
        return context
