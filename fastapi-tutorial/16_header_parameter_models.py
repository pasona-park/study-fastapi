from typing import Annotated, Union, List
from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI()

# --------------------------------------------------
# ヘッダーパラメータモデル
## 関連するヘッダーパラメータのグループがある場合、Pydanticモデルを作成して宣言可能
## 複数の場所でモデルを再利用可能
## すべてのパラメータに対する検証とメタデータを一度に宣言可能
# --------------------------------------------------

# 参考
## FastAPIバージョン 0.115.0 以降からサポート

# --------------------------------------------------
# Pydanticモデルを使用したヘッダーパラメータ
# --------------------------------------------------

class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: Union[str, None] = None
    traceparent: Union[str, None] = None
    x_tag: List[str] = []

@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers
# Pydanticモデルに必要なヘッダーパラメータを宣言
# そのパラメータを Header として宣言
# FastAPIはリクエストから受け取ったヘッダーから各フィールドのデータを抽出
# 定義したPydanticモデルを提供

# --------------------------------------------------
# ドキュメントの確認
## ドキュメントUI /docs で必要なヘッダーを確認できる
# --------------------------------------------------

# 複数のヘッダーフィールドを持つモデル
class RequestHeaders(BaseModel):
    user_agent: Union[str, None] = None
    accept_language: Union[str, None] = None
    accept_encoding: Union[str, None] = None
    referer: Union[str, None] = None

@app.get("/request-info/")
async def read_request_info(headers: Annotated[RequestHeaders, Header()]):
    return {
        "user_agent": headers.user_agent,
        "accept_language": headers.accept_language,
        "accept_encoding": headers.accept_encoding,
        "referer": headers.referer,
    }
# 複数のヘッダーフィールドを持つモデルを使用

# --------------------------------------------------
# 追加ヘッダーの禁止
## 一部の特別なユースケースで受信するヘッダーを制限可能
## Pydanticのモデル設定を使用して追加(extra)フィールドを禁止(forbid)可能
# --------------------------------------------------

class StrictHeaders(BaseModel):
    model_config = {"extra": "forbid"}

    host: str
    save_data: bool
    if_modified_since: Union[str, None] = None
    traceparent: Union[str, None] = None
    x_tag: List[str] = []

@app.get("/strict-items/")
async def read_strict_items(headers: Annotated[StrictHeaders, Header()]):
    return headers
# クライアントが追加のヘッダーを送信しようとするとエラーレスポンスを受け取る
# 例: クライアントが tool ヘッダーを plumbus 値で送信しようとするとエラー発生
# エラーレスポンス例:
# {
#     "detail": [
#         {
#             "type": "extra_forbidden",
#             "loc": ["header", "tool"],
#             "msg": "Extra inputs are not permitted",
#             "input": "plumbus"
#         }
#     ]
# }

# カスタム検証を含むヘッダーモデル
class AuthHeaders(BaseModel):
    authorization: str
    x_api_key: Union[str, None] = None
    x_request_id: Union[str, None] = None

@app.get("/protected/")
async def read_protected(headers: Annotated[AuthHeaders, Header()]):
    return {
        "authorization": headers.authorization,
        "x_api_key": headers.x_api_key,
        "x_request_id": headers.x_request_id,
    }
# 認証関連のヘッダーをモデルとしてグループ化

# --------------------------------------------------
# まとめ
## Pydanticモデルを使用してFastAPIでヘッダーを宣言できる
## モデルの再利用性と一括検証が可能
# --------------------------------------------------
