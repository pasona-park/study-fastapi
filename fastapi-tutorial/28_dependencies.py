from typing import Annotated, Union, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Query, Header, Cookie
from pydantic import BaseModel
import time
import asyncio
from datetime import datetime
from uuid import uuid4

app = FastAPI()

# --------------------------------------------------
# 依存性注入（Dependencies）
## コードが動作するのに必要なもの（依存性）を宣言すると、システム（FastAPI）が自動的に提供
## 主な利点：
### 1. コード再利用：共通ロジックを一度だけ記述
### 2. 関心の分離：ビジネスロジックとインフラロジックの分離
### 3. テスト容易性：依存性を簡単にモック可能
### 4. 保守性：変更が一箇所にのみ影響
## 重要：関数を直接呼び出さず、Depends()に渡す
# --------------------------------------------------

# 1. 基本的な依存性の使用
async def common_parameters(q: Union[str, None] = None, skip: int = 0, limit: int = 100):
    """
    共通パラメータ依存性
    - 複数のエンドポイントで使用される共通のクエリパラメータ
    - ページネーション、検索、フィルタリングなどに使用
    """
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    """
    アイテム一覧取得
    - common_parameters依存性を使用
    - FastAPIが自動的に依存性を解決して注入
    """
    return {
        "message": "Items retrieved",
        "parameters": commons,
        "items": [f"item_{i}" for i in range(commons["skip"], commons["skip"] + commons["limit"])]
    }

@app.get("/users/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    """
    ユーザー一覧取得
    - 同じcommon_parameters依存性を再利用
    """
    return {
        "message": "Users retrieved", 
        "parameters": commons,
        "users": [f"user_{i}" for i in range(commons["skip"], commons["skip"] + commons["limit"])]
    }


# --------------------------------------------------
# 2. Annotated型エイリアスの活用
# --------------------------------------------------

# 型エイリアスを作成してコード重複を削減
CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/products/")
async def read_products(commons: CommonsDep):
    """
    型エイリアスを使用した依存性
    - コード重複を削減
    - 型情報を保持
    - IDE自動補完をサポート
    """
    return {
        "message": "Products retrieved with type alias",
        "parameters": commons
    }

@app.get("/categories/")
async def read_categories(commons: CommonsDep):
    """型エイリアスの再利用例"""
    return {
        "message": "Categories retrieved with type alias",
        "parameters": commons
    }


# --------------------------------------------------
# 3. より複雑な依存性の例
# --------------------------------------------------

# データベース接続をシミュレートする依存性
class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected_at = datetime.now()
    
    def query(self, sql: str):
        return f"Executing: {sql} on {self.connection_string}"

async def get_database():
    """
    データベース接続依存性
    - 実際の実装ではデータベースプールから接続を取得
    - 接続管理、トランザクション処理などを担当
    """
    db = DatabaseConnection("postgresql://localhost/mydb")
    try:
        yield db
    finally:
        # 実際の実装では接続をクローズ
        print(f"Database connection closed: {db.connection_string}")

@app.get("/db-items/")
async def get_items_from_db(
    commons: CommonsDep,
    db: Annotated[DatabaseConnection, Depends(get_database)]
):
    """
    データベース依存性を使用したエンドポイント
    - 複数の依存性を組み合わせ
    - データベース操作の実行
    """
    query = f"SELECT * FROM items LIMIT {commons['limit']} OFFSET {commons['skip']}"
    if commons['q']:
        query += f" WHERE name LIKE '%{commons['q']}%'"
    
    result = db.query(query)
    
    return {
        "message": "Items from database",
        "query": result,
        "connected_at": db.connected_at,
        "parameters": commons
    }


# --------------------------------------------------
# 4. 認証・認可の依存性
# --------------------------------------------------

# 偽のユーザーデータベース
fake_users_db = {
    "alice": {"username": "alice", "email": "alice@example.com", "role": "admin"},
    "bob": {"username": "bob", "email": "bob@example.com", "role": "user"},
    "charlie": {"username": "charlie", "email": "charlie@example.com", "role": "user"}
}

class User(BaseModel):
    username: str
    email: str
    role: str

async def get_current_user(token: Annotated[str, Query()]) -> User:
    """
    現在のユーザーを取得する依存性
    - 実際の実装ではJWTトークンの検証を行う
    - 認証失敗時は例外を発生
    """
    # 簡単なトークン検証（実際の実装ではJWT等を使用）
    if token not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    user_data = fake_users_db[token]
    return User(**user_data)

async def get_admin_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    管理者ユーザーを取得する依存性
    - get_current_user依存性に依存（階層的依存性）
    - 管理者権限チェック
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@app.get("/profile/")
async def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
    """
    ユーザープロフィール取得
    - 認証が必要なエンドポイント
    """
    return {
        "message": "User profile",
        "user": current_user
    }

@app.get("/admin/users/")
async def get_all_users(admin_user: Annotated[User, Depends(get_admin_user)]):
    """
    全ユーザー取得（管理者のみ）
    - 階層的依存性の例
    - get_current_user → get_admin_user の順で実行
    """
    return {
        "message": "All users (admin only)",
        "admin": admin_user.username,
        "users": list(fake_users_db.values())
    }


# --------------------------------------------------
# 5. パフォーマンス監視の依存性
# --------------------------------------------------

class RequestTimer:
    def __init__(self):
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        return time.time() - self.start_time

async def get_request_timer():
    """
    リクエスト処理時間を測定する依存性
    - パフォーマンス監視に使用
    - ログ記録、メトリクス収集などに活用
    """
    timer = RequestTimer()
    try:
        yield timer
    finally:
        elapsed = timer.get_elapsed_time()
        print(f"Request completed in {elapsed:.4f} seconds")

@app.get("/timed-operation/")
async def timed_operation(
    timer: Annotated[RequestTimer, Depends(get_request_timer)],
    commons: CommonsDep
):
    """
    処理時間を測定するエンドポイント
    - パフォーマンス監視依存性を使用
    """
    # 何らかの処理をシミュレート
    import asyncio
    await asyncio.sleep(0.1)
    
    return {
        "message": "Timed operation completed",
        "elapsed_time": timer.get_elapsed_time(),
        "parameters": commons
    }


# --------------------------------------------------
# 6. 設定管理の依存性
# --------------------------------------------------

class Settings(BaseModel):
    app_name: str = "FastAPI Dependencies Demo"
    debug: bool = False
    max_items_per_page: int = 100
    database_url: str = "sqlite:///./test.db"

# シングルトンパターンで設定を管理
_settings_instance = None

async def get_settings() -> Settings:
    """
    アプリケーション設定を取得する依存性
    - シングルトンパターンで実装
    - 環境変数、設定ファイルから読み込み
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

@app.get("/config/")
async def get_config(settings: Annotated[Settings, Depends(get_settings)]):
    """
    アプリケーション設定取得
    - 設定管理依存性を使用
    """
    return {
        "message": "Application configuration",
        "settings": settings
    }

@app.get("/items-with-config/")
async def get_items_with_config(
    commons: CommonsDep,
    settings: Annotated[Settings, Depends(get_settings)]
):
    """
    設定を考慮したアイテム取得
    - 設定値を使用してビジネスロジックを制御
    """
    # 設定値を使用してlimitを制限
    actual_limit = min(commons["limit"], settings.max_items_per_page)
    
    return {
        "message": "Items with configuration",
        "requested_limit": commons["limit"],
        "actual_limit": actual_limit,
        "max_allowed": settings.max_items_per_page,
        "debug_mode": settings.debug
    }


# --------------------------------------------------
# 7. 外部サービス連携の依存性
# --------------------------------------------------

class ExternalAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
    
    async def fetch_data(self, endpoint: str):
        # 実際の実装ではhttpxやaiohttpを使用
        return f"Data from {self.base_url}/{endpoint} with key {self.api_key[:8]}..."

async def get_external_api_client():
    """
    外部API クライアント依存性
    - 外部サービスとの連携
    - API キー管理、レート制限などを処理
    """
    client = ExternalAPIClient(
        base_url="https://api.external-service.com",
        api_key="secret-api-key-12345"
    )
    try:
        yield client
    finally:
        # 実際の実装では接続をクローズ
        print("External API client closed")

@app.get("/external-data/")
async def get_external_data(
    api_client: Annotated[ExternalAPIClient, Depends(get_external_api_client)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    外部データ取得
    - 外部API依存性と認証依存性を組み合わせ
    """
    data = await api_client.fetch_data("user-data")
    
    return {
        "message": "External data retrieved",
        "user": current_user.username,
        "data": data
    }



# --------------------------------------------------
# 8. キャッシュ依存性
# --------------------------------------------------

class CacheService:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str):
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 300):
        # 実際の実装ではTTLを考慮
        self._cache[key] = value
        return value
    
    def delete(self, key: str):
        return self._cache.pop(key, None)

# グローバルキャッシュインスタンス
_cache_instance = None

async def get_cache_service() -> CacheService:
    """
    キャッシュサービス依存性
    - データキャッシング機能を提供
    - Redis、Memcachedなどの実装も可能
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance

@app.get("/cached-items/{item_id}")
async def get_cached_item(
    item_id: str,
    cache: Annotated[CacheService, Depends(get_cache_service)]
):
    """
    キャッシュ機能付きアイテム取得
    - キャッシュ依存性を使用
    """
    cache_key = f"item:{item_id}"
    
    # キャッシュから取得を試行
    cached_item = cache.get(cache_key)
    if cached_item:
        return {
            "message": "Item from cache",
            "item": cached_item,
            "cache_hit": True
        }
    
    # キャッシュにない場合は新しく作成
    new_item = {
        "id": item_id,
        "name": f"Item {item_id}",
        "created_at": datetime.now().isoformat()
    }
    
    # キャッシュに保存
    cache.set(cache_key, new_item)
    
    return {
        "message": "Item created and cached",
        "item": new_item,
        "cache_hit": False
    }


# --------------------------------------------------
# 9. 複数依存性の組み合わせ例
# --------------------------------------------------

@app.get("/complex-endpoint/")
async def complex_endpoint(
    commons: CommonsDep,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[DatabaseConnection, Depends(get_database)],
    settings: Annotated[Settings, Depends(get_settings)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
    timer: Annotated[RequestTimer, Depends(get_request_timer)]
):
    """
    複数の依存性を組み合わせた複雑なエンドポイント
    - 認証、データベース、設定、キャッシュ、パフォーマンス監視
    - 実際のアプリケーションでよく見られるパターン
    """
    cache_key = f"user_data:{current_user.username}"
    
    # キャッシュチェック
    cached_data = cache.get(cache_key)
    if cached_data:
        return {
            "message": "Complex operation (cached)",
            "user": current_user.username,
            "data": cached_data,
            "elapsed_time": timer.get_elapsed_time(),
            "from_cache": True
        }
    
    # データベースクエリ
    query = f"SELECT * FROM user_items WHERE user_id = '{current_user.username}' LIMIT {commons['limit']}"
    db_result = db.query(query)
    
    # 結果を作成
    result_data = {
        "db_query": db_result,
        "parameters": commons,
        "app_name": settings.app_name,
        "debug": settings.debug
    }
    
    # キャッシュに保存
    cache.set(cache_key, result_data)
    
    return {
        "message": "Complex operation completed",
        "user": current_user.username,
        "data": result_data,
        "elapsed_time": timer.get_elapsed_time(),
        "from_cache": False
    }


# --------------------------------------------------
# 10. 依存性としてのクラス（Classes as Dependencies）
# --------------------------------------------------

# 偽のアイテムデータベース
fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
    {"item_name": "Qux"},
    {"item_name": "Quux"}
]

class CommonQueryParams:
    """
    共通クエリパラメータクラス
    - 関数の代わりにクラスを依存性として使用
    - より良い型ヒントとIDE支援を提供
    - 属性アクセスによる明確なデータ構造
    """
    def __init__(self, q: Union[str, None] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/class-items/")
async def read_items_with_class(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    """
    クラス依存性を使用したアイテム取得
    - CommonQueryParamsクラスのインスタンスを受け取る
    - 属性アクセス（commons.q, commons.skip等）が可能
    - IDEの自動補完とタイプチェックをサポート
    """
    response = {}
    
    if commons.q:
        response.update({"q": commons.q})
    
    # スライシングでページネーション実装
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    
    return {
        "message": "Items retrieved using class dependency",
        "query_params": {
            "q": commons.q,
            "skip": commons.skip,
            "limit": commons.limit
        },
        "result": response
    }

# クラス依存性の短縮記法
@app.get("/class-items-short/")
async def read_items_with_class_short(commons: Annotated[CommonQueryParams, Depends()]):
    """
    クラス依存性の短縮記法
    - Depends()の中にクラス名を書かなくても良い
    - 型アノテーションからFastAPIが自動的に推論
    - コード重複を削減
    """
    response = {}
    
    if commons.q:
        response.update({"q": commons.q})
    
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    
    return {
        "message": "Items retrieved using short class dependency syntax",
        "query_params": {
            "q": commons.q,
            "skip": commons.skip,
            "limit": commons.limit
        },
        "result": response
    }


# --------------------------------------------------
# 11. より複雑なクラス依存性の例
# --------------------------------------------------

class DatabaseConfig:
    """
    データベース設定クラス
    - 設定値の管理とバリデーション
    - 複雑な初期化ロジックを含む
    """
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 5432, 
                 database: str = "myapp",
                 max_connections: int = 10):
        self.host = host
        self.port = port
        self.database = database
        self.max_connections = max_connections
        
        # 接続文字列を自動生成
        self.connection_string = f"postgresql://{host}:{port}/{database}"
        
        # バリデーション
        if port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        if max_connections < 1:
            raise ValueError("Max connections must be at least 1")

class SearchParams:
    """
    検索パラメータクラス
    - 複雑な検索条件を管理
    - バリデーションとデータ変換を含む
    """
    def __init__(self,
                 query: Union[str, None] = None,
                 category: Union[str, None] = None,
                 min_price: Union[float, None] = None,
                 max_price: Union[float, None] = None,
                 sort_by: str = "name",
                 sort_order: str = "asc"):
        self.query = query
        self.category = category
        self.min_price = min_price
        self.max_price = max_price
        self.sort_by = sort_by
        self.sort_order = sort_order
        
        # バリデーション
        if sort_by not in ["name", "price", "created_at"]:
            raise ValueError("sort_by must be one of: name, price, created_at")
        if sort_order not in ["asc", "desc"]:
            raise ValueError("sort_order must be asc or desc")
        if min_price is not None and min_price < 0:
            raise ValueError("min_price must be non-negative")
        if max_price is not None and max_price < 0:
            raise ValueError("max_price must be non-negative")
        if (min_price is not None and max_price is not None and 
            min_price > max_price):
            raise ValueError("min_price must be less than or equal to max_price")

@app.get("/advanced-search/")
async def advanced_search(
    search: Annotated[SearchParams, Depends()],
    pagination: Annotated[CommonQueryParams, Depends()],
    db_config: Annotated[DatabaseConfig, Depends()]
):
    """
    高度な検索エンドポイント
    - 複数のクラス依存性を組み合わせ
    - 各クラスが独自のバリデーションロジックを持つ
    - 複雑なビジネスロジックを構造化
    """
    # 検索条件の構築
    search_conditions = []
    if search.query:
        search_conditions.append(f"name LIKE '%{search.query}%'")
    if search.category:
        search_conditions.append(f"category = '{search.category}'")
    if search.min_price is not None:
        search_conditions.append(f"price >= {search.min_price}")
    if search.max_price is not None:
        search_conditions.append(f"price <= {search.max_price}")
    
    where_clause = " AND ".join(search_conditions) if search_conditions else "1=1"
    
    # SQLクエリの構築
    sql_query = f"""
    SELECT * FROM items 
    WHERE {where_clause}
    ORDER BY {search.sort_by} {search.sort_order.upper()}
    LIMIT {pagination.limit} OFFSET {pagination.skip}
    """
    
    return {
        "message": "Advanced search completed",
        "database": {
            "connection_string": db_config.connection_string,
            "max_connections": db_config.max_connections
        },
        "search_params": {
            "query": search.query,
            "category": search.category,
            "price_range": [search.min_price, search.max_price],
            "sort": f"{search.sort_by} {search.sort_order}"
        },
        "pagination": {
            "skip": pagination.skip,
            "limit": pagination.limit
        },
        "generated_sql": sql_query.strip()
    }


# --------------------------------------------------
# 12. 継承を使用したクラス依存性
# --------------------------------------------------

class BaseQueryParams:
    """
    基底クエリパラメータクラス
    - 共通の機能を提供
    - 継承による機能拡張をサポート
    """
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit
        
        # バリデーション
        if skip < 0:
            raise ValueError("skip must be non-negative")
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
    
    def get_offset_limit(self):
        """オフセットとリミットのタプルを返す"""
        return (self.skip, self.limit)

class SearchQueryParams(BaseQueryParams):
    """
    検索用クエリパラメータクラス
    - BaseQueryParamsを継承
    - 検索固有の機能を追加
    """
    def __init__(self, q: Union[str, None] = None, skip: int = 0, limit: int = 100):
        super().__init__(skip, limit)
        self.q = q
    
    def has_search_query(self):
        """検索クエリが存在するかチェック"""
        return self.q is not None and len(self.q.strip()) > 0

class FilterQueryParams(BaseQueryParams):
    """
    フィルタ用クエリパラメータクラス
    - BaseQueryParamsを継承
    - フィルタ固有の機能を追加
    """
    def __init__(self, 
                 category: Union[str, None] = None,
                 status: str = "active",
                 skip: int = 0, 
                 limit: int = 100):
        super().__init__(skip, limit)
        self.category = category
        self.status = status
        
        # ステータスのバリデーション
        if status not in ["active", "inactive", "all"]:
            raise ValueError("status must be one of: active, inactive, all")
    
    def get_filters(self):
        """アクティブなフィルタの辞書を返す"""
        filters = {}
        if self.category:
            filters["category"] = self.category
        if self.status != "all":
            filters["status"] = self.status
        return filters

@app.get("/search-items/")
async def search_items(params: Annotated[SearchQueryParams, Depends()]):
    """
    継承クラス依存性を使用した検索
    - SearchQueryParamsクラスを使用
    - 継承による機能拡張の例
    """
    offset, limit = params.get_offset_limit()
    
    return {
        "message": "Search with inheritance-based dependency",
        "has_search": params.has_search_query(),
        "query": params.q,
        "pagination": {"offset": offset, "limit": limit},
        "items": fake_items_db[offset:offset + limit] if not params.has_search_query() 
                else [item for item in fake_items_db if params.q.lower() in item["item_name"].lower()]
    }

@app.get("/filter-items/")
async def filter_items(params: Annotated[FilterQueryParams, Depends()]):
    """
    継承クラス依存性を使用したフィルタリング
    - FilterQueryParamsクラスを使用
    """
    offset, limit = params.get_offset_limit()
    filters = params.get_filters()
    
    return {
        "message": "Filter with inheritance-based dependency",
        "active_filters": filters,
        "pagination": {"offset": offset, "limit": limit},
        "category": params.category,
        "status": params.status,
        "items": fake_items_db[offset:offset + limit]
    }


# --------------------------------------------------
# 13. クラス依存性と関数依存性の比較
# --------------------------------------------------

# 関数ベースの依存性（従来の方法）
async def function_based_params(q: Union[str, None] = None, skip: int = 0, limit: int = 100):
    """関数ベースの依存性"""
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/function-vs-class/function")
async def function_based_endpoint(params: Annotated[dict, Depends(function_based_params)]):
    """
    関数ベース依存性の例
    - 辞書を返すため、IDEサポートが限定的
    - キーの存在をランタイムで確認する必要
    """
    return {
        "message": "Function-based dependency",
        "type": "dict",
        "params": params,
        "q_exists": "q" in params,
        "ide_support": "limited"
    }

@app.get("/function-vs-class/class")
async def class_based_endpoint(params: Annotated[CommonQueryParams, Depends()]):
    """
    クラスベース依存性の例
    - 属性アクセスによる明確なインターフェース
    - IDEの完全なサポート（自動補完、型チェック）
    - より良いコード可読性
    """
    return {
        "message": "Class-based dependency",
        "type": "CommonQueryParams",
        "params": {
            "q": params.q,
            "skip": params.skip,
            "limit": params.limit
        },
        "q_exists": params.q is not None,
        "ide_support": "full"
    }


# --------------------------------------------------
# 14. サブ依存性（Sub-dependencies）
# --------------------------------------------------

from fastapi import Cookie

def query_extractor(q: Union[str, None] = None):
    """
    第一レベルの依存性
    - 基本的なクエリパラメータを抽出
    - 他の依存性の基盤となる
    """
    return q

def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],  # サブ依存性
    last_query: Annotated[Union[str, None], Cookie()] = None,
):
    """
    第二レベルの依存性
    - query_extractorに依存（サブ依存性を持つ）
    - クエリがない場合はクッキーから取得
    - 依存性でありながら同時に依存者でもある
    """
    if not q:
        return last_query
    return q

@app.get("/sub-dependency-example/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)],
):
    """
    サブ依存性を使用するエンドポイント
    - query_or_cookie_extractorのみを宣言
    - FastAPIが自動的にquery_extractorも解決
    - 実行順序：query_extractor → query_or_cookie_extractor → read_query
    """
    return {"q_or_cookie": query_or_default}


# --------------------------------------------------
# 15. より複雑なサブ依存性の例
# --------------------------------------------------

# レベル1：基本認証
def get_token_from_header(authorization: Union[str, None] = None) -> Union[str, None]:
    """
    認証トークンを抽出する基本依存性
    - HTTPヘッダーからトークンを取得
    - 最下位レベルの依存性
    """
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]  # "Bearer " を除去
    return None

# レベル2：トークン検証
def verify_token(token: Annotated[Union[str, None], Depends(get_token_from_header)]) -> Union[dict, None]:
    """
    トークンを検証する依存性
    - get_token_from_headerに依存
    - トークンの有効性をチェック
    """
    if not token:
        return None
    
    # 簡単なトークン検証（実際の実装ではJWT等を使用）
    if token == "valid-token-123":
        return {"user_id": 1, "username": "testuser", "role": "user"}
    elif token == "admin-token-456":
        return {"user_id": 2, "username": "admin", "role": "admin"}
    
    return None

# レベル3：現在のユーザー取得
def get_current_user(user_data: Annotated[Union[dict, None], Depends(verify_token)]) -> User:
    """
    現在のユーザーを取得する依存性
    - verify_tokenに依存
    - 認証されたユーザー情報を返す
    """
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )
    
    return User(
        username=user_data["username"],
        email=f"{user_data['username']}@example.com",
        role=user_data["role"]
    )

# レベル4：管理者権限チェック
def get_admin_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    管理者権限をチェックする依存性
    - get_current_userに依存
    - 4レベルの依存性チェーン
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@app.get("/protected-resource/")
async def get_protected_resource(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    保護されたリソースへのアクセス
    - 3レベルの依存性チェーン
    - get_token_from_header → verify_token → get_current_user
    """
    return {
        "message": "Protected resource accessed",
        "user": current_user.username,
        "role": current_user.role
    }

@app.get("/admin-only/")
async def admin_only_resource(
    admin_user: Annotated[User, Depends(get_admin_user)]
):
    """
    管理者専用リソース
    - 4レベルの依存性チェーン
    - get_token_from_header → verify_token → get_current_user → get_admin_user
    """
    return {
        "message": "Admin-only resource accessed",
        "admin": admin_user.username
    }


# --------------------------------------------------
# 16. 依存性キャッシングの例
# --------------------------------------------------

# カウンターで依存性の実行回数を追跡
execution_counter = {"count": 0}

def expensive_operation() -> dict:
    """
    重い処理をシミュレートする依存性
    - 実行回数をカウント
    - 同じリクエスト内では1回のみ実行される（キャッシュ）
    """
    execution_counter["count"] += 1
    print(f"Expensive operation executed {execution_counter['count']} times")
    
    # 重い処理をシミュレート
    import time
    time.sleep(0.1)
    
    return {
        "result": "expensive_data",
        "execution_count": execution_counter["count"]
    }

def dependency_a(expensive_data: Annotated[dict, Depends(expensive_operation)]) -> str:
    """expensive_operationに依存する依存性A"""
    return f"A: {expensive_data['result']}"

def dependency_b(expensive_data: Annotated[dict, Depends(expensive_operation)]) -> str:
    """expensive_operationに依存する依存性B"""
    return f"B: {expensive_data['result']}"

@app.get("/cached-dependencies/")
async def cached_dependencies_example(
    result_a: Annotated[str, Depends(dependency_a)],
    result_b: Annotated[str, Depends(dependency_b)],
    direct_expensive: Annotated[dict, Depends(expensive_operation)]
):
    """
    依存性キャッシングのデモ
    - expensive_operationは3回参照されるが、1回のみ実行
    - FastAPIが自動的にキャッシュして結果を再利用
    """
    return {
        "message": "Cached dependencies example",
        "result_a": result_a,
        "result_b": result_b,
        "direct_result": direct_expensive,
        "total_executions": execution_counter["count"]
    }

# キャッシュを無効化する例
def non_cached_operation() -> dict:
    """キャッシュされない依存性"""
    execution_counter["count"] += 1
    return {"result": "non_cached_data", "execution_count": execution_counter["count"]}

@app.get("/non-cached-dependencies/")
async def non_cached_dependencies_example(
    cached_result: Annotated[dict, Depends(expensive_operation)],
    non_cached_1: Annotated[dict, Depends(non_cached_operation, use_cache=False)],
    non_cached_2: Annotated[dict, Depends(non_cached_operation, use_cache=False)]
):
    """
    キャッシュ無効化のデモ
    - expensive_operationはキャッシュされる
    - non_cached_operationはuse_cache=Falseで毎回実行
    """
    return {
        "message": "Non-cached dependencies example",
        "cached_result": cached_result,
        "non_cached_1": non_cached_1,
        "non_cached_2": non_cached_2
    }


# --------------------------------------------------
# 17. 実戦的なサブ依存性の例：データベースとログ
# --------------------------------------------------

# レベル1：データベース接続
def get_db_connection() -> DatabaseConnection:
    """
    データベース接続を取得
    - 最下位レベルの依存性
    - 接続プールから接続を取得
    """
    return DatabaseConnection("postgresql://localhost/myapp")

# レベル2：トランザクション開始
def get_db_transaction(
    db: Annotated[DatabaseConnection, Depends(get_db_connection)]
) -> dict:
    """
    データベーストランザクションを開始
    - データベース接続に依存
    - トランザクション管理
    """
    transaction_id = f"tx_{id(db)}_{time.time()}"
    return {
        "db": db,
        "transaction_id": transaction_id,
        "started_at": datetime.now()
    }

# レベル3：ログ設定
def get_request_logger(
    current_user: Annotated[User, Depends(get_current_user)],
    db_tx: Annotated[dict, Depends(get_db_transaction)]
) -> dict:
    """
    リクエスト専用ログ設定
    - ユーザー情報とトランザクション情報に依存
    - 構造化ログ設定
    """
    return {
        "user_id": current_user.username,
        "transaction_id": db_tx["transaction_id"],
        "request_id": f"req_{uuid4()}",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/complex-operation/")
async def complex_operation(
    logger: Annotated[dict, Depends(get_request_logger)],
    db_tx: Annotated[dict, Depends(get_db_transaction)]
):
    """
    複雑な操作のエンドポイント
    - 多層の依存性を組み合わせ
    - 認証、データベース、ログが全て連携
    """
    # 実際の実装では、ここでビジネスロジックを実行
    operation_result = {
        "operation": "complex_business_logic",
        "status": "completed",
        "processed_at": datetime.now().isoformat()
    }
    
    return {
        "message": "Complex operation completed",
        "logger_info": logger,
        "transaction_info": {
            "id": db_tx["transaction_id"],
            "started_at": db_tx["started_at"].isoformat()
        },
        "result": operation_result
    }


# --------------------------------------------------
# 重要なポイント
## 1. 依存性は通常の関数として定義（デコレータ不要）
## 2. Depends()に関数を渡す（直接呼び出さない）
## 3. FastAPIが自動的に依存性を解決して注入
## 4. 階層的依存性：依存性が他の依存性に依存可能
## 5. async/sync混在可能
## 6. 型エイリアスでコード重複を削減
## 7. OpenAPIスキーマに自動統合
## 8. テスト時に依存性を簡単にモック可能
## 9. クラス依存性：より良い型ヒントとIDE支援
## 10. 短縮記法：Depends()で型から自動推論
## 11. 継承：クラス依存性での機能拡張
## 12. "呼び出し可能"なものは全て依存性として使用可能
## 13. サブ依存性：任意の深さまでネスト可能
## 14. 自動キャッシング：同じリクエスト内で依存性結果を再利用
## 15. use_cache=False：キャッシュを無効化して毎回実行
## 16. 依存性ツリー：FastAPIが自動的に解決順序を決定
# --------------------------------------------------

# --------------------------------------------------
# 18. パス操作デコレータでの依存性
# --------------------------------------------------

async def verify_token(x_token: Annotated[str, Header()]):
    """
    トークン検証依存性
    - 戻り値は使用されない
    - 検証のみを目的とする
    - 無効な場合は例外を発生
    """
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

async def verify_key(x_key: Annotated[str, Header()]):
    """
    キー検証依存性
    - 値を返すが、デコレータレベルでは使用されない
    - 通常の依存性としても再利用可能
    """
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

@app.get("/decorator-items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    """
    デコレータレベル依存性の例
    - verify_tokenとverify_keyが自動実行
    - 戻り値は関数パラメータに渡されない
    - 検証失敗時は自動的に例外発生
    - 関数パラメータがクリーンに保たれる
    """
    return [{"item": "Foo"}, {"item": "Bar"}]

# 通常の依存性との比較
@app.get("/decorator-items-with-params/")
async def read_items_with_params(
    x_token: Annotated[str, Header()],
    x_key: Annotated[str, Depends(verify_key)]
):
    """
    通常の依存性パラメータとの比較
    - パラメータとして値を受け取る
    - 関数内で値を使用可能
    - パラメータリストが長くなる
    """
    return {
        "items": [{"item": "Foo"}, {"item": "Bar"}],
        "token_received": bool(x_token),
        "key_received": x_key
    }

# 複数の検証依存性
async def verify_user_agent(user_agent: Annotated[str, Header()]):
    """ユーザーエージェント検証"""
    if "bot" in user_agent.lower():
        raise HTTPException(status_code=403, detail="Bots not allowed")

async def verify_content_type(content_type: Annotated[str, Header()] = "application/json"):
    """コンテンツタイプ検証"""
    if content_type != "application/json":
        raise HTTPException(status_code=415, detail="Only JSON content type allowed")

@app.post("/secure-endpoint/", dependencies=[
    Depends(verify_token),
    Depends(verify_key), 
    Depends(verify_user_agent),
    Depends(verify_content_type)
])
async def secure_endpoint(data: dict):
    """
    複数の検証依存性を持つエンドポイント
    - 4つの検証が自動実行
    - すべて通過した場合のみ関数実行
    - 関数パラメータは実際のデータのみ
    """
    return {"message": "Secure operation completed", "data": data}


# --------------------------------------------------
# 重要なポイント（更新版）
## 17. デコレータレベル依存性：戻り値不要、検証のみの場合に使用
## 18. dependencies=[Depends(func)]：パラメータリストをクリーンに保つ
## 19. 同じ依存性関数を異なる方法で使用可能（パラメータ/デコレータ）
## 20. 複数の検証依存性を組み合わせて強固なセキュリティ実現
# --------------------------------------------------

# --------------------------------------------------
# 19. グローバル依存性（Global Dependencies）
# --------------------------------------------------

# グローバル認証依存性
async def global_verify_token(x_token: Annotated[str, Header()]):
    """
    グローバルトークン検証依存性
    - すべてのエンドポイントで自動実行
    - アプリケーション全体のセキュリティを保証
    - 認証が不要なエンドポイントは別途作成が必要
    """
    if x_token != "global-secret-token":
        raise HTTPException(status_code=401, detail="Global authentication failed")

async def global_verify_key(x_key: Annotated[str, Header()]):
    """
    グローバルキー検証依存性
    - APIキーによる追加認証
    - レート制限やアクセス制御に使用
    """
    if x_key != "global-api-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_key

# グローバル依存性を持つ新しいアプリケーションインスタンス
global_app = FastAPI(
    title="Global Dependencies Example",
    dependencies=[Depends(global_verify_token), Depends(global_verify_key)]
)

@global_app.get("/public-items/")
async def get_public_items():
    """
    パブリックアイテム取得
    - グローバル依存性が自動適用
    - 関数パラメータには現れないが検証は実行される
    - すべてのリクエストでトークンとキー検証が必要
    """
    return {
        "message": "Public items with global authentication",
        "items": ["item1", "item2", "item3"],
        "note": "This endpoint requires global token and key"
    }

@global_app.get("/public-users/")
async def get_public_users():
    """
    パブリックユーザー取得
    - 同じグローバル依存性が適用
    - 個別の認証コードが不要
    """
    return {
        "message": "Public users with global authentication", 
        "users": ["user1", "user2", "user3"],
        "note": "Global dependencies automatically applied"
    }

# グローバル依存性と個別依存性の組み合わせ
async def additional_verification(user_agent: Annotated[str, Header()]):
    """追加検証依存性"""
    if "bot" in user_agent.lower():
        raise HTTPException(status_code=403, detail="Bots not allowed")

@global_app.get("/secure-data/", dependencies=[Depends(additional_verification)])
async def get_secure_data():
    """
    セキュアデータ取得
    - グローバル依存性（トークン + キー検証）
    - 個別依存性（ユーザーエージェント検証）
    - 両方が実行される
    """
    return {
        "message": "Secure data access",
        "data": "highly_sensitive_information",
        "security_layers": ["global_token", "global_key", "user_agent_check"]
    }

# グローバル依存性と通常の依存性パラメータの組み合わせ
@global_app.get("/user-specific-data/")
async def get_user_specific_data(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    ユーザー固有データ取得
    - グローバル依存性（自動実行）
    - パラメータ依存性（ユーザー情報取得）
    - 多層セキュリティの実現
    """
    return {
        "message": "User specific data",
        "user": current_user.username,
        "data": f"private_data_for_{current_user.username}",
        "security_note": "Protected by global + user-specific authentication"
    }


# --------------------------------------------------
# 20. グローバル依存性の実践的な例
# --------------------------------------------------

# リクエスト追跡用のグローバル依存性
class RequestTracker:
    def __init__(self):
        self.request_id = str(uuid4())
        self.start_time = time.time()
        self.metadata = {}
    
    def add_metadata(self, key: str, value: Any):
        self.metadata[key] = value
    
    def get_duration(self):
        return time.time() - self.start_time

async def global_request_tracker():
    """
    グローバルリクエスト追跡依存性
    - すべてのリクエストを追跡
    - パフォーマンス監視
    - ログ記録とデバッグ支援
    """
    tracker = RequestTracker()
    try:
        yield tracker
    finally:
        duration = tracker.get_duration()
        print(f"Request {tracker.request_id} completed in {duration:.4f}s")
        print(f"Metadata: {tracker.metadata}")

# レート制限用のグローバル依存性
request_counts = {}

async def global_rate_limiter(request: str = Header(alias="x-forwarded-for", default="unknown")):
    """
    グローバルレート制限依存性
    - IPアドレスベースの制限
    - DDoS攻撃防止
    - API使用量制御
    """
    client_ip = request
    current_time = time.time()
    
    # 簡単なレート制限実装（実際にはRedisなどを使用）
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # 過去1分間のリクエスト数をチェック
    recent_requests = [t for t in request_counts[client_ip] if current_time - t < 60]
    request_counts[client_ip] = recent_requests
    
    if len(recent_requests) >= 10:  # 1分間に10リクエストまで
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Max 10 requests per minute."
        )
    
    request_counts[client_ip].append(current_time)

# 包括的なグローバル依存性を持つアプリケーション
comprehensive_app = FastAPI(
    title="Comprehensive Global Dependencies",
    dependencies=[
        Depends(global_verify_token),
        Depends(global_rate_limiter),
        Depends(global_request_tracker)
    ]
)

@comprehensive_app.get("/protected-resource/")
async def get_protected_resource(
    tracker: Annotated[RequestTracker, Depends(global_request_tracker)]
):
    """
    保護されたリソース
    - 複数のグローバル依存性が適用
    - 認証、レート制限、追跡が自動実行
    """
    tracker.add_metadata("endpoint", "protected-resource")
    tracker.add_metadata("action", "resource_access")
    
    return {
        "message": "Protected resource accessed successfully",
        "request_id": tracker.request_id,
        "timestamp": datetime.now().isoformat(),
        "security_layers": ["authentication", "rate_limiting", "request_tracking"]
    }

@comprehensive_app.post("/protected-action/")
async def perform_protected_action(
    data: dict,
    tracker: Annotated[RequestTracker, Depends(global_request_tracker)]
):
    """
    保護されたアクション実行
    - POST操作でもグローバル依存性適用
    - データ操作の完全な追跡
    """
    tracker.add_metadata("endpoint", "protected-action")
    tracker.add_metadata("data_keys", list(data.keys()))
    
    return {
        "message": "Protected action completed",
        "request_id": tracker.request_id,
        "processed_data": data,
        "status": "success"
    }


# --------------------------------------------------
# 21. グローバル依存性の除外パターン
# --------------------------------------------------

# 認証不要なエンドポイント用の別アプリケーション
public_app = FastAPI(title="Public API")

@public_app.get("/health/")
async def health_check():
    """
    ヘルスチェックエンドポイント
    - 認証不要
    - 監視システム用
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@public_app.get("/public-info/")
async def get_public_info():
    """
    パブリック情報取得
    - 認証不要
    - 一般公開データ
    """
    return {
        "message": "Public information",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# メインアプリケーションにパブリックアプリをマウント
app.mount("/public", public_app)
app.mount("/global", global_app)
app.mount("/comprehensive", comprehensive_app)


# --------------------------------------------------
# 重要なポイント（最終更新版）
## 19. グローバル依存性：FastAPI(dependencies=[...])でアプリ全体に適用
## 20. 実行順序：グローバル → デコレータ → パラメータ → 関数
## 21. 組み合わせ：グローバル + 個別依存性の同時使用可能
## 22. 除外パターン：認証不要エンドポイントは別アプリで分離
## 23. 実践的活用：認証、レート制限、ログ、監視の統合
## 24. パフォーマンス考慮：軽量な処理のみグローバルに設定
## 25. セキュリティ強化：すべてのAPIに一貫したセキュリティ適用
# --------------------------------------------------
# --------------------------------------------------
# 22. yieldを使用する依存性（Dependencies with yield）
# --------------------------------------------------

# 基本的なyield依存性の例
class DatabaseSession:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.is_connected = False
        self.transaction_count = 0
    
    def connect(self):
        """データベース接続をシミュレート"""
        self.is_connected = True
        print(f"Database connected: {self.connection_string}")
    
    def close(self):
        """データベース接続を閉じる"""
        self.is_connected = False
        print(f"Database connection closed: {self.connection_string}")
    
    def execute(self, query: str):
        """クエリ実行をシミュレート"""
        if not self.is_connected:
            raise Exception("Database not connected")
        self.transaction_count += 1
        return f"Executed: {query} (Transaction #{self.transaction_count})"

async def get_database_session():
    """
    データベースセッション依存性（yield使用）
    - yield前：リソース初期化（接続作成）
    - yield：値を注入
    - yield後：リソース清理（接続終了）
    """
    # リソース初期化（レスポンス生成前に実行）
    db_session = DatabaseSession("postgresql://localhost:5432/myapp")
    db_session.connect()
    
    try:
        # 値を注入（パス操作や他の依存性で使用）
        yield db_session
    finally:
        # リソース清理（レスポンス生成後に実行）
        db_session.close()

@app.get("/database-operation/")
async def database_operation(
    db: Annotated[DatabaseSession, Depends(get_database_session)]
):
    """
    データベース操作エンドポイント
    - yield依存性を使用してリソース管理
    - 自動的に接続作成と終了が処理される
    """
    result1 = db.execute("SELECT * FROM users")
    result2 = db.execute("SELECT * FROM products")
    
    return {
        "message": "Database operations completed",
        "connection": db.connection_string,
        "results": [result1, result2],
        "transaction_count": db.transaction_count
    }


# --------------------------------------------------
# 23. 例外処理を含むyield依存性
# --------------------------------------------------

class FileManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.file_handle = None
        self.operations = []
    
    def open(self):
        """ファイルを開く（シミュレート）"""
        print(f"Opening file: {self.filename}")
        self.file_handle = f"handle_for_{self.filename}"
        return self
    
    def write(self, content: str):
        """ファイルに書き込み（シミュレート）"""
        if not self.file_handle:
            raise Exception("File not opened")
        self.operations.append(f"WRITE: {content}")
        return f"Written to {self.filename}: {content}"
    
    def close(self):
        """ファイルを閉じる"""
        if self.file_handle:
            print(f"Closing file: {self.filename}")
            self.file_handle = None

async def get_file_manager():
    """
    ファイル管理依存性（例外処理付き）
    - try/finallyで確実なリソース解放
    - 例外が発生してもファイルが確実に閉じられる
    """
    file_manager = FileManager("application.log")
    
    try:
        file_manager.open()
        yield file_manager
    except Exception as e:
        # 例外をログに記録（実際の実装では適切なロガーを使用）
        print(f"Exception in file manager: {e}")
        # 例外を再発生させて上位に伝播
        raise
    finally:
        # 例外の有無に関わらず実行される清理コード
        file_manager.close()

@app.post("/write-log/")
async def write_log(
    message: str,
    file_mgr: Annotated[FileManager, Depends(get_file_manager)]
):
    """
    ログ書き込みエンドポイント
    - ファイル管理依存性を使用
    - 例外が発生してもファイルが確実に閉じられる
    """
    try:
        result = file_mgr.write(f"[{datetime.now()}] {message}")
        return {
            "message": "Log written successfully",
            "result": result,
            "operations": file_mgr.operations
        }
    except Exception as e:
        # ビジネスロジックでの例外処理
        raise HTTPException(status_code=500, detail=f"Failed to write log: {e}")


# --------------------------------------------------
# 24. 階層的yield依存性（Sub-dependencies with yield）
# --------------------------------------------------

# レベル1：基本接続
async def get_connection():
    """
    基本接続依存性
    - 最下位レベルのリソース
    """
    print("Creating connection...")
    connection = {"id": "conn_123", "status": "connected"}
    
    try:
        yield connection
    finally:
        print("Closing connection...")

# レベル2：セッション（接続に依存）
async def get_session(
    conn: Annotated[dict, Depends(get_connection)]
):
    """
    セッション依存性
    - 接続に依存する上位レベルリソース
    """
    print(f"Creating session with connection {conn['id']}...")
    session = {
        "id": "session_456", 
        "connection_id": conn["id"],
        "transactions": []
    }
    
    try:
        yield session
    finally:
        print(f"Closing session {session['id']}...")

# レベル3：トランザクション（セッションに依存）
async def get_transaction(
    session: Annotated[dict, Depends(get_session)]
):
    """
    トランザクション依存性
    - セッションに依存する最上位レベルリソース
    """
    print(f"Starting transaction in session {session['id']}...")
    transaction = {
        "id": "tx_789",
        "session_id": session["id"],
        "operations": []
    }
    session["transactions"].append(transaction["id"])
    
    try:
        yield transaction
    finally:
        print(f"Committing transaction {transaction['id']}...")

@app.post("/complex-database-operation/")
async def complex_database_operation(
    data: dict,
    tx: Annotated[dict, Depends(get_transaction)]
):
    """
    複雑なデータベース操作
    - 3レベルの階層的yield依存性
    - 実行順序：connection → session → transaction → 関数
    - 終了順序：transaction → session → connection（逆順）
    """
    # トランザクション内での操作
    tx["operations"].extend([
        f"INSERT INTO table1 VALUES ({data})",
        f"UPDATE table2 SET status='processed'",
        f"DELETE FROM temp_table WHERE id < 100"
    ])
    
    return {
        "message": "Complex operation completed",
        "transaction_id": tx["id"],
        "session_id": tx["session_id"],
        "operations": tx["operations"],
        "data_processed": data
    }


# --------------------------------------------------
# 25. HTTPExceptionを使用するyield依存性
# --------------------------------------------------

# カスタム例外クラス
class ResourceError(Exception):
    pass

class SecurityError(Exception):
    pass

# リソース管理データ
resource_registry = {}

async def get_secure_resource(resource_id: str = Query(...)):
    """
    セキュアリソース依存性
    - yield後のコードでHTTPExceptionを発生可能
    - リソースアクセスの監査とセキュリティチェック
    """
    # リソース取得前の検証
    if resource_id.startswith("admin_") and resource_id not in ["admin_allowed"]:
        raise HTTPException(status_code=403, detail="Admin resource access denied")
    
    # リソース作成
    resource = {
        "id": resource_id,
        "created_at": datetime.now(),
        "access_count": 0
    }
    resource_registry[resource_id] = resource
    print(f"Resource {resource_id} created and registered")
    
    try:
        yield resource
    except ResourceError as e:
        # カスタム例外をHTTPExceptionに変換
        raise HTTPException(status_code=400, detail=f"Resource error: {e}")
    except SecurityError as e:
        # セキュリティ例外の処理
        raise HTTPException(status_code=403, detail=f"Security violation: {e}")
    finally:
        # リソース使用後の監査ログ
        if resource["access_count"] > 10:
            print(f"WARNING: Resource {resource_id} accessed {resource['access_count']} times")
        
        # リソース登録解除
        if resource_id in resource_registry:
            del resource_registry[resource_id]
            print(f"Resource {resource_id} unregistered")

@app.get("/secure-resource/{operation}")
async def access_secure_resource(
    operation: str,
    resource: Annotated[dict, Depends(get_secure_resource)]
):
    """
    セキュアリソースアクセス
    - yield依存性での例外処理とHTTPException
    """
    resource["access_count"] += 1
    
    # 操作に応じた例外発生のシミュレート
    if operation == "dangerous":
        raise ResourceError("Dangerous operation not allowed")
    elif operation == "unauthorized":
        raise SecurityError("Unauthorized access attempt")
    elif operation == "normal":
        return {
            "message": "Secure operation completed",
            "resource_id": resource["id"],
            "access_count": resource["access_count"],
            "operation": operation
        }
    else:
        raise HTTPException(status_code=400, detail="Unknown operation")


# --------------------------------------------------
# 26. コンテキストマネージャーとyield依存性
# --------------------------------------------------

class CustomContextManager:
    """
    カスタムコンテキストマネージャー
    - __enter__と__exit__メソッドを実装
    - withステートメントで使用可能
    """
    def __init__(self, name: str):
        self.name = name
        self.resources = []
    
    def __enter__(self):
        print(f"Entering context: {self.name}")
        self.resources.append(f"resource_for_{self.name}")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(f"Exiting context: {self.name}")
        if exc_type:
            print(f"Exception occurred: {exc_type.__name__}: {exc_value}")
        self.resources.clear()
        return False  # 例外を再発生させる
    
    def do_work(self, task: str):
        return f"Completed {task} with resources: {self.resources}"

async def get_context_managed_resource():
    """
    コンテキストマネージャーを使用するyield依存性
    - withステートメントでリソース管理
    - 例外処理の自動化
    """
    with CustomContextManager("api_resource") as manager:
        yield manager

@app.post("/context-managed-operation/")
async def context_managed_operation(
    task: str,
    manager: Annotated[CustomContextManager, Depends(get_context_managed_resource)]
):
    """
    コンテキスト管理された操作
    - カスタムコンテキストマネージャーを使用
    - 自動的なリソース管理と例外処理
    """
    result = manager.do_work(task)
    
    return {
        "message": "Context managed operation completed",
        "result": result,
        "context_name": manager.name,
        "available_resources": manager.resources
    }


# --------------------------------------------------
# 27. 実践的なyield依存性の例：Redis接続管理
# --------------------------------------------------

class RedisConnection:
    """Redis接続をシミュレートするクラス"""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connected = False
        self.operations = []
    
    async def connect(self):
        """Redis接続"""
        print(f"Connecting to Redis at {self.host}:{self.port}")
        self.connected = True
    
    async def disconnect(self):
        """Redis切断"""
        print(f"Disconnecting from Redis at {self.host}:{self.port}")
        self.connected = False
    
    async def set(self, key: str, value: str):
        """値の設定"""
        if not self.connected:
            raise Exception("Not connected to Redis")
        self.operations.append(f"SET {key} {value}")
        return f"OK: SET {key}"
    
    async def get(self, key: str):
        """値の取得"""
        if not self.connected:
            raise Exception("Not connected to Redis")
        self.operations.append(f"GET {key}")
        return f"value_for_{key}"

async def get_redis_connection():
    """
    Redis接続依存性
    - 非同期リソース管理の実践例
    - 接続プールの代替として使用
    """
    redis = RedisConnection("localhost", 6379)
    
    try:
        await redis.connect()
        yield redis
    except Exception as e:
        print(f"Redis error: {e}")
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    finally:
        await redis.disconnect()

@app.post("/cache-operation/")
async def cache_operation(
    key: str,
    value: str,
    redis: Annotated[RedisConnection, Depends(get_redis_connection)]
):
    """
    キャッシュ操作エンドポイント
    - Redis接続の自動管理
    - 非同期リソース処理
    """
    # キャッシュに値を設定
    set_result = await redis.set(key, value)
    
    # 設定した値を取得して確認
    get_result = await redis.get(key)
    
    return {
        "message": "Cache operation completed",
        "set_result": set_result,
        "get_result": get_result,
        "operations": redis.operations,
        "connection": f"{redis.host}:{redis.port}"
    }


# --------------------------------------------------
# 重要なポイント（最終更新版）
## 26. yield依存性：return代わりにyieldを使用してリソース管理
## 27. 実行順序：yield前（初期化）→ yield（注入）→ yield後（清理）
## 28. 例外処理：try/finally/exceptでの適切なリソース管理
## 29. 階層的管理：複数レベルのyield依存性の逆順清理
## 30. HTTPException：yield後のコードでも例外発生可能
## 31. コンテキストマネージャー：withステートメントとの統合
## 32. 非同期リソース：async/awaitを使った非同期リソース管理
## 33. 実践パターン：DB接続、ファイル、外部API、キャッシュ管理
# --------------------------------------------------