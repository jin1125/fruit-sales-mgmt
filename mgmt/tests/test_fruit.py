"""
テストコードファイル

- 果物マスタ管理(一覧, 登録, 編集, 論理削除)
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from mgmt.models import Fruit
from mgmt.views import fruit_view


class FruitListTest(TestCase):
    """果物マスタ管理(一覧)のテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            name="リンゴ",
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.login_path = reverse("mgmt:login")
        self.fruit_path = reverse("mgmt:fruit")
        self.expected_path = self.login_path + "?next=" + self.fruit_path

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.fruit_path)
        self.assertEqual(view.func.view_class, fruit_view.FruitListView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertTemplateUsed(response, "mgmt/fruit.html")

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertContains(response, "果物マスタ管理")

    def test_should_return_db_name_value(self):
        """DBの名前の値が表示されるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertContains(response, self.fruit.name)

    def test_should_return_db_price_value(self):
        """DBの単価の値が表示されるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertContains(response, self.fruit.price)

    def test_should_return_db_created_at_value(self):
        """DBの登録日時の値が表示されるかテスト"""
        response = self.client.get(self.fruit_path)
        self.assertContains(
            response,
            timezone.localtime(self.fruit.created_at).strftime("%Y-%m-%d"),
        )

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.fruit_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )


class FruitCreateTest(TestCase):
    """果物マスタ管理(登録)のテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)
        self.login_path = reverse("mgmt:login")
        self.fruit_path = reverse("mgmt:fruit")
        self.fruit_create_path = reverse("mgmt:fruit_create")
        self.expected_path = (
            self.login_path + "?next=" + self.fruit_create_path
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_create_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.fruit_create_path)
        self.assertEqual(view.func.view_class, fruit_view.FruitCreateView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_create_path)
        self.assertTemplateUsed(response, "mgmt/fruit_form.html")

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.fruit_create_path)
        self.assertContains(response, "果物登録")

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.fruit_create_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )

    def test_fruit_name_registration_succeed(self):
        """果物の名前の登録が成功するかテスト"""
        request = {"name": "リンゴ", "price": 100}
        self.client.post(self.fruit_create_path, request)
        fruit = Fruit.objects.get(name=request["name"])
        self.assertEqual(fruit.name, request["name"])

    def test_fruit_price_registration_succeed(self):
        """果物の単価の登録が成功するかテスト"""
        request = {"name": "リンゴ", "price": 100}
        self.client.post(self.fruit_create_path, request)
        fruit = Fruit.objects.get(name=request["name"])
        self.assertEqual(fruit.price, request["price"])

    def test_redirect_expected_page_when_return_200(self):
        """
        果物の登録に成功した場合、
        果物マスタ管理(一覧)ページにリダイレクトされるかテスト
        """
        request = {"name": "リンゴ", "price": 100}
        response = self.client.post(self.fruit_create_path, request)
        self.assertRedirects(
            response,
            self.fruit_path,
            status_code=302,
            target_status_code=200,
        )


class FruitUpdateTest(TestCase):
    """果物マスタ管理(編集)のテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            name="リンゴ",
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.login_path = reverse("mgmt:login")
        self.fruit_path = reverse("mgmt:fruit")
        self.fruit_update_path = reverse(
            "mgmt:fruit_update",
            kwargs={"pk": self.fruit.pk},
        )
        self.expected_path = (
            self.login_path + "?next=" + self.fruit_update_path
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Fruit.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_update_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.fruit_update_path)
        self.assertEqual(view.func.view_class, fruit_view.FruitUpdateView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.fruit_update_path)
        self.assertTemplateUsed(response, "mgmt/fruit_form.html")

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.fruit_update_path)
        self.assertContains(response, "果物編集")

    def test_should_return_db_name_value(self):
        """DBの名前の値が表示されるかテスト"""
        response = self.client.get(self.fruit_update_path)
        self.assertContains(response, self.fruit.name)

    def test_should_return_db_price_value(self):
        """DBの単価の値が表示されるかテスト"""
        response = self.client.get(self.fruit_update_path)
        self.assertContains(response, self.fruit.price)

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.fruit_update_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )

    def test_fruit_name_edit_succeed(self):
        """果物の名前の編集が成功するかテスト"""
        request = {"name": "オレンジ", "price": 150}
        self.client.post(self.fruit_update_path, request)
        fruit = Fruit.objects.get(pk=self.fruit.pk)
        self.assertEqual(fruit.name, request["name"])

    def test_fruit_price_edit_succeed(self):
        """果物の単価の編集が成功するかテスト"""
        request = {"name": "オレンジ", "price": 150}
        self.client.post(self.fruit_update_path, request)
        fruit = Fruit.objects.get(pk=self.fruit.pk)
        self.assertEqual(fruit.price, request["price"])

    def test_redirect_expected_page_when_return_200(self):
        """
        果物の登録に成功した場合、
        果物マスタ管理(一覧)ページにリダイレクトされるかテスト
        """
        request = {"name": "オレンジ", "price": 150}
        response = self.client.post(self.fruit_update_path, request)
        self.assertRedirects(
            response,
            self.fruit_path,
            status_code=302,
            target_status_code=200,
        )


class FruitDeleteTest(TestCase):
    """果物マスタ管理(論理削除)のテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)
        self.fruit = Fruit.objects.create(
            name="リンゴ",
            price=100,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_deleted=False,
        )
        self.login_path = reverse("mgmt:login")
        self.fruit_path = reverse("mgmt:fruit")
        self.fruit_delete_path = reverse(
            "mgmt:fruit_delete", kwargs={"pk": self.fruit.pk}
        )

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()
        Fruit.objects.all().delete()

    def test_fruit_logical_delete_succeed(self):
        """果物の論理削除が成功するかテスト"""
        self.client.post(self.fruit_delete_path)
        fruit = Fruit.objects.get(pk=self.fruit.pk)
        self.assertEqual(fruit.is_deleted, True)

    def test_redirect_expected_page_when_return_200(self):
        """
        果物の論理削除に成功した場合、
        果物マスタ管理(一覧)ページにリダイレクトされるかテスト
        """
        response = self.client.post(self.fruit_delete_path)
        self.assertRedirects(
            response,
            self.fruit_path,
            status_code=302,
            target_status_code=200,
        )
