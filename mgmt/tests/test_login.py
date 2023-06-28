"""
テストコードファイル

- ログイン
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from mgmt.views import login_view


class UserLoginTest(TestCase):
    """ログインのテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.login_path = reverse("mgmt:login")
        self.top_path = reverse("mgmt:top")

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.login_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.login_path)
        self.assertEqual(view.func.view_class, login_view.UserLoginView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.login_path)
        self.assertTemplateUsed(response, "mgmt/login.html")

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.login_path)
        self.assertContains(response, "ログイン")

    def test_redirect_expected_page_when_return_200(self):
        """
        ログインが成功するかテスト
        成功した場合、トップページにリダイレクトされるかテスト
        """
        request = {"username": "test_user", "password": "test_password"}
        response = self.client.post(self.login_path, request)
        self.assertRedirects(
            response,
            self.top_path,
            status_code=302,
            target_status_code=200,
        )

    def test_redirect_expected_when_logged_in(self):
        """ログイン済みの場合、トップページにリダイレクトされるかテスト"""
        self.client.force_login(self.user)
        response = self.client.get(self.login_path)
        self.assertRedirects(response, self.top_path)
