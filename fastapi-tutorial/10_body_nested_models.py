from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import Union, List, Set, Dict

app = FastAPI()

# --------------------------------------------------
# ボディ - ネストされたモデル
## FastAPIを通じてネストされたモデルの定義、検証、ドキュメント化が可能
# --------------------------------------------------

# 1. リストタイプの基本使用
class ItemBasic(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: list = []  # サブタイプなしのリスト（すべてのタイプを許可）

@app.put("/items-basic/{item_id}")
async def update_item_basic(item_id: int, item: ItemBasic):
    results = {"item_id": item_id, "item": item}
    return results
# tags: list = [] はリストタイプだが、要素のタイプは指定していない
# つまり文字列、数値、booleanなど、すべてのタイプを許可
# 例: "tags": ["電子製品", "コンピュータ", 123, true]


# 2. タイプを指定したリスト
class ItemWithTypedList(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tags: List[str] = []  # 文字列のみを含むリスト

@app.put("/items-typed/{item_id}")
async def update_item_typed(item_id: int, item: ItemWithTypedList):
    return {"item_id": item_id, "item": item}
# tags: List[str] = [] は文字列のみを要素として持つリスト


# 3. Setタイプ（重複を許可しない）
class ItemWithSet(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tags: Set[str] = set()  # 重複しない文字列の集合

@app.put("/items-set/{item_id}")
async def update_item_set(item_id: int, item: ItemWithSet):
    return {"item_id": item_id, "item": item}
# Set[str] = set() : 重複データがあるリクエストを受信しても、ユニークな項目の集合に自動変換


# 4. ネストされたモデル（サブモデル）
class Image(BaseModel):
    url: str
    name: str

class ItemWithImage(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tags: Set[str] = set()
    image: Union[Image, None] = None  # Imageモデルをタイプとして使用

@app.put("/items-nested/{item_id}")
async def update_item_nested(item_id: int, item: ItemWithImage):
    return {"item_id": item_id, "item": item}
# Pydanticモデルを他のPydanticモデルの属性タイプとして使用可能
# リクエストボディ例:
# {
#     "name": "Foo",
#     "price": 42.0,
#     "tags": ["rock", "metal"],
#     "image": {
#         "url": "http://example.com/baz.jpg",
#         "name": "The Foo live"
#     }
# }


# 5. 特別なタイプと検証（HttpUrl）
class ImageWithValidation(BaseModel):
    url: HttpUrl  # strの代わりにHttpUrlを使用
    name: str

class ItemWithValidatedImage(BaseModel):
    name: str
    price: float
    image: Union[ImageWithValidation, None] = None

@app.put("/items-validated/{item_id}")
async def update_item_validated(item_id: int, item: ItemWithValidatedImage):
    return {"item_id": item_id, "item": item}
# HttpUrl: 有効なURLかどうかを自動検証
# 無効なURL（例: "invalid-url"）→ 検証失敗
# 有効なURL（例: "http://example.com/image.jpg"）→ 検証成功


# 6. サブモデルのリスト
class ItemWithImageList(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    images: Union[List[ImageWithValidation], None] = None  # Imageモデルのリスト

@app.put("/items-images/{item_id}")
async def update_item_images(item_id: int, item: ItemWithImageList):
    return {"item_id": item_id, "item": item}
# Pydanticモデルをリストやセットの要素タイプとして使用可能
# リクエストボディ例:
# {
#     "name": "Foo",
#     "images": [
#         {"url": "http://example.com/1.jpg", "name": "Image 1"},
#         {"url": "http://example.com/2.jpg", "name": "Image 2"}
#     ]
# }


# 7. 深くネストされたモデル
class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[ItemWithImageList]  # ItemリストでImageリストを含む

@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer
# モデルの中にモデル、その中にまたモデル...の形で無限にネスト可能
# 構造:
# Offer
#   └─ items: List[Item]
#        └─ images: List[Image]
#             └─ url: HttpUrl


# 8. 実戦例：複数の特殊タイプを使用
class ContactInfo(BaseModel):
    email: EmailStr = Field(..., description="連絡先メール")
    website: HttpUrl = Field(..., description="ウェブサイトURL")

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(gt=0, description="価格は0より大きい必要があります")
    contacts: List[ContactInfo] = []  # ネストされたモデルのリスト

@app.post("/products/")
async def create_product(product: Product):
    return product
# 複雑なデータ構造でもタイプ安全性 + 自動検証 + ドキュメント化が可能
# リクエストボディ例:
# {
#     "name": "Premium Product",
#     "price": 99.99,
#     "contacts": [
#         {
#             "email": "contact@example.com",
#             "website": "https://example.com"
#         }
#     ]
# }

# --------------------------------------------------
# 主要な特殊タイプ
## HttpUrl: HTTP/HTTPS URL
## EmailStr: メールアドレス
## IPvAnyAddress: IPアドレス
## UUID: UUID形式
## FilePath, DirectoryPath: ファイル、ディレクトリパス
# --------------------------------------------------


# 9. 純粋なリストのボディ
@app.post("/images/multiple/")
async def create_multiple_images(images: List[ImageWithValidation]):
    return images
# リクエストボディ自体が配列の場合、Pydanticモデルのリストを直接受け取れる
# リクエストボディ例:
# [
#     {"url": "http://example.com/1.jpg", "name": "Image 1"},
#     {"url": "http://example.com/2.jpg", "name": "Image 2"}
# ]
# 一般的な場合: {"images": [...]} ← オブジェクト内に配列
# 純粋なリスト: [...] ← 最上位が配列自体


# 10. 任意のdictボディ
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights
# キーと値のタイプのみ指定し、具体的なフィールド名を事前に定義する必要がない
# リクエストボディ例:
# {
#     "0": 0.5,
#     "1": 1.2,
#     "2": 0.8
# }
# Pydanticが自動変換:
## JSONのキーは常に文字列 ("0", "1", "2")
## Pydanticが自動的にintに変換 (0, 1, 2)
## 最終結果: {0: 0.5, 1: 1.2, 2: 0.8}

# いつ使用するか？
## 動的なキーを受け取る必要がある場合（事前にフィールド名が分からない場合）
## キーがint、UUIDなどの特殊タイプの場合
## 設定値、重み、マッピングデータなど

# Pydanticモデル vs Dict:
## Pydanticモデル: フィールドが固定
##   class Item(BaseModel):
##       name: str
##       price: float
## Dict: フィールドが動的
##   weights: Dict[int, float]  # どんなintキーでも受け取れる
