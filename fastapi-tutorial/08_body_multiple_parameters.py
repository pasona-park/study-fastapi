from typing import Union
from fastapi import FastAPI, Path, Body
from pydantic import BaseModel

app = FastAPI()


# --------------------------------------------------
# ボディ - 複数パラメータ
## Path、Query、リクエストボディ（HTTP送信時に渡されるデータ）を自由に混合して使用可能
## ボディパラメータのデフォルト値をNoneに設定して選択項目として指定可能
# --------------------------------------------------

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


# Path、Query、リクエストボディの混合例
@app.put("/items/{item_id}")
async def update_item_mixed(
    *,
    item_id: int = Path(title="取得するアイテムのID", ge=0, le=1000),
    q: Union[str, None] = None,
    item: Union[Item, None] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results
# Path、Query、リクエストボディの混合使用例
## item_id: パスパラメータ（URL経路の一部）
## q: クエリパラメータ（URL ?q=value）
## item: ボディパラメータ（PydanticオブジェクトのためFastAPIが自動認識）


# --------------------------------------------------
# 複数リクエストボディ
## 複数のリクエストボディを設定することも可能（itemとuser）
# --------------------------------------------------

@app.put("/products/{product_id}")
async def update_product_multi_body(product_id: int, item: Item, user: User):
    results = {"product_id": product_id, "item": item, "user": user}
    return results
# 複数リクエストボディの例
# 以下のようなボディ構造になる：
## {
##     "item": {"name": "商品名", "price": 1000},
##     "user": {"username": "ユーザー名", "full_name": "フルネーム"}
## }


# --------------------------------------------------
# ボディ内の単一値
## Body()を使用してクエリパラメータをボディに含める方法
# --------------------------------------------------

@app.put("/orders/{order_id}")
async def update_order_with_importance(
    order_id: int, 
    item: Item, 
    user: User, 
    importance: int = Body()
):
    results = {
        "order_id": order_id, 
        "item": item, 
        "user": user, 
        "importance": importance
    }
    return results
# Body()使用例：
## 基本ルール: importanceは単一値のためクエリパラメータになる
## Body()使用: importanceがリクエストボディに変更される

# 結果のボディ構造：
## {
##     "item": {...},
##     "user": {...},
##     "importance": 5
## }


# --------------------------------------------------
# 単一ボディパラメータ埋め込み
## 単一Pydanticモデルをボディでどのように処理するかembedで設定
# --------------------------------------------------

# 基本方式（embed=False、デフォルト値）
@app.put("/books/{book_id}")
async def update_book_normal(book_id: int, item: Item):
    return {"book_id": book_id, "item": item}
# 基本方式の例
# 予想されるボディ：
## {
##     "name": "本のタイトル",
##     "description": "説明",
##     "price": 1500
## }
## → Itemモデルのフィールドが最上位に位置


# embed=True使用
@app.put("/magazines/{magazine_id}")
async def update_magazine_embedded(magazine_id: int, item: Item = Body(embed=True)):
    return {"magazine_id": magazine_id, "item": item}
# embed=True使用例
# 予想されるボディ：
## {
##     "item": {
##         "name": "雑誌名",
##         "description": "説明",
##         "price": 800
##     }
## }
## → "item"というキー内にデータが入っている形態

# embed=Trueを使用する理由：
## 一貫性維持：複数モデルがある時と同じ構造維持
## 明示的構造：データがどのモデルに属するか分かりやすく表示
## 拡張性：後で新しいモデルが追加された時構造変更なし

# ※ 複数モデルが存在する時は自動でキーが生成される
# ※ embed=Trueは単一モデルで同じ構造を望む時に使用
