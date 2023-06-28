"""
テストコードファイル

- リダイレクト(404)
"""
from django.test import TestCase
from django.urls import reverse


class RedirectTest(TestCase):
    """リダイレクト(404)のテスト"""

    def test_redirect_expected_page_when_logged_out(self):
        """未定義URLへのアクセスは、ログインページにリダイレクトされるかテスト"""
        test_404_path = "/test_404_path/"
        expected_path = reverse("mgmt:login")
        response = self.client.get(test_404_path)
        self.assertRedirects(
            response,
            expected_path,
            status_code=302,
            target_status_code=200,
        )
