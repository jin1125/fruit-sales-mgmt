"""
テストコードファイル

- 販売情報管理(一覧, 一覧[CSVインポート], 登録, 編集, 削除)
"""
import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from mgmt.forms import SalesCSVForm
from mgmt.models import Fruit, Sales
from mgmt.views import sales_view


class SalesListTest(TestCase):
    """販売情報管理(一覧)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.sales = Sales.objects.create(
            fruit=self.fruit,
            quantity=3,
            total=300,
            sale_date=timezone.now(),
        )
        self.login_path = reverse('mgmt:login')
        self.sales_path = reverse('mgmt:sales')
        self.expected_path = self.login_path + '?next=' + self.sales_path

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.sales_path)
        self.assertEqual(view.func.view_class, sales_view.SalesListView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertTemplateUsed(response, 'mgmt/sales.html')

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertContains(response, '販売情報管理')

    def test_should_return_db_fruit_value(self):
        """DBの果物の値が表示されるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertContains(response, self.sales.fruit)

    def test_should_return_db_quantity_value(self):
        """DBの個数の値が表示されるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertContains(response, self.sales.quantity)

    def test_should_return_db_total_value(self):
        """DBの合計金額の値が表示されるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertContains(response, self.sales.total)

    def test_should_return_db_sale_date_value(self):
        """DBの販売日時の値が表示されるかテスト"""
        response = self.client.get(self.sales_path)
        self.assertContains(
            response,
            timezone.localtime(self.sales.sale_date).strftime('%Y-%m-%d'),
        )

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.sales_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )


class SalesListCSVImportTest(TestCase):
    """販売情報管理(一覧)CSVインポートのテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.fruit_apple = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.fruit_orange = Fruit.objects.create(
            name='オレンジ',
            price=50,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.csv_filename = 'test.csv'
        self.text_filename = 'test.txt'
        self.content_type = 'text/csv'
        self.jst = datetime.timezone(datetime.timedelta(hours=9))
        self.sales_path = reverse('mgmt:sales')

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_csv_data_first_line_fruit_import_succeed(self):
        """CSVデータ(1行目)の果物のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_apple = Sales.objects.get(fruit=self.fruit_apple)
        self.assertEqual(sales_apple.fruit, self.fruit_apple)

    def test_csv_data_first_line_quantity_import_succeed(self):
        """CSVデータ(1行目)の個数のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_apple = Sales.objects.get(fruit=self.fruit_apple)
        self.assertEqual(sales_apple.quantity, 3)

    def test_csv_data_first_line_sale_date_import_succeed(self):
        """CSVデータ(1行目)の販売日時のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_apple = Sales.objects.get(fruit=self.fruit_apple)
        self.assertEqual(
            sales_apple.sale_date,
            datetime.datetime.fromisoformat(
                '2016-02-01 10:35'
            ).replace(tzinfo=self.jst),
        )

    def test_csv_data_second_line_fruit_import_succeed(self):
        """CSVデータ(2行目)の果物のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(sales_orange.fruit, self.fruit_orange)

    def test_csv_data_second_line_quantity_import_succeed(self):
        """CSVデータ(2行目)の個数のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(sales_orange.quantity, 5)

    def test_csv_data_second_line_sale_date_import_succeed(self):
        """CSVデータ(2行目)の販売日時のインポートが成功するかテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(
            sales_orange.sale_date,
            datetime.datetime.fromisoformat(
                '2016-02-02 10:30',
            ).replace(tzinfo=self.jst),
        )

    def test_ignore_if_data_type_illegal(self):
        """
        データ形式が不正な行はインポートを無視しているかテスト
        ex) intを期待しているがstr(TEST)だった場合
        """
        file_content = (
            'リンゴ,TEST,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        with self.assertRaises(Sales.DoesNotExist):
            Sales.objects.get(fruit=self.fruit_apple)

    def test_import_fruit_if_data_type_not_illegal(self):
        """データ形式が不正な行以外はインポートできているか2行目の果物をテスト"""
        file_content = (
            'リンゴ,TEST,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(sales_orange.fruit, self.fruit_orange)

    def test_import_quantity_if_data_type_not_illegal(self):
        """データ形式が不正な行以外はインポートできているか2行目の個数をテスト"""
        file_content = (
            'リンゴ,TEST,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(sales_orange.quantity, 5)

    def test_import_sale_date_if_data_type_not_illegal(self):
        """データ形式が不正な行以外はインポートできているか2行目の販売日時をテスト"""
        file_content = (
            'リンゴ,TEST,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        self.client.post(self.sales_path, request)
        sales_orange = Sales.objects.get(fruit=self.fruit_orange)
        self.assertEqual(
            sales_orange.sale_date,
            datetime.datetime.fromisoformat(
                '2016-02-02 10:30',
            ).replace(tzinfo=self.jst),
        )

    def allowed_file_type_is_valid_true(self):
        """許可されたファイル形式の場合は、バリデーションを通過することをテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.csv_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        response = self.client.post(self.sales_path, request)
        form = SalesCSVForm(response, request)
        self.assertTrue(form.is_valid())

    def not_arrowed_file_type_is_valid_false(self):
        """許可されていないファイル形式の場合は、バリデーションを通過しないことをテスト"""
        file_content = (
            'リンゴ,3,300,2016-02-01 10:35\n'
            'オレンジ,5,250,2016-02-02 10:30'
        ).encode('utf-8')

        csv_data = SimpleUploadedFile(
            self.text_filename,
            file_content,
            self.content_type
        )
        request = {'csv': csv_data}
        response = self.client.post(self.sales_path, request)
        form = SalesCSVForm(response, request)
        self.assertFalse(form.is_valid())


class SalesCreateTest(TestCase):
    """販売情報管理(登録)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            pk=0,
            name='リンゴ',
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.login_path = reverse('mgmt:login')
        self.sales_path = reverse('mgmt:sales')
        self.sales_create_path = reverse('mgmt:sales_create')
        self.expected_path = (
            self.login_path
            + '?next='
            + self.sales_create_path
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_create_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.sales_create_path)
        self.assertEqual(view.func.view_class, sales_view.SalesCreateView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_create_path)
        self.assertTemplateUsed(response, 'mgmt/sales_form.html')

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.sales_create_path)
        self.assertContains(response, '販売情報登録')

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.sales_create_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )

    def test_fruit_registration_succeed(self):
        """販売情報の果物の登録が成功するかテスト"""
        request = {
            'fruit': self.fruit.pk,
            'quantity': 5,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_create_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.fruit, self.fruit)

    def test_quantity_registration_succeed(self):
        """販売情報の個数の登録が成功するかテスト"""
        request = {
            'fruit': self.fruit.pk,
            'quantity': 5,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_create_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.quantity, request['quantity'])

    def test_total_registration_succeed(self):
        """販売情報の合計金額の登録が成功するかテスト"""
        request = {
            'fruit': self.fruit.pk,
            'quantity': 5,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_create_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        total = self.fruit.price * request['quantity']
        self.assertEqual(sales.total, total)

    def test_sale_date_registration_succeed(self):
        """販売情報の販売日時の登録が成功するかテスト"""
        request = {
            'fruit': self.fruit.pk,
            'quantity': 5,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_create_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.sale_date, request['sale_date'])

    def test_redirect_top_page_when_return_200(self):
        """
        販売情報の登録に成功した場合、
        販売情報管理(一覧)ページにリダイレクトされるかテスト
        """
        request = {
            'fruit': self.fruit.pk,
            'quantity': 5,
            'sale_date': timezone.now(),
        }
        response = self.client.post(self.sales_create_path, request)
        self.assertRedirects(
            response,
            self.sales_path,
            status_code=302,
            target_status_code=200,
        )


class SalesUpdateTest(TestCase):
    """販売情報管理(編集)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.fruit_apple = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.fruit_orange = Fruit.objects.create(
            name='オレンジ',
            price=50,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.sales = Sales.objects.create(
            fruit=self.fruit_apple,
            quantity=3,
            total=300,
            sale_date=timezone.now(),
        )
        self.login_path = reverse('mgmt:login')
        self.sales_path = reverse('mgmt:sales')
        self.sales_update_path = reverse(
            'mgmt:sales_update',
            kwargs={'pk': self.sales.pk},
        )
        self.expected_path = (
            self.login_path
            + '?next='
            + self.sales_update_path
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.sales_update_path)
        self.assertEqual(view.func.view_class, sales_view.SalesUpdateView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertTemplateUsed(response, 'mgmt/sales_form.html')

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertContains(response, '販売情報編集')

    def test_should_return_db_fruit_value(self):
        """DBの果物の値が表示されるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertContains(response, self.sales.fruit)

    def test_should_return_db_quantity_value(self):
        """DBの個数の値が表示されるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertContains(response, self.sales.quantity)

    def test_should_return_db_sale_date_value(self):
        """DBの販売日時が表示されるかテスト"""
        response = self.client.get(self.sales_update_path)
        self.assertContains(
            response,
            timezone.localtime(self.sales.sale_date).strftime('%Y-%m-%d')
        )

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.sales_update_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )

    def test_fruit_edit_succeed(self):
        """販売情報の果物の編集が成功するかテスト"""
        request = {
            'fruit': self.fruit_orange.pk,
            'quantity': 2,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_update_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.fruit, self.fruit_orange)

    def test_quantity_edit_succeed(self):
        """販売情報の個数の編集が成功するかテスト"""
        request = {
            'fruit': self.fruit_orange.pk,
            'quantity': 2,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_update_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.quantity, request['quantity'])

    def test_total_edit_succeed(self):
        """販売情報の合計金額の編集(自動計算)が成功するかテスト"""
        request = {
            'fruit': self.fruit_orange.pk,
            'quantity': 2,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_update_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        total = self.fruit_orange.price * request['quantity']
        self.assertEqual(sales.total, total)

    def test_sale_date_edit_succeed(self):
        """販売情報の販売日時の編集が成功するかテスト"""
        request = {
            'fruit': self.fruit_orange.pk,
            'quantity': 2,
            'sale_date': timezone.now(),
        }
        self.client.post(self.sales_update_path, request)
        sales = Sales.objects.get(fruit=request['fruit'])
        self.assertEqual(sales.sale_date, request['sale_date'])

    def test_redirect_expected_page_when_return_200(self):
        """
        販売情報の編集に成功した場合、
        販売情報管理(一覧)ページにリダイレクトされるかテスト
        """
        request = {
            'fruit': self.fruit_orange.pk,
            'quantity': 2,
            'sale_date': timezone.now(),
        }
        response = self.client.post(self.sales_update_path, request)
        self.assertRedirects(
            response,
            self.sales_path,
            status_code=302,
            target_status_code=200,
        )


class SalesDeleteTest(TestCase):
    """販売情報管理(削除)のテスト"""
    def setUp(self):
        """"テストデータの初期設定"""
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            name='リンゴ',
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.sales = Sales.objects.create(
            fruit=self.fruit,
            quantity=3,
            total=300,
            sale_date=timezone.now(),
        )
        self.login_path = reverse('mgmt:login')
        self.sales_path = reverse('mgmt:sales')
        self.sales_delete_path = reverse(
            'mgmt:sales_delete',
            kwargs={'pk': self.sales.pk}
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Sales.objects.all().delete()
        Fruit.objects.all().delete()

    def test_sales_delete_succeed(self):
        """販売情報の削除が成功するかテスト"""
        self.client.post(self.sales_delete_path)
        with self.assertRaises(Sales.DoesNotExist):
            Sales.objects.get(fruit=self.fruit)

    def test_redirect_expected_page_when_return_200(self):
        """
        販売情報の削除に成功した場合、
        販売情報管理(一覧)ページにリダイレクトされるかテスト
        """
        response = self.client.post(self.sales_delete_path)
        self.assertRedirects(
            response,
            self.sales_path,
            status_code=302,
            target_status_code=200,
        )
