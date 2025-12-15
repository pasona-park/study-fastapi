from typing import Union, List, Dict
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

# --------------------------------------------------
# 追加モデル（Extra Models）
## 実際のアプリケーションでは、一つのエンティティに対して複数のモデルが必要
## 例：ユーザーエンティティの場合
### - 入力モデル：パスワードを含む（ユーザー登録時）
### - 出力モデル：パスワードを除外（API応答時）
### - データベースモデル：ハッシュ化されたパスワードを含む（DB保存時）
# --------------------------------------------------

# 1. 複数モデルパターンの基本例
class UserIn(BaseModel):
    username: str
    password: str  # 平文パスワード（入力時のみ）
    email: EmailStr
    full_name: Union[str, None] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None
    # password フィールドなし → セキュリティのため

class UserInDB(BaseModel):
    username: str
    hashed_password: str  # ハッシュ化されたパスワード
    email: EmailStr
    full_name: Union[str, None] = None

# パスワードハッシュ化の偽関数（実際の実装では適切なハッシュライブラリを使用）
def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

# ユーザー保存の偽関数
def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    # **user_in.dict() でPydanticオブジェクトをdictに変換してアンパック
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved
# 入力にはパスワードが含まれるが、出力からは自動的に除外される


# --------------------------------------------------
# Pydanticモデルの変換テクニック
## .dict() メソッド：PydanticオブジェクトをPython辞書に変換
## ** アンパック：辞書をキーワード引数として展開
# --------------------------------------------------

# 2. .dict()メソッドとアンパックの詳細例
def demonstrate_dict_unpacking():
    # Pydanticオブジェクトの作成
    user_in = UserIn(
        username="john", 
        password="secret", 
        email="john.doe@example.com"
    )
    
    # .dict()でPython辞書に変換
    user_dict = user_in.dict()
    # 結果: {'username': 'john', 'password': 'secret', 'email': 'john.doe@example.com', 'full_name': None}
    
    # **でアンパックして新しいモデル作成
    # UserInDB(**user_dict) は以下と同等：
    # UserInDB(
    #     username=user_dict["username"],
    #     password=user_dict["password"],
    #     email=user_dict["email"],
    #     full_name=user_dict["full_name"]
    # )
    
    # 追加フィールドと組み合わせ
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    
    return user_in_db


# --------------------------------------------------
# コード重複の削減 - 継承パターン
## 共通フィールドを基底クラスに定義し、各モデルで継承
## バグ、セキュリティ問題、コード非同期化問題を防止
# --------------------------------------------------

# 3. 継承を使った改良版モデル設計
class UserBase(BaseModel):
    """ユーザーの共通フィールドを定義する基底クラス"""
    username: str
    email: EmailStr
    full_name: Union[str, None] = None

class UserInImproved(UserBase):
    """入力用モデル - パスワード追加"""
    password: str

class UserOutImproved(UserBase):
    """出力用モデル - 基本フィールドのみ"""
    pass  # 基底クラスのフィールドをそのまま継承

class UserInDBImproved(UserBase):
    """データベース用モデル - ハッシュ化パスワード追加"""
    hashed_password: str

# 改良版のユーザー作成エンドポイント
@app.post("/user-improved/", response_model=UserOutImproved)
async def create_user_improved(user_in: UserInImproved):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDBImproved(**user_in.dict(), hashed_password=hashed_password)
    print("User saved with improved models!")
    return user_in_db


# --------------------------------------------------
# Union型 - 複数の型を許可する応答
## OpenAPIでは anyOf として表現される
## より具体的な型を先に、より一般的な型を後に配置
# --------------------------------------------------

# 4. Union型を使った複数タイプ応答
class BaseItem(BaseModel):
    description: str
    type: str

class CarItem(BaseItem):
    type: str = "car"  # デフォルト値で型を固定

class PlaneItem(BaseItem):
    type: str = "plane"
    size: int  # 飛行機特有のフィールド

# テストデータ
items_data = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items_data[item_id]
# 注意：より具体的なPlaneItemを先に配置


# --------------------------------------------------
# モデルのリスト応答
## List[Model] または Python 3.9+ では list[Model] を使用
# --------------------------------------------------

# 5. リスト形式の応答モデル
class SimpleItem(BaseModel):
    name: str
    description: str

simple_items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]

@app.get("/simple-items/", response_model=List[SimpleItem])
async def read_simple_items():
    return simple_items

# Python 3.9+ の場合
@app.get("/simple-items-modern/", response_model=list[SimpleItem])
async def read_simple_items_modern():
    return simple_items


# --------------------------------------------------
# 任意のdict応答
## Pydanticモデルを使わず、キーと値の型のみ指定
## 事前にフィールド名が分からない場合に有用
# --------------------------------------------------

# 6. 辞書形式の応答（キーと値の型のみ指定）
@app.get("/keyword-weights/", response_model=Dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}

# Python 3.9+ の場合
@app.get("/keyword-weights-modern/", response_model=dict[str, float])
async def read_keyword_weights_modern():
    return {"python": 4.5, "fastapi": 5.0}


# --------------------------------------------------
# 実戦的な例：商品管理システム
# --------------------------------------------------

# 7. 実戦例：商品管理システムでの複数モデル活用
class ProductBase(BaseModel):
    """商品の共通フィールド"""
    name: str
    description: Union[str, None] = None
    price: float

class ProductCreate(ProductBase):
    """商品作成用 - コスト情報含む"""
    cost: float  # 仕入れ価格（内部情報）
    supplier_id: int

class ProductPublic(ProductBase):
    """公開用 - 基本情報のみ"""
    id: int
    is_available: bool = True

class ProductInternal(ProductBase):
    """内部用 - 全情報含む"""
    id: int
    cost: float
    supplier_id: int
    profit_margin: float
    is_available: bool = True

# 商品作成（内部情報は応答から除外）
@app.post("/products/", response_model=ProductPublic)
async def create_product(product: ProductCreate):
    # 実際の実装では利益率計算やDB保存を行う
    profit_margin = (product.price - product.cost) / product.cost * 100
    
    product_internal = ProductInternal(
        **product.dict(),
        id=1,
        profit_margin=profit_margin,
        is_available=True
    )
    
    return product_internal  # ProductPublicモデルで自動フィルタリング

# 管理者用エンドポイント（全情報）
@app.get("/admin/products/{product_id}", response_model=ProductInternal)
async def get_product_internal(product_id: int):
    # 実際の実装では認証チェックとDB取得を行う
    return {
        "id": product_id,
        "name": "Sample Product",
        "description": "A great product",
        "price": 99.99,
        "cost": 50.00,
        "supplier_id": 123,
        "profit_margin": 99.98,
        "is_available": True
    }

# 一般ユーザー用エンドポイント（公開情報のみ）
@app.get("/products/{product_id}", response_model=ProductPublic)
async def get_product_public(product_id: int):
    # 同じデータでも異なるモデルで情報制御
    return {
        "id": product_id,
        "name": "Sample Product",
        "description": "A great product",
        "price": 99.99,
        "cost": 50.00,  # この情報は応答から除外される
        "supplier_id": 123,  # この情報は応答から除外される
        "profit_margin": 99.98,  # この情報は応答から除外される
        "is_available": True
    }


# --------------------------------------------------
# 重要なポイント
## 1. セキュリティ：平文パスワードの保存禁止
## 2. コード重複防止：継承による共通フィールド管理
## 3. 柔軟性：状況に応じた多様なモデル活用
## 4. 型安全性：Union、List、Dictなど多様な型サポート
## 5. 保守性：モデル継承による変更の影響範囲最小化
# --------------------------------------------------


# 8. 高度な例：条件付きフィールドを持つモデル
class UserProfile(BaseModel):
    """ユーザープロフィール基底クラス"""
    username: str
    email: EmailStr
    created_at: str

class PublicProfile(UserProfile):
    """公開プロフィール"""
    bio: Union[str, None] = None

class PrivateProfile(UserProfile):
    """プライベートプロフィール（本人のみ）"""
    bio: Union[str, None] = None
    phone: Union[str, None] = None
    address: Union[str, None] = None

class AdminProfile(UserProfile):
    """管理者用プロフィール（全情報）"""
    bio: Union[str, None] = None
    phone: Union[str, None] = None
    address: Union[str, None] = None
    last_login: Union[str, None] = None
    is_verified: bool = False
    account_status: str = "active"

# 条件に応じて異なるプロフィール情報を返す例
@app.get("/profiles/{user_id}/public", response_model=PublicProfile)
async def get_public_profile(user_id: int):
    return {
        "username": "john_doe",
        "email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "bio": "Hello, I'm John!",
        "phone": "+1234567890",  # 除外される
        "address": "123 Main St"  # 除外される
    }

@app.get("/profiles/{user_id}/private", response_model=PrivateProfile)
async def get_private_profile(user_id: int):
    # 実際の実装では認証チェックが必要
    return {
        "username": "john_doe",
        "email": "john@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "bio": "Hello, I'm John!",
        "phone": "+1234567890",
        "address": "123 Main St",
        "last_login": "2024-01-15T10:30:00Z",  # 除外される
        "is_verified": True,  # 除外される
        "account_status": "active"  # 除外される
    }