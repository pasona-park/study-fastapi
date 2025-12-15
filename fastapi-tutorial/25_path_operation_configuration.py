from typing import Set, Union
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

# --------------------------------------------------
# パス操作設定（Path Operation Configuration）
## パス操作デコレータに渡すことができるパラメータでAPIエンドポイントのメタデータと動作を設定
## 主な設定項目：
### 1. レスポンスステータスコード
### 2. タグ（APIドキュメントのグループ化）
### 3. 要約と説明
### 4. レスポンス説明
### 5. 非推奨マーク
## 重要：これらのパラメータはデコレータに直接渡される（関数パラメータではない）
# --------------------------------------------------

# 基本モデル定義
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None

# --------------------------------------------------
# 1. レスポンスステータスコードの設定
# --------------------------------------------------

@app.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """
    ステータスコード設定の基本例
    - status.HTTP_201_CREATED を使用（推奨）
    - 数値 201 を直接使用することも可能
    - OpenAPIスキーマに自動追加
    """
    return item

@app.put("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(item_id: int, item: Item):
    """
    更新操作での204 No Content使用例
    - 更新成功だがレスポンスボディなし
    """
    # 実際の実装では、ここでアイテムを更新
    pass

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """
    削除操作での204 No Content使用例
    """
    # 実際の実装では、ここでアイテムを削除
    pass


# --------------------------------------------------
# 2. タグを使用したAPI整理
# --------------------------------------------------

@app.post("/items/", response_model=Item, tags=["items"])
async def create_item_with_tag(item: Item):
    """
    タグ付きアイテム作成
    - tags=["items"] でアイテム関連APIとしてグループ化
    - 対話型ドキュメントでセクション別に整理される
    """
    return item

@app.get("/items/", tags=["items"])
async def read_items():
    """アイテム一覧取得（itemsタグ）"""
    return [{"name": "Foo", "price": 42}]

@app.get("/users/", tags=["users"])
async def read_users():
    """ユーザー一覧取得（usersタグ）"""
    return [{"username": "johndoe"}]

@app.post("/users/", response_model=User, tags=["users"])
async def create_user(user: User):
    """ユーザー作成（usersタグ）"""
    return user

# 複数タグの使用例
@app.get("/admin/items/", tags=["items", "admin"])
async def read_admin_items():
    """
    複数タグの使用例
    - itemsとadminの両方のタグを持つ
    - 管理者用アイテム管理API
    """
    return [{"name": "Admin Item", "price": 100, "admin_only": True}]


# --------------------------------------------------
# 3. 要約と説明の設定
# --------------------------------------------------

@app.post(
    "/items/detailed/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information: name, description, price, tax and a set of unique tags",
    tags=["items"]
)
async def create_item_detailed(item: Item):
    """
    詳細な要約と説明付きのエンドポイント
    - summary: 短い要約
    - description: 詳細な説明
    """
    return item


# --------------------------------------------------
# 4. ドキュメントストリングを使用した説明
# --------------------------------------------------

@app.post("/items/documented/", response_model=Item, summary="Create an item", tags=["items"])
async def create_item_documented(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    
    This endpoint creates a new item in the system with comprehensive validation.
    """
    return item

@app.get("/items/{item_id}", tags=["items"])
async def read_item_documented(item_id: int):
    """
    Retrieve a specific item by ID:
    
    ## Parameters
    - **item_id**: The unique identifier for the item
    
    ## Returns
    - Item object with all details
    - 404 error if item not found
    
    ## Example
    ```
    GET /items/123
    ```
    """
    return {"item_id": item_id, "name": "Sample Item", "price": 42.0}


# --------------------------------------------------
# 5. レスポンス説明の設定
# --------------------------------------------------

@app.post(
    "/items/with-response-desc/",
    response_model=Item,
    summary="Create an item",
    response_description="The created item",
    tags=["items"]
)
async def create_item_with_response_desc(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item

@app.get(
    "/users/{user_id}",
    response_model=User,
    summary="Get user by ID",
    response_description="The user information",
    tags=["users"]
)
async def get_user_with_response_desc(user_id: int):
    """
    Retrieve user information by user ID:
    
    - Returns complete user profile
    - Includes username, email, and full name
    """
    return {"username": f"user_{user_id}", "email": f"user_{user_id}@example.com"}


# --------------------------------------------------
# 6. 非推奨API（Deprecated）の設定
# --------------------------------------------------

@app.get("/items/", tags=["items"])
async def read_items_current():
    """現在の推奨されるアイテム取得API"""
    return [{"name": "Foo", "price": 42}]

@app.get("/users/", tags=["users"])
async def read_users_current():
    """現在の推奨されるユーザー取得API"""
    return [{"username": "johndoe"}]

@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    """
    非推奨のエレメント取得API
    - deprecated=True で非推奨マークを設定
    - 対話型ドキュメントで非推奨として表示
    - 段階的なAPI移行をサポート
    """
    return [{"item_id": "Foo"}]

@app.get("/old-users/", tags=["users"], deprecated=True)
async def read_old_users():
    """
    旧バージョンのユーザー取得API
    - 新しいAPIへの移行を推奨
    """
    return [{"user_id": "johndoe"}]


# --------------------------------------------------
# 7. 複合的な設定例
# --------------------------------------------------

@app.post(
    "/products/",
    response_model=Item,
    status_code=status.HTTP_201_CREATED,
    tags=["products", "items"],
    summary="Create a new product",
    response_description="The newly created product",
)
async def create_product(item: Item):
    """
    Create a new product in the catalog:
    
    ## Product Information
    - **name**: Product name (required)
    - **description**: Detailed product description
    - **price**: Product price in USD (required)
    - **tax**: Tax rate (optional, defaults to 0)
    - **tags**: Product categories and labels
    
    ## Business Rules
    - Product name must be unique
    - Price must be positive
    - Tags are used for categorization and search
    
    ## Example Request
    ```json
    {
        "name": "Laptop Computer",
        "description": "High-performance laptop",
        "price": 999.99,
        "tax": 0.08,
        "tags": ["electronics", "computers"]
    }
    ```
    """
    return item

@app.put(
    "/products/{product_id}",
    response_model=Item,
    tags=["products", "items"],
    summary="Update an existing product",
    response_description="The updated product information"
)
async def update_product(product_id: int, item: Item):
    """
    Update an existing product:
    
    - All fields are optional for updates
    - Only provided fields will be updated
    - Returns the complete updated product information
    """
    return item

@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["products", "items"],
    summary="Delete a product",
    response_description="Product successfully deleted"
)
async def delete_product(product_id: int):
    """
    Delete a product from the catalog:
    
    - Permanently removes the product
    - Cannot be undone
    - Returns no content on success
    """
    pass


# --------------------------------------------------
# 8. 管理者用API（特別なタグと設定）
# --------------------------------------------------

@app.get(
    "/admin/stats/",
    tags=["admin", "statistics"],
    summary="Get system statistics",
    response_description="System performance and usage statistics"
)
async def get_admin_stats():
    """
    Retrieve system statistics (Admin only):
    
    ## Available Metrics
    - Total users count
    - Total items count
    - API usage statistics
    - System performance metrics
    
    ## Access Requirements
    - Admin authentication required
    - Rate limited to 10 requests per minute
    """
    return {
        "total_users": 1250,
        "total_items": 5430,
        "api_calls_today": 12500,
        "system_uptime": "99.9%"
    }

@app.post(
    "/admin/maintenance/",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["admin", "maintenance"],
    summary="Start system maintenance",
    response_description="Maintenance task started"
)
async def start_maintenance():
    """
    Start system maintenance mode:
    
    - Puts system in maintenance mode
    - Returns 202 Accepted (task started)
    - Maintenance runs asynchronously
    """
    return {"message": "Maintenance mode started", "task_id": "maint_12345"}


# --------------------------------------------------
# 9. バージョン管理の例
# --------------------------------------------------

# V1 API（非推奨）
@app.get(
    "/v1/items/",
    tags=["v1", "items"],
    deprecated=True,
    summary="Get items (v1 - deprecated)"
)
async def get_items_v1():
    """
    Version 1 API for getting items (DEPRECATED):
    
    - This version is deprecated
    - Please use /v2/items/ instead
    - Will be removed in future versions
    """
    return [{"id": 1, "name": "Item 1"}]

# V2 API（現在推奨）
@app.get(
    "/v2/items/",
    tags=["v2", "items"],
    summary="Get items (v2 - current)",
    response_description="List of items with enhanced data"
)
async def get_items_v2():
    """
    Version 2 API for getting items (CURRENT):
    
    ## Improvements over v1
    - Enhanced item data structure
    - Better performance
    - Additional metadata
    - Improved error handling
    
    ## Migration Guide
    - Replace /v1/items/ with /v2/items/
    - Update client code to handle new response format
    """
    return [
        {
            "id": 1,
            "name": "Item 1",
            "created_at": "2024-01-15T10:30:00Z",
            "metadata": {"version": "2.0"}
        }
    ]


# --------------------------------------------------
# 重要なポイント
## 1. 全てのパラメータはデコレータに渡される（関数パラメータではない）
## 2. OpenAPIスキーマに自動追加される
## 3. 対話型ドキュメントUIが向上する
## 4. タグでAPIをグループ化して整理
## 5. マークダウン記法でドキュメントストリングを記述可能
## 6. deprecatedでAPIバージョン管理をサポート
## 7. summaryは短い要約、descriptionは詳細説明
## 8. response_descriptionは応答に特化した説明
# --------------------------------------------------