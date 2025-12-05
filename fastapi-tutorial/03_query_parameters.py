from fastapi import FastAPI
from typing import Union

app = FastAPI()
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# クエリパラメータの使用例
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
## 例：/items/?skip=0&limit=10
### skip = 0, limit = 10 の2つのクエリパラメータを指定
### URLは文字列だが、宣言された型に基づいて自動的に変換される（skip:int = 0なので整数型）

## 関数内でデフォルト値を指定（skipのデフォルト値は0、limitのデフォルト値は10）
### 「/items/」は「/items/?skip=0&limit=10」と同じ意味になる
### 「/items/?skip=20」は「/items/?skip=20&limit=10」と同じ意味になる



# オプショナルなパラメータ
@app.get("/items1/{item_id}")
async def read_item_optional(item_id: str, q: Union[str, None] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
## パラメータqはオプショナル、デフォルト値はNone
## item_idはパスパラメータ、qはクエリパラメータ

# 必須のクエリパラメータ
@app.get("/items2/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item
## パラメータneedyは必須のクエリパラメータ
### 「/items2/foo」は必須パラメータneedyがないためエラー

# --------------------------------------------------
# Unionとは？
## 複数の型のうち、いずれかを許可するために使用
### 例：Union[str, None]は、str型またはNoneを許可
### Python 3.10以降では、|を使用可能（例：Union[int, str]はint | strと同じ）
# --------------------------------------------------



# クエリパラメータの型変換
@app.get("/items3/{item_id}")
async def read_item_with_short(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
## boolean型のクエリパラメータshortは、以下のいずれもTrueと解釈される
### /items3/foo?short=1
### /items3/foo?short=true
### /items3/foo?short=True
### /items3/foo?short=yes
### /items3/foo?short=on