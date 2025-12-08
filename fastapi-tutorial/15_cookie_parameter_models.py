from typing import Annotated, Union
from fastapi import Cookie, FastAPI
from pydantic import BaseModel

app = FastAPI()

# --------------------------------------------------
# クッキーパラメータモデル
## 関連するクッキーのグループがある場合、Pydanticモデルを作成して宣言可能
## 複数の場所でモデルを再利用可能
## すべてのパラメータに対する検証とメタデータを一度に宣言可能
# --------------------------------------------------

# 参考
## FastAPIバージョン 0.115.0 以降からサポート
## 同じ技術が Query, Cookie, Header に適用される

# --------------------------------------------------
# Pydanticモデルを使用したクッキー
# --------------------------------------------------

class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: Union[str, None] = None
    googall_tracker: Union[str, None] = None

@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies
# Pydanticモデルに必要なクッキーパラメータを宣言
# そのパラメータを Cookie として宣言
# FastAPIはリクエストから受け取ったクッキーから各フィールドのデータを抽出
# 定義したPydanticモデルを提供

# --------------------------------------------------
# ドキュメントの確認
## ドキュメントUI /docs で定義したクッキーを確認できる
# --------------------------------------------------

# --------------------------------------------------
# 重要
## 内部的にブラウザはクッキーを特別な方法で処理するため、JavaScriptが簡単にクッキーを触れない
## /docs でAPIドキュメントUIに移動すると、パス操作に対するクッキーのドキュメントを確認できる
## しかし、データを入力して「実行(Execute)」をクリックしても、ドキュメントUIはJavaScriptで動作するためクッキーは送信されない
## 何も値を書いていないかのようにエラーメッセージが表示される
# --------------------------------------------------

# 複数のクッキーパラメータを持つモデル
class UserCookies(BaseModel):
    user_id: str
    session_token: str
    preferences: Union[str, None] = None

@app.get("/user-profile/")
async def read_user_profile(cookies: Annotated[UserCookies, Cookie()]):
    return {
        "user_id": cookies.user_id,
        "session_token": cookies.session_token,
        "preferences": cookies.preferences,
    }
# 複数のクッキーフィールドを持つモデルを使用

# --------------------------------------------------
# 追加クッキーの禁止
## 一部の特別なユースケースで受信するクッキーを制限可能
## APIが自身のクッキー同意を制御する権限を持つ
## Pydanticのモデル設定を使用して追加(extra)フィールドを禁止(forbid)可能
# --------------------------------------------------

class StrictCookies(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    fatebook_tracker: Union[str, None] = None
    googall_tracker: Union[str, None] = None

@app.get("/strict-items/")
async def read_strict_items(cookies: Annotated[StrictCookies, Cookie()]):
    return cookies
# クライアントが追加のクッキーを送信しようとするとエラーレスポンスを受け取る
# 例: クライアントが santa_tracker クッキーを good-list-please 値で送信しようとするとエラー発生
# エラーレスポンス例:
# {
#     "detail": [
#         {
#             "type": "extra_forbidden",
#             "loc": ["cookie", "santa_tracker"],
#             "msg": "Extra inputs are not permitted",
#             "input": "good-list-please"
#         }
#     ]
# }

# --------------------------------------------------
# まとめ
## Pydanticモデルを使用してFastAPIでクッキーを宣言できる
## モデルの再利用性と一括検証が可能
# --------------------------------------------------
