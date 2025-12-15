from typing import Any, List, Union
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

# --------------------------------------------------
# レスポンスモデル（Response Model）
## FastAPIでAPI応答の構造を定義し、データをフィルタリングする機能
## 主な役割：
### 1. 出力データの型変換と検証
### 2. セキュリティのためのデータフィルタリング
### 3. OpenAPIスキーマの自動生成
### 4. 自動ドキュメント化
# --------------------------------------------------

# 1. 基本的なレスポンスモデルの使用
class Product(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []

# response_modelパラメータで応答構造を定義
@app.post("/products/", response_model=Product)
async def create_product(product: Product) -> Any:
    return product
# FastAPIは自動的にProductモデルの構造に合わせて応答をフィルタリング

# リストタイプのレスポンスモデル
@app.get("/products/", response_model=List[Product])
async def read_products() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]
# List[Product]でProductモデルのリストとして応答構造を定義


# 2. 入力と出力モデルの分離（セキュリティ重要）
class UserInput(BaseModel):
    username: str
    password: str  # 入力時には必要
    email: EmailStr
    full_name: Union[str, None] = None

class UserOutput(BaseModel):
    username: str
    # password フィールドなし！ → セキュリティのため出力から除外
    email: EmailStr
    full_name: Union[str, None] = None

# 入力にはパスワードが含まれるが、出力からは自動的に除外される
@app.post("/users/", response_model=UserOutput)
async def create_user(user: UserInput) -> Any:
    return user
# userにはpasswordが含まれているが、UserOutputモデルにpasswordフィールドがないため
# 応答からは自動的に除外される → セキュリティ確保


# 3. レスポンスモデルエンコーディングパラメータ
class ItemModel(BaseModel):
    name: str
    description: Union[str, None] = None  # デフォルト値: None
    price: float
    tax: float = 10.5  # デフォルト値: 10.5
    tags: List[str] = []  # デフォルト値: 空のリスト

# テストデータ
items_data = {
    "foo": {"name": "Foo", "price": 50.2},  # デフォルト値のみ
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},  # 一部カスタム値
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},  # 明示的にデフォルト値設定
}

# response_model_exclude_unset=True: 設定されていないデフォルト値を応答から除外
@app.get("/items/{item_id}", response_model=ItemModel, response_model_exclude_unset=True)
async def read_item_data(item_id: str):
    return items_data[item_id]
# 例：fooアイテムの場合 → {"name": "Foo", "price": 50.2} のみ応答
# description、tax、tagsのデフォルト値は応答に含まれない


# 4. 特定フィールドのみ含める（response_model_include）
@app.get(
    "/items/{item_id}/name",
    response_model=ItemModel,
    response_model_include={"name", "description"},  # nameとdescriptionのみ含める
)
async def read_item_name_only(item_id: str):
    return items_data[item_id]
# どのアイテムでも name と description フィールドのみ応答に含まれる
# 例：{"name": "Bar", "description": "The bartenders"}


# 5. 特定フィールドを除外する（response_model_exclude）
@app.get("/items/{item_id}/public", response_model=ItemModel, response_model_exclude={"tax"})
async def read_item_public_info(item_id: str):
    return items_data[item_id]
# tax フィールドを除外して応答（価格情報を隠す場合など）
# 例：{"name": "Bar", "description": "The bartenders", "price": 62, "tags": []}


# 6. リストを使った包含/除外（setに自動変換される）
@app.get(
    "/items/{item_id}/basic",
    response_model=ItemModel,
    response_model_include=["name", "price"],  # リストでも指定可能（内部でsetに変換）
)
async def read_item_basic_info(item_id: str):
    return items_data[item_id]
# FastAPIが自動的に list を set に変換して処理
# 基本情報（名前と価格）のみ応答


# 7. 複雑な例：条件付きレスポンスモデル
class AdminItemModel(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []
    internal_code: str  # 管理者専用フィールド
    cost: float  # 管理者専用フィールド

class PublicItemModel(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tags: List[str] = []
    # tax, internal_code, cost フィールドなし

# 管理者用エンドポイント（すべての情報）
@app.get("/admin/items/{item_id}", response_model=AdminItemModel)
async def read_admin_item(item_id: str):
    # 実際の実装では認証チェックが必要
    admin_data = {
        **items_data.get(item_id, {}),
        "internal_code": "INT-001",
        "cost": 25.0
    }
    return admin_data

# 一般ユーザー用エンドポイント（公開情報のみ）
@app.get("/public/items/{item_id}", response_model=PublicItemModel)
async def read_public_item(item_id: str):
    return items_data[item_id]
# 同じデータでも異なるレスポンスモデルを使用して情報を制御


# 8. その他の便利なパラメータ
@app.get("/items/{item_id}/defaults", response_model=ItemModel, response_model_exclude_defaults=True)
async def read_item_exclude_defaults(item_id: str):
    return items_data[item_id]
# response_model_exclude_defaults=True: デフォルト値と同じ値を持つフィールドを除外

@app.get("/items/{item_id}/none", response_model=ItemModel, response_model_exclude_none=True)
async def read_item_exclude_none(item_id: str):
    return items_data[item_id]
# response_model_exclude_none=True: None値を持つフィールドを除外


# --------------------------------------------------
# レスポンスモデルの重要なポイント
## 1. セキュリティ：機密情報の自動フィルタリング
## 2. パフォーマンス：不要なデータ転送の削減
## 3. API設計：クリーンで一貫性のある応答構造
## 4. ドキュメント化：OpenAPIスキーマの自動生成
## 5. 型安全性：コンパイル時の型チェック
# --------------------------------------------------


# 9. 実戦的な例：ユーザー管理システム
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Union[str, None] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Union[str, None] = None
    is_active: bool = True
    created_at: str
    # password は含まれない！

class UserList(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

# ユーザー作成（パスワードは応答から除外）
@app.post("/users/", response_model=UserResponse)
async def create_user_account(user: UserCreate) -> Any:
    # 実際の実装では、パスワードをハッシュ化してDBに保存
    return {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "password": user.password  # これは応答から自動除外される
    }

# ユーザーリスト（ページネーション付き）
@app.get("/users/", response_model=UserList)
async def get_users_list() -> Any:
    return {
        "users": [
            {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "per_page": 10
    }

# プロフィール情報のみ（最小限の情報）
@app.get("/users/{user_id}/profile", response_model=UserResponse, response_model_exclude={"email", "is_active", "created_at"})
async def get_user_profile(user_id: int) -> Any:
    return {
        "id": user_id,
        "username": "john_doe",
        "email": "john@example.com",  # 除外される
        "full_name": "John Doe",
        "is_active": True,  # 除外される
        "created_at": "2024-01-01T00:00:00Z"  # 除外される
    }
# 応答: {"id": 1, "username": "john_doe", "full_name": "John Doe"}