from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, Union

app = FastAPI()

# --------------------------------------------------
# リクエスト例データの宣言
## アプリが受け取るデータの例を宣言可能
# --------------------------------------------------

# 1. Pydanticモデル内の追加JSONスキーマデータ
class ItemWithModelConfig(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }

@app.put("/items-model-config/{item_id}")
async def update_item_model_config(item_id: int, item: ItemWithModelConfig):
    results = {"item_id": item_id, "item": item}
    return results
# Pydantic v2では model_config 属性を使用
# "json_schema_extra" に examples を含むdictを設定
# 追加情報はモデルのJSONスキーマに追加され、APIドキュメントで使用される


# 2. Fieldの追加引数
class ItemWithFieldExamples(BaseModel):
    name: str = Field(examples=["Foo"])
    description: Union[str, None] = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: Union[float, None] = Field(default=None, examples=[3.2])

@app.put("/items-field-examples/{item_id}")
async def update_item_field_examples(item_id: int, item: ItemWithFieldExamples):
    results = {"item_id": item_id, "item": item}
    return results
# Field() を使用する際に追加の examples を宣言可能


# 3. Bodyにexamplesを含める
class ItemBasic(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

@app.put("/items-body-examples/{item_id}")
async def update_item_body_examples(
    item_id: int,
    item: Annotated[
        ItemBasic,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
# Body() に例データを含む examples を渡すことが可能
# Path(), Query(), Header(), Cookie(), Body(), Form(), File() などで使用可能


# 4. 複数のexamplesを含むBody
@app.put("/items-multiple-examples/{item_id}")
async def update_item_multiple_examples(
    *,
    item_id: int,
    item: Annotated[
        ItemBasic,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
                {
                    "name": "Bar",
                    "price": "35.4",
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
# 複数の例を渡すことが可能
# 例はボディデータの内部JSONスキーマの一部になる
# 現在のSwagger UIはJSONスキーマ内の複数例の表示をサポートしていない


# 5. OpenAPI特化のexamples (openapi_examples)
@app.put("/items-openapi-examples/{item_id}")
async def update_item_openapi_examples(
    *,
    item_id: int,
    item: Annotated[
        ItemBasic,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "通常の例",
                    "description": "**正常な**アイテムは正しく動作します。",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "変換されたデータの例",
                    "description": "FastAPIは価格の`文字列`を自動的に実際の`数値`に変換できます",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "無効なデータはエラーで拒否される",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results
# JSONスキーマが examples をサポートする前からOpenAPIは examples フィールドをサポート
# OpenAPI特化の examples は各パス操作の詳細に含まれる（JSONスキーマ内部ではない）
# Swagger UIはこの特定の examples フィールドを長くサポートしてきた
# 形式: (listではなく) 複数の例を含むdict

# openapi_examples の各例に含めることができる項目:
## summary: 例の短い説明
## description: マークダウンテキストを含むことができる長い説明
## value: 実際に表示される例（例: dict）
## externalValue: valueの代替で、例を指すURL

# --------------------------------------------------
# まとめ
## 1. model_config: Pydanticモデル全体に例を設定
## 2. Field(examples=[]): 各フィールドに例を設定
## 3. Body(examples=[]): リクエストボディに複数の例を設定（JSONスキーマ）
## 4. Body(openapi_examples={}): OpenAPI特化の例（Swagger UIで表示）
# --------------------------------------------------
