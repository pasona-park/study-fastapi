from typing import Annotated, Union
from fastapi import Cookie, FastAPI

app = FastAPI()

# --------------------------------------------------
# クッキーパラメータ
## クッキーパラメータを Query と Path パラメータと同じ方法で定義可能
# --------------------------------------------------

# 基本的なCookieパラメータの宣言
@app.get("/items/")
async def read_items(ads_id: Annotated[Union[str, None], Cookie()] = None):
    return {"ads_id": ads_id}
# Path と Query と同じ構造を使用
# 最初の値はデフォルト値
# 追加の検証やアノテーションパラメータをすべて渡すことが可能

# --------------------------------------------------
# 技術的な詳細
## Cookie は Path および Query の「姉妹」クラス
## 同じ共通の Param クラスを継承
## Query, Path, Cookie などは fastapi からインポートする際、実際には特別なクラスを返す関数
# --------------------------------------------------

# --------------------------------------------------
# 重要
## クッキーを宣言するには Cookie を使用する必要がある
## そうしないと、そのパラメータをクエリパラメータとして解釈される
# --------------------------------------------------

# 複数のCookieパラメータ
@app.get("/user-info/")
async def read_user_info(
    session_id: Annotated[Union[str, None], Cookie()] = None,
    user_token: Annotated[Union[str, None], Cookie()] = None,
):
    return {
        "session_id": session_id,
        "user_token": user_token,
    }
# 複数のクッキーパラメータを同時に宣言可能

# 検証付きCookieパラメータ
@app.get("/analytics/")
async def read_analytics(
    tracking_id: Annotated[Union[str, None], Cookie(min_length=10, max_length=50)] = None,
):
    return {"tracking_id": tracking_id}
# Cookie にも Query や Path と同様に検証パラメータを追加可能
# min_length, max_length などの検証オプションを使用できる

# --------------------------------------------------
# まとめ
## Cookie は Query, Path と同じパターンを使用して宣言
## クッキーを扱う際は必ず Cookie を使用すること
# --------------------------------------------------
