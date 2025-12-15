from typing import Union, List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

# --------------------------------------------------
# ボディ更新（Body Updates）
## HTTP PUTとPATCHメソッドを使用して既存データを更新する機能
## 主な違い：
### PUT：完全置換（全体データを新しいデータで置き換え）
### PATCH：部分更新（提供されたフィールドのみ更新）
## 重要なPydanticメソッド：
### - exclude_unset: 設定されていないデフォルト値を除外
### - copy/model_copy: モデルのコピーを作成して更新
# --------------------------------------------------

# 基本モデル定義
class Item(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[float, None] = None
    tax: float = 10.5
    tags: List[str] = []

# テストデータ
items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

# --------------------------------------------------
# 1. PUT による完全置換更新
# --------------------------------------------------

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    """アイテム取得"""
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]

@app.put("/items/{item_id}", response_model=Item)
async def update_item_put(item_id: str, item: Item):
    """
    PUT による完全置換更新
    - 既存データを新しいデータで完全に置き換え
    - 提供されていないフィールドはデフォルト値になる
    - 注意：既存の値が失われる可能性がある
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # JSON互換形式に変換して保存
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    
    return update_item_encoded

# PUT の問題点を示すエンドポイント
@app.put("/items-demo/{item_id}", response_model=Item)
async def update_item_put_demo(item_id: str, item: Item):
    """
    PUT の問題点デモ
    例：barアイテム（tax: 20.2）に対して {"name": "Barz", "price": 3} だけ送信すると
    tax が 20.2 から 10.5（デフォルト値）に変更されてしまう
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    original_data = items[item_id].copy()
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    
    return {
        "message": "PUT update completed",
        "original_data": original_data,
        "updated_data": update_item_encoded,
        "warning": "Some fields may have been reset to default values"
    }


# --------------------------------------------------
# 2. PATCH による部分更新
# --------------------------------------------------

@app.patch("/items/{item_id}", response_model=Item)
async def update_item_patch(item_id: str, item: Item):
    """
    PATCH による部分更新
    - 提供されたフィールドのみ更新
    - 既存データは保持される
    - exclude_unset=True を使用して設定されたフィールドのみ取得
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # 既存データを取得してPydanticモデルに変換
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    
    # 更新データから設定されたフィールドのみ抽出
    update_data = item.dict(exclude_unset=True)
    
    # 既存モデルのコピーを作成し、更新データで更新
    updated_item = stored_item_model.copy(update=update_data)
    
    # JSON互換形式に変換して保存
    items[item_id] = jsonable_encoder(updated_item)
    
    return updated_item


# --------------------------------------------------
# 3. より複雑なモデルでの部分更新例
# --------------------------------------------------

class UserProfile(BaseModel):
    username: Union[str, None] = None
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    age: Union[int, None] = None
    bio: Union[str, None] = None
    preferences: Dict[str, Any] = {}
    last_updated: Union[datetime, None] = None

# ユーザープロファイルデータ
user_profiles = {
    "user1": {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "age": 30,
        "bio": "Software developer",
        "preferences": {"theme": "dark", "notifications": True},
        "last_updated": "2024-01-01T00:00:00"
    }
}

@app.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """ユーザープロファイル取得"""
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    return user_profiles[user_id]

@app.patch("/users/{user_id}/profile", response_model=UserProfile)
async def update_user_profile(user_id: str, profile: UserProfile):
    """
    ユーザープロファイルの部分更新
    - 提供されたフィールドのみ更新
    - 最終更新時刻を自動設定
    """
    if user_id not in user_profiles:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 既存データを取得
    stored_profile_data = user_profiles[user_id]
    stored_profile_model = UserProfile(**stored_profile_data)
    
    # 更新データを抽出（設定されたフィールドのみ）
    update_data = profile.dict(exclude_unset=True)
    
    # 最終更新時刻を追加
    update_data["last_updated"] = datetime.now()
    
    # モデル更新
    updated_profile = stored_profile_model.copy(update=update_data)
    
    # 保存
    user_profiles[user_id] = jsonable_encoder(updated_profile)
    
    return updated_profile


# --------------------------------------------------
# 4. 詳細な更新プロセスのデモ
# --------------------------------------------------

@app.patch("/items/{item_id}/detailed", response_model=Dict[str, Any])
async def update_item_detailed_process(item_id: str, item: Item):
    """
    詳細な部分更新プロセスのデモ
    - 各ステップの結果を表示
    - デバッグや学習用
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # ステップ1: 既存データ取得
    stored_item_data = items[item_id]
    
    # ステップ2: Pydanticモデルに変換
    stored_item_model = Item(**stored_item_data)
    
    # ステップ3: 更新データ抽出（exclude_unset=True）
    update_data = item.dict(exclude_unset=True)
    
    # ステップ4: モデル更新
    updated_item = stored_item_model.copy(update=update_data)
    
    # ステップ5: JSON互換形式に変換
    json_compatible_data = jsonable_encoder(updated_item)
    
    # ステップ6: 保存
    items[item_id] = json_compatible_data
    
    return {
        "message": "Detailed update process completed",
        "steps": {
            "1_original_data": stored_item_data,
            "2_original_model": stored_item_model.dict(),
            "3_update_data": update_data,
            "4_updated_model": updated_item.dict(),
            "5_json_compatible": json_compatible_data
        },
        "final_result": json_compatible_data
    }


# --------------------------------------------------
# 5. 異なる更新モデルの使用例
# --------------------------------------------------

# 作成用モデル（必須フィールドあり）
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Union[str, None] = None
    price: float = Field(..., gt=0)
    tax: float = Field(default=10.5, ge=0)
    tags: List[str] = []

# 更新用モデル（すべてオプション）
class ItemUpdate(BaseModel):
    name: Union[str, None] = Field(None, min_length=1, max_length=100)
    description: Union[str, None] = None
    price: Union[float, None] = Field(None, gt=0)
    tax: Union[float, None] = Field(None, ge=0)
    tags: Union[List[str], None] = None

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """
    アイテム作成（必須フィールドあり）
    - 作成専用モデルを使用
    - 必須フィールドの検証
    """
    item_id = f"item_{len(items) + 1}"
    item_data = jsonable_encoder(item)
    items[item_id] = item_data
    
    return item_data

@app.patch("/items-v2/{item_id}", response_model=Item)
async def update_item_v2(item_id: str, item: ItemUpdate):
    """
    改良版部分更新
    - 更新専用モデルを使用
    - より厳密な検証
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    
    # 更新データ抽出
    update_data = item.dict(exclude_unset=True)
    
    # None値を除外（明示的にNoneを設定した場合は更新）
    filtered_update_data = {k: v for k, v in update_data.items() if v is not None}
    
    # モデル更新
    updated_item = stored_item_model.copy(update=filtered_update_data)
    
    # 保存
    items[item_id] = jsonable_encoder(updated_item)
    
    return updated_item


# --------------------------------------------------
# 6. 条件付き更新の例
# --------------------------------------------------

class ProductStatus(BaseModel):
    status: str = Field(..., regex="^(active|inactive|discontinued)$")
    reason: Union[str, None] = None
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.now)

# 商品データ
products = {
    "prod1": {
        "name": "Product 1",
        "price": 100.0,
        "status": "active",
        "updated_by": "system",
        "updated_at": "2024-01-01T00:00:00"
    }
}

@app.patch("/products/{product_id}/status")
async def update_product_status(product_id: str, status_update: ProductStatus):
    """
    商品ステータスの条件付き更新
    - ステータス変更の履歴記録
    - ビジネスルールの適用
    """
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    
    current_product = products[product_id]
    current_status = current_product.get("status")
    
    # ビジネスルール：discontinuedからactiveへの変更は禁止
    if current_status == "discontinued" and status_update.status == "active":
        raise HTTPException(
            status_code=400,
            detail="Cannot reactivate discontinued product"
        )
    
    # 更新データ準備
    update_data = {
        "status": status_update.status,
        "updated_by": status_update.updated_by,
        "updated_at": status_update.updated_at,
    }
    
    if status_update.reason:
        update_data["status_reason"] = status_update.reason
    
    # 更新実行
    products[product_id].update(update_data)
    
    return {
        "message": "Product status updated successfully",
        "product_id": product_id,
        "old_status": current_status,
        "new_status": status_update.status,
        "updated_data": products[product_id]
    }


# --------------------------------------------------
# 7. バッチ更新の例
# --------------------------------------------------

class BatchUpdateItem(BaseModel):
    item_id: str
    updates: ItemUpdate

class BatchUpdateRequest(BaseModel):
    items: List[BatchUpdateItem]

@app.patch("/items/batch")
async def batch_update_items(batch_request: BatchUpdateRequest):
    """
    複数アイテムの一括部分更新
    - トランザクション的な処理
    - エラーハンドリング
    """
    results = []
    errors = []
    
    for batch_item in batch_request.items:
        try:
            item_id = batch_item.item_id
            
            if item_id not in items:
                errors.append({
                    "item_id": item_id,
                    "error": "Item not found"
                })
                continue
            
            # 部分更新実行
            stored_item_data = items[item_id]
            stored_item_model = Item(**stored_item_data)
            update_data = batch_item.updates.dict(exclude_unset=True)
            updated_item = stored_item_model.copy(update=update_data)
            items[item_id] = jsonable_encoder(updated_item)
            
            results.append({
                "item_id": item_id,
                "status": "updated",
                "data": jsonable_encoder(updated_item)
            })
            
        except Exception as e:
            errors.append({
                "item_id": batch_item.item_id,
                "error": str(e)
            })
    
    return {
        "message": "Batch update completed",
        "successful_updates": len(results),
        "failed_updates": len(errors),
        "results": results,
        "errors": errors
    }


# --------------------------------------------------
# 重要なポイント
## 1. PUT：完全置換、PATCH：部分更新
## 2. exclude_unset=True で設定されたフィールドのみ抽出
## 3. copy(update=data) でモデルの部分更新
## 4. jsonable_encoder でDB保存可能な形式に変換
## 5. 作成用と更新用でモデルを分離することを推奨
## 6. ビジネスルールや条件付き更新の実装
## 7. バッチ更新でのエラーハンドリング
## 8. 入力検証は部分更新でも実行される
# --------------------------------------------------