from typing import Union
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(q: Union[str, None] = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# パラメータqは文字列だけど、オプショナルなためNoneも許容
# Query関数を使って、qの最大長を50に制限している（max_length）
## min_lengthで最小長も指定可能

# --------------------------------------------------
# Query関数とは？
## FastAPIでクエリパラメータの詳細な設定を行うための関数

## 提供機能
### 1. 検証：max_length, min_length, regexなどのバリデーションルールを設定可能
### 2. デフォルト値の設定：default=Noneはオプショナル、default=は必須パラメータ
### 3. メタデータの追加：title, descriptionなどのドキュメント用メタデータを追加可能
### 4. その他の制約：gt（greater than）, lt（less than）
# --------------------------------------------------