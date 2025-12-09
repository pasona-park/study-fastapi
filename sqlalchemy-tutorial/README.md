# FastAPI Tutorial Environment

FastAPIとSQLAlchemyを学習するためのチュートリアル環境です。

## 環境構成

- **FastAPI**: Pythonのフレームワーク
- **SQLAlchemy**: PythonのORMライブラリ
- **MySQL**: データベース
- **Adminer**: データベース管理ツール

## 起動方法

```bash
cd sqlalchemy-tutorial
make upd
```

## アクセス先

- **API ドキュメント**: http://localhost:8001/docs
- **Adminer**: http://localhost:8081
  - サーバー: `db`
  - ユーザー名: `tutorial`
  - パスワード: `tutorial`
  - データベース: `tutorial`

## その他のコマンド

```bash
# 停止
make down

# API再起動
make restart

# 完全削除（ボリュームも削除）
make clean
```

## サンプルAPI

### GET /users
ユーザー一覧取得

### GET /addresses
アドレス一覧取得

## データベース構造

SQLAlchemy公式チュートリアルに基づいた構造:

- **user_account**: ユーザー情報
- **address**: メールアドレス情報
- **user_address**: ユーザーとアドレスの多対多関連テーブル

初期データとして3人のユーザー（spongebob, sandy, patrick）が登録されています。

## ファイル構成

```
sqlalchemy-tutorial/
├── main.py          # FastAPIアプリケーションのエントリーポイント
├── database.py      # データベース接続設定
├── models.py        # SQLAlchemyモデル定義
├── routers.py       # APIルート定義（ルーター層）
├── services.py      # ビジネスロジック（サービス層）
├── cruds.py         # データベース操作（CRUD層）
├── seed.py          # テーブル作成とダミーデータ投入
├── compose.yaml     # Docker Compose設定
└── Dockerfile       # Dockerイメージ設定
```

## アーキテクチャ

3層アーキテクチャを採用しています：

1. **ルーター層** (`routers.py`) - HTTPリクエスト処理、ルート定義
2. **サービス層** (`services.py`) - ビジネスロジック、データ変換
3. **CRUD層** (`cruds.py`) - データベース操作

## モデル変更し、DBに反映させたいとき

`init_db()`は既存テーブルに影響しません。モデルを変更した場合は、以下の手順でデータベースをリセットしてください。

```bash
make clean  # DBを完全削除
make upd    # 再起動（新しいテーブルが作成される）
```


## 学習の進め方

1. `models.py` でテーブル構造を確認・編集
2. `routers.py` でAPIエンドポイントを追加
3. ブラウザで http://localhost:8001/docs を開いてAPIをテスト
4. Adminerでデータベースの変化を確認
5. SQLAlchemyのリレーションシップ（relationship）の動作を確認
