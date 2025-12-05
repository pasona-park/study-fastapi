from fastapi import Body, FastAPI
from pydantic import BaseModel, Field
from typing import Union

app = FastAPI()

# --------------------------------------------------
# ボディ - フィールド
## PydanticのFieldを使用してモデル内で検証やメタデータを宣言可能
# --------------------------------------------------

from pydantic import Field

class ItemWithField(BaseModel):
    name: str
    description: Union[str, None] = Field(
        default=None, title="アイテムの説明", max_length=300
    )
    price: float = Field(gt=0, description="価格は0より大きい値である必要があります")
    tax: Union[float, None] = None


@app.put("/items-with-field/{item_id}")
async def update_item_with_field(item_id: int, item: ItemWithField = Body(embed=True)):
    return {"item_id": item_id, "item": item}
# PydanticのFieldを使用した検証とメタデータの例
## description: max_length=300で最大文字数制限
## price: gt=0で0より大きい値のみ許可
## title, descriptionでSwagger UIに表示される情報を設定

# Fieldで使用可能な検証オプション：
## gt, ge, lt, le: 数値の範囲制限
## min_length, max_length: 文字列の長さ制限
## regex: 正規表現パターンマッチング
## title, description: ドキュメント用メタデータ