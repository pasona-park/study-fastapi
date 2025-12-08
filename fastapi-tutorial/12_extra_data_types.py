from datetime import datetime, time, timedelta
from typing import Annotated, Union
from uuid import UUID
from decimal import Decimal

from fastapi import Body, FastAPI

app = FastAPI()

# --------------------------------------------------
# 追加データ型
## 一般的なデータ型（int, float, str, bool）以外にも、より複雑なデータ型を使用可能
## 同じ機能を提供:
### - エディタサポート
### - 受信リクエストのデータ変換
### - レスポンスデータのデータ変換
### - データ検証
### - 自動アノテーションとドキュメント化
# --------------------------------------------------

# 使用可能な追加データ型の例
@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[Union[time, None], Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }
# 関数内のパラメータが固有のデータ型を持つ
# 日付操作が可能（例: start_datetime + process_after）
# 自動的に型変換と検証を実行

# --------------------------------------------------
# 主要な追加データ型
# --------------------------------------------------

# UUID
## 標準「汎用一意識別子」で、多くのデータベースやシステムでIDとして使用
## リクエストとレスポンスで str として表現される

# datetime.datetime
## Pythonの datetime.datetime
## リクエストとレスポンスで 2008-09-15T15:53:00+05:00 のようなISO 8601形式の str として表現

# datetime.date
## Pythonの datetime.date
## リクエストとレスポンスで 2008-09-15 のようなISO 8601形式の str として表現

# datetime.time
## Pythonの datetime.time
## リクエストとレスポンスで 14:23:55.003 のようなISO 8601形式の str として表現

# datetime.timedelta
## Pythonの datetime.timedelta
## リクエストとレスポンスで全体の秒（seconds）の float として表現
## Pydanticは「ISO 8601時差エンコーディング」として表現することも許可

# frozenset
## リクエストとレスポンスで set と同じように扱われる
## リクエスト時: リストを読み込み、重複を削除して set に変換
## レスポンス時: set は list に変換
## 生成されたスキーマは（JSONスキーマの uniqueItems を利用して）set の値が一意であることを明示

# bytes
## 標準Pythonの bytes
## リクエストとレスポンスで str として扱われる
## 生成されたスキーマはこれが binary「形式」の str であることを明示

# Decimal
## 標準Pythonの Decimal
## リクエストとレスポンスで float と同じように扱われる

# --------------------------------------------------
# その他の例
# --------------------------------------------------

@app.post("/products/")
async def create_product(
    product_id: UUID,
    price: Annotated[Decimal, Body()],
    created_at: Annotated[datetime, Body()],
    available_time: Annotated[Union[time, None], Body()] = None,
):
    return {
        "product_id": product_id,
        "price": price,
        "created_at": created_at,
        "available_time": available_time,
    }
# Decimal型は金額など精度が重要な数値に使用
# UUIDは一意なIDとして使用
# datetimeとtimeで日時情報を扱う

# --------------------------------------------------
# 参考
## すべての有効なPydanticデータ型: https://docs.pydantic.dev/latest/concepts/types/
# --------------------------------------------------
