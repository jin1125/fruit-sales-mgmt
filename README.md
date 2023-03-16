# 果物販売管理システム

果物の販売管理を行うためのWebアプリケーションです。

---

## ページ構成

- 管理サイト
- ログイン
- 管理TOP
- 果物マスタ管理
  - 果物一覧
  - 果物登録
  - 果物編集
- 販売情報管理
  - 販売情報一覧(CSV登録)
  - 販売情報登録
  - 販売情報編集
- 販売統計情報

---

## 前提条件

- Python 3.8以上

---

## 実行手順

- 仮想環境を作成

    ```python
    python3 -m venv venv
    ```

- 仮想環境の有効化

    ```python
    source venv/bin/activate
    ```

- pipをアップデート

    ```python
    pip3 install --upgrade pip
    ```

- Djangoをインストール

    ```python
    pip3 install -r requirements.txt
    ```

- DBテーブルを生成

    ```python
    python3 manage.py migrate
    ```

- ユーザーを作成

    ```python
    python3 manage.py createsuperuser
    ```

- 初期データを設定

    ```python
    python3 manage.py loaddata init.json
    ```

- 開発用サーバーを起動

    ```python
    python3 manage.py runserver
    ```

- 表示されたURLにアクセス

    ```python
    http://127.0.0.1:8000/ など
    ```

---

## ポイント

- 保守性を意識した実装
    - docstring
    - テストコード
    - テストの自動化
    - 動的な設定値をenv設定
    - ファイル分割(views, tests)
