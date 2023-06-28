"""
テストコードファイル

- トップ
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from mgmt.views import top_view


class TopTest(TestCase):
    """トップのテスト"""

    def setUp(self):
        """テストデータの初期設定"""
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)
        self.login_path = reverse("mgmt:login")
        self.top_path = reverse("mgmt:top")
        self.expected_path = self.login_path + "?next=" + self.top_path

    def tearDown(self):
        """テスト後に生成物を削除"""
        User.objects.all().delete()

    def test_get_return_200(self):
        """ステータスコード200のレスポンスが返ってくるかテスト"""
        response = self.client.get(self.top_path)
        self.assertEqual(response.status_code, 200)

    def test_uses_expected_view(self):
        """URLパスとビューがマッピングされているかテスト"""
        view = resolve(self.top_path)
        self.assertEqual(view.func.view_class, top_view.TopView)

    def test_uses_expected_template(self):
        """想定したテンプレートのレスポンスが返ってくるかテスト"""
        response = self.client.get(self.top_path)
        self.assertTemplateUsed(response, "mgmt/top.html")

    def test_should_return_expected_title(self):
        """想定したタイトルが表示されるかテスト"""
        response = self.client.get(self.top_path)
        self.assertContains(response, "管理TOP")

    def test_redirect_expected_page_when_logged_out(self):
        """未ログインの場合、ログインページにリダイレクトされるかテスト"""
        self.client.logout()
        response = self.client.get(self.top_path)
        self.assertRedirects(
            response,
            self.expected_path,
            status_code=302,
            target_status_code=200,
        )
