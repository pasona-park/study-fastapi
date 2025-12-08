from typing import Annotated, Union, List
from fastapi import FastAPI, Header

app = FastAPI()

# --------------------------------------------------
# ヘッダーパラメータ
## ヘッダーパラメータを Query, Path, Cookie パラメータと同じ方法で定義可能
# --------------------------------------------------

# 基本的なHeaderパラメータの宣言
@app.get("/items/")
async def read_items(user_agent: Annotated[Union[str, None], Header()] = None):
    return {"User-Agent": user_agent}
# Path, Query, Cookie を使用した同じ構造を利用してヘッダーパラメータを宣言
# 最初の値はデフォルト値
# 追加の検証やアノテーションパラメータをすべて渡すことが可能

# --------------------------------------------------
# 技術的な詳細
## Header は Path, Query および Cookie の「姉妹」クラス
## 同じ共通の Param クラスを継承
## Query, Path, Header などを fastapi からインポートする際、これらは実際には特別なクラスを返す関数
# --------------------------------------------------

# --------------------------------------------------
# 重要
## ヘッダーを宣言するには Header を使用する必要がある
## そうしないと、そのパラメータをクエリパラメータとして解釈される
# --------------------------------------------------

# --------------------------------------------------
# 自動変換
## アンダースコア(_)をハイフン(-)に自動変換
# --------------------------------------------------

# アンダースコアの自動変換例
@app.get("/user-info/")
async def read_user_info(
    user_agent: Annotated[Union[str, None], Header()] = None,
    accept_language: Annotated[Union[str, None], Header()] = None,
):
    return {
        "User-Agent": user_agent,
        "Accept-Language": accept_language,
    }
# ほとんどの標準ヘッダーは「ハイフン」文字(-)で区切られる
# Pythonで user-agent のような形式の変数は無効
# Header は基本的にパラメータ名をアンダースコア(_)からハイフン(-)に変換してヘッダーを抽出・記録
# HTTPヘッダーは大文字小文字を区別しないため、「snake_case」として知られる標準Pythonスタイルで宣言可能
# User_Agent などのように最初の文字を大文字化する必要なく、Pythonコードのように user_agent として使用

# 自動変換の無効化
@app.get("/special-headers/")
async def read_special_headers(
    strange_header: Annotated[Union[str, None], Header(convert_underscores=False)] = None,
):
    return {"strange_header": strange_header}
# Header の convert_underscores パラメータを False に設定
# 注意: 一部のHTTPプロキシやサーバーはアンダースコアを含むヘッダーの使用を許可しない

# --------------------------------------------------
# 重複ヘッダー
## 重複ヘッダーを受信可能（複数の値を持つ同じヘッダー）
## 型定義でリストを使用して定義
## 重複ヘッダーのすべての値をPythonの list として受信
# --------------------------------------------------

@app.get("/tokens/")
async def read_tokens(x_token: Annotated[Union[List[str], None], Header()] = None):
    return {"X-Token values": x_token}
# 2回以上現れる可能性のある X-Token ヘッダーを宣言
# リクエスト例:
#   X-Token: foo
#   X-Token: bar
# レスポンス:
#   {
#       "X-Token values": [
#           "bar",
#           "foo"
#       ]
#   }

# 複数のヘッダーパラメータ
@app.get("/request-info/")
async def read_request_info(
    host: Annotated[Union[str, None], Header()] = None,
    user_agent: Annotated[Union[str, None], Header()] = None,
    accept: Annotated[Union[str, None], Header()] = None,
    accept_language: Annotated[Union[str, None], Header()] = None,
):
    return {
        "Host": host,
        "User-Agent": user_agent,
        "Accept": accept,
        "Accept-Language": accept_language,
    }
# 複数のヘッダーパラメータを同時に宣言可能

# --------------------------------------------------
# まとめ
## Header は Query, Path, Cookie と同じパターンを使用して宣言
## 変数のアンダースコアを心配する必要はない - FastAPIが自動的に変換する
# --------------------------------------------------
