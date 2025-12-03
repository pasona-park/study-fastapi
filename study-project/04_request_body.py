from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

# パスパラメータ、リクエストボディ、クエリパラメータを同時に指定することも可能
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
## パスに宣言されているitem_idはパスパラメータ
## データ型（int, float, str, boolなど）が指定されているqはクエリパラメータ
## Pydanticモデルitemはリクエストボディ

# --------------------------------------------------
# Pydanticとは？
## Pythonのデータバリデーションと設定管理のためのライブラリ
## データ型のチェック、バリデーションチェック、シリアライゼーションなどを提供し、データの入出力を簡素化
### シリアライゼーション(직렬화)：データ構造を保存や転送に適した形式（例：JSON）に変換するプロセス

# BaseModelとは？
## Pydancticの基本クラスで、データモデルを定義するために使用
## 提供機能
### 1. データ型チェック（name: strなら文字列のみ受け入れる）
### 2. バリデーション
### 4. シリアライゼーションとデシリアライゼーション（辞書やJSONとの変換）
### 5. 自動ドキュメント生成（FastAPIのSwagger UI）

## シリアライゼーションを行うメソッドの例
### item = Item(name="Laptop", price=999.99)
### item.dict()  → {'name': 'Laptop', 'price': 999.99, 'description': None, 'tax': None}
### item.json()  → '{"name": "Laptop", "price": 999.99, "description": null, "tax": null}'
# --------------------------------------------------