"""
テストコードファイル

- 販売統計情報
"""
import datetime

from django.contrib.auth.models import User
from django.db.models import Sum
from django.test import TestCase
from django.urls import resolve, reverse

from mgmt.models import Fruit, Sales
from mgmt.views import statistics_view


class StatisticsTest(TestCase):
    """販売統計情報のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.login_path = reverse('mgmt:login')
        self.statistics_path = reverse('mgmt:statistics')
        self.expected_path = self.login_path + '?next=' + self.statistics_path

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.statistics_path)
        self.assertEqual(
            view.func.view_class,
            statistics_view.StatisticsListView,
        )

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertTemplateUsed(response, 'mgmt/statistics.html')

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, '販売統計情報')

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.statistics_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )


class StatisticsAllPeriodTest(TestCase):
    """販売統計情報(全期間)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        jst = datetime.timezone(datetime.timedelta(hours=9))
        fruit_create_date = datetime.datetime(2022, 1, 1, tzinfo=jst)
        self.fruit = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=fruit_create_date,
            updated_at=fruit_create_date,
            is_deleted=False,
        )
        now = datetime.datetime.now(tz=jst)
        self.sales_1 = Sales.objects.create(
            fruit=self.fruit,
            quantity=1,
            total=100,
            sale_date=now,
        )
        last_month_last_day = now.replace(day=1) - datetime.timedelta(days=1)
        self.sales_2 = Sales.objects.create(
            fruit=self.fruit,
            quantity=2,
            total=200,
            sale_date=last_month_last_day,
        )
        last_month_first_day = self.sales_2.sale_date.replace(day=1)
        self.sales_3 = Sales.objects.create(
            fruit=self.fruit,
            quantity=3,
            total=300,
            sale_date=last_month_first_day,
        )
        two_months_ago_last_day = (
            self.sales_3.sale_date - datetime.timedelta(days=1)
        )
        self.sales_4 = Sales.objects.create(
            fruit=self.fruit,
            quantity=4,
            total=400,
            sale_date=two_months_ago_last_day,
        )
        two_months_ago_first_day = self.sales_4.sale_date.replace(day=1)
        self.sales_5 = Sales.objects.create(
            fruit=self.fruit,
            quantity=5,
            total=500,
            sale_date=two_months_ago_first_day,
        )
        three_months_ago_last_day = (
            self.sales_5.sale_date - datetime.timedelta(days=1)
        )
        self.sales_6 = Sales.objects.create(
            fruit=self.fruit,
            quantity=6,
            total=600,
            sale_date=three_months_ago_last_day,
        )
        self.statistics_path = reverse('mgmt:statistics')

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_should_return_all_period_total(self):
        """累計金額(全期間)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        all_period_total = Sales.objects.aggregate(Sum('total'))['total__sum']
        self.assertContains(response, all_period_total)


class StatisticsMonthlyPeriodTest(TestCase):
    """販売統計情報(月別の当月を含む過去3ヶ月間)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        jst = datetime.timezone(datetime.timedelta(hours=9))
        fruit_create_date = datetime.datetime(2022, 1, 1, tzinfo=jst)
        self.fruit = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=fruit_create_date,
            updated_at=fruit_create_date,
            is_deleted=False,
        )
        now = datetime.datetime.now(tz=jst)
        self.sales_1 = Sales.objects.create(
            fruit=self.fruit,
            quantity=1,
            total=100,
            sale_date=now,
        )
        last_month_last_day = now.replace(day=1) - datetime.timedelta(days=1)
        self.sales_2 = Sales.objects.create(
            fruit=self.fruit,
            quantity=2,
            total=200,
            sale_date=last_month_last_day,
        )
        last_month_first_day = self.sales_2.sale_date.replace(day=1)
        self.sales_3 = Sales.objects.create(
            fruit=self.fruit,
            quantity=3,
            total=300,
            sale_date=last_month_first_day,
        )
        two_months_ago_last_day = (
            self.sales_3.sale_date - datetime.timedelta(days=1)
        )
        self.sales_4 = Sales.objects.create(
            fruit=self.fruit,
            quantity=4,
            total=400,
            sale_date=two_months_ago_last_day,
        )
        two_months_ago_first_day = self.sales_4.sale_date.replace(day=1)
        self.sales_5 = Sales.objects.create(
            fruit=self.fruit,
            quantity=5,
            total=500,
            sale_date=two_months_ago_first_day,
        )
        three_months_ago_last_day = (
            self.sales_5.sale_date - datetime.timedelta(days=1)
        )
        self.sales_6 = Sales.objects.create(
            fruit=self.fruit,
            quantity=6,
            total=600,
            sale_date=three_months_ago_last_day,
        )
        self.statistics_path = reverse('mgmt:statistics')

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_should_return_monthly_period_current_month_total(self):
        """月別の合計金額(当月)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        current_month_total = self.sales_1.total
        self.assertContains(response, current_month_total)

    def test_should_return_monthly_period_last_month_total(self):
        """月別の合計金額(1ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        last_month_total = self.sales_2.total + self.sales_3.total
        self.assertContains(response, last_month_total)

    def test_should_return_monthly_period_two_months_ago_total(self):
        """月別の合計金額(2ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        two_months_ago_total = self.sales_4.total + self.sales_5.total
        self.assertContains(response, two_months_ago_total)

    def test_should_return_monthly_period_current_month_date(self):
        """月別の日付(当月)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_1.sale_date, '%Y/%m')
        )

    def test_should_return_monthly_period_last_month_date(self):
        """月別の日付(1ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_3.sale_date, '%Y/%m')
        )

    def test_should_return_monthly_period_two_months_ago_date(self):
        """月別の日付(2ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_5.sale_date, '%Y/%m')
        )

    def test_should_return_monthly_period_current_month_fruit_name(self):
        """月別の内訳の果物名(当月)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_1.fruit.name)

    def test_should_return_monthly_period_last_month_fruit_name(self):
        """月別の内訳の果物名(1ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_3.fruit.name)

    def test_should_return_monthly_period_two_months_ago_fruit_name(self):
        """月別の内訳の果物名(2ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_5.fruit.name)

    def test_should_return_monthly_period_current_month_quantity(self):
        """月別の内訳の個数(当月)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_1.quantity)

    def test_should_return_monthly_period_last_month_quantity(self):
        """月別の内訳の個数(1ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        last_month_quantity = self.sales_2.quantity + self.sales_3.quantity
        self.assertContains(response, last_month_quantity)

    def test_should_return_monthly_period_two_months_ago_quantity(self):
        """月別の内訳の個数(2ヶ月前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        two_months_ago_quantity = self.sales_4.quantity + self.sales_5.quantity
        self.assertContains(response, two_months_ago_quantity)


class StatisticsDailyPeriodTest(TestCase):
    """販売統計情報(日別の当日を含む過去3日間)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        jst = datetime.timezone(datetime.timedelta(hours=9))
        fruit_create_date = datetime.datetime(2022, 1, 1, tzinfo=jst)
        self.fruit = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=fruit_create_date,
            updated_at=fruit_create_date,
            is_deleted=False,
        )
        now = datetime.datetime.now(tz=jst)
        self.sales_1 = Sales.objects.create(
            fruit=self.fruit,
            quantity=1,
            total=100,
            sale_date=now,
        )
        date_one_days_ago = now - datetime.timedelta(days=1)
        self.sales_2 = Sales.objects.create(
            fruit=self.fruit,
            quantity=2,
            total=200,
            sale_date=date_one_days_ago,
        )
        date_two_days_ago = now - datetime.timedelta(days=2)
        self.sales_3 = Sales.objects.create(
            fruit=self.fruit,
            quantity=2,
            total=200,
            sale_date=date_two_days_ago,
        )
        date_three_days_ago = now - datetime.timedelta(days=3)
        self.sales_4 = Sales.objects.create(
            fruit=self.fruit,
            quantity=2,
            total=200,
            sale_date=date_three_days_ago,
        )
        self.statistics_path = reverse('mgmt:statistics')

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_should_return_daily_period_today_total(self):
        """日別の合計金額(当日)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_1.total)

    def test_should_return_daily_period_one_days_ago_total(self):
        """日別の合計金額(1日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_2.total)

    def test_should_return_daily_period_two_days_ago_total(self):
        """日別の合計金額(2日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_3.total)

    def test_should_return_daily_period_today_date(self):
        """日別の日付(当日)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_1.sale_date, '%Y/%m/%d')
        )

    def test_should_return_daily_period_one_days_ago_date(self):
        """日別の日付(1日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_2.sale_date, '%Y/%m/%d')
        )

    def test_should_return_daily_period_two_days_ago_date(self):
        """日別の日付(2日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(
            response,
            datetime.datetime.strftime(self.sales_3.sale_date, '%Y/%m/%d')
        )

    def test_should_return_daily_period_today_fruit_name(self):
        """日別の内訳の果物名(当日)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_1.fruit.name)

    def test_should_return_daily_period_one_days_ago_fruit_name(self):
        """日別の内訳の果物名(1日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_2.fruit.name)

    def test_should_return_daily_period_two_days_ago_fruit_name(self):
        """日別の内訳の果物名(2日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_3.fruit.name)

    def test_should_return_daily_period_today_quantity(self):
        """日別の内訳の個数(当日)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_1.quantity)

    def test_should_return_daily_period_one_days_ago_quantity(self):
        """日別の内訳の個数(1日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_2.quantity)

    def test_should_return_daily_period_two_days_ago_quantity(self):
        """日別の内訳の個数(2日前)の値が表示されるかテスト"""
        response = self.client.get(self.statistics_path)
        self.assertContains(response, self.sales_3.quantity)
