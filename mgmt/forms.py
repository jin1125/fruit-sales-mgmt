"""
フォーム定義ファイル

- 果物マスタ管理(登録, 編集)
- 販売情報管理(CSVインポート, 登録, 編集)
"""
import collections
import csv
import datetime
import io
import logging
import re

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import FileExtensionValidator

from mgmt.models import Fruit, Sales


class FruitForm(forms.ModelForm):
    """果物マスタ管理(登録, 編集)のフォームを定義"""

    class Meta:
        fields = ("name", "price")
        model = Fruit


class SalesCSVForm(forms.Form):
    """販売情報管理(CSVインポート)のフォームを定義"""

    csv = forms.FileField(
        label="CSV一括登録",
        validators=[FileExtensionValidator(["csv"])],
    )

    def load_csv(self, csv_data):
        """
        アップロードしたCSVデータからCSVリーダーを生成(データ読み込み)

        Parameters
        ----------
        csv_data : InMemoryUploadedFile
            アップロードしたCSVデータ

        Returns
        -------
        csv_reader: reader
            CSVリーダー
        """
        csv_text = csv_data.read().decode("utf-8")
        csv_file = io.StringIO(csv_text)
        return csv.reader(csv_file)

    def validate_and_format_csv(self, record):
        """
        CSVリーダーのデータを1行ずつフォーマット(バリデーション)

        Parameters
        ----------
        record: list
            CSVリーダーのデータ(1行)

        Returns
        -------
        FormatCsv: FormatCsv
            Sales生成の為の引数
        """
        DATE_REGEX = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"

        if not record[1].isdigit():
            raise ValueError("個数に数値以外が入力されています")

        if not record[2].isdigit():
            raise ValueError("売り上げに数値以外が入力されています")

        if int(record[1]) < 0:
            raise ValueError("個数にマイナスの数値が入力されています")

        if int(record[2]) < 0:
            raise ValueError("売り上げにマイナスの数値が入力されています")

        if not re.fullmatch(DATE_REGEX, record[3]):
            raise ValueError("販売日時が YYYY-MM-DD HH:MM 形式になっていません")

        jst = datetime.timezone(datetime.timedelta(hours=9))
        FormatCsv = collections.namedtuple(
            "FormatCsv",
            ["fruit", "quantity", "total", "sale_date"],
        )
        return FormatCsv(
            Fruit.objects.get(name=record[0]),
            int(record[1]),
            int(record[2]),
            datetime.datetime.fromisoformat(
                record[3],
            ).replace(tzinfo=jst),
        )

    def get_sales_list(self, csv_reader):
        """
        Salesのリストを取得

        Parameters
        ----------
        csv_reader: reader
            CSVリーダー

        Returns
        -------
        sales_list: list
            Salesリスト
        """
        sales_list = []

        for i, record in enumerate(csv_reader):
            try:
                format_csv = self.validate_and_format_csv(record)

                sales = Sales(
                    fruit=format_csv.fruit,
                    quantity=format_csv.quantity,
                    total=format_csv.total,
                    sale_date=format_csv.sale_date,
                )
                sales_list.append(sales)
            except ObjectDoesNotExist as e:
                logging.warning(e)

                self.add_error(
                    "csv",
                    f"CSVデータ{i + 1}行目の果物が見つかりませんでした。",
                )
            except ValueError as e:
                logging.warning(e)

                self.add_error(
                    "csv",
                    f"CSVデータ{i + 1}行目の{e}",
                )
            except Exception as e:
                logging.warning(e)

                self.add_error(
                    "csv",
                    f"CSVデータ{i + 1}行目でエラーが発生しました。",
                )
        return sales_list

    def save_csv(self, csv_data):
        """
        アップロードしたCSVデータをDBに一括保存

        Parameters
        ----------
        csv_data : InMemoryUploadedFile
            アップロードしたCSVデータ
        """
        csv_reader = self.load_csv(csv_data)
        sales_list = self.get_sales_list(csv_reader)

        Sales.objects.bulk_create(sales_list)


class SalesForm(forms.ModelForm):
    """販売情報管理(登録, 編集)のフォームを定義"""

    class Meta:
        fields = ("fruit", "quantity", "sale_date")
        model = Sales
