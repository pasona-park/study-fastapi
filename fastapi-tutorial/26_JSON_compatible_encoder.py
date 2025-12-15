from datetime import datetime, date, time
from typing import Union, List, Dict, Any
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4
from pathlib import Path

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
import json

app = FastAPI()

# --------------------------------------------------
# JSON互換エンコーダー（JSON Compatible Encoder）
## PydanticモデルやdatetimeなどのPythonオブジェクトをJSON互換形式に変換
## 主な用途：
### 1. データベース保存（NoSQLなどJSON互換データのみ受け入れるDB）
### 2. 外部API連携（JSON形式でのデータ送信）
### 3. キャッシング（RedisなどにJSON形式で保存）
### 4. ログ記録（構造化ログをJSONで記録）
## 重要：JSON文字列ではなく、Python標準データ構造（dict等）を返す
# --------------------------------------------------

# 偽のデータベース（JSON互換データのみ受け入れる）
fake_db = {}

# 1. 基本的なPydanticモデル
class Item(BaseModel):
    title: str
    timestamp: datetime
    description: Union[str, None] = None

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    """
    基本的なjsonable_encoder使用例
    - PydanticモデルをJSON互換dictに変換
    - datetimeをISO形式文字列に変換
    """
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    
    return {
        "message": "Item updated",
        "original_type": str(type(item)),
        "converted_type": str(type(json_compatible_item_data)),
        "converted_data": json_compatible_item_data
    }


# --------------------------------------------------
# 様々なデータ型の変換例
# --------------------------------------------------

# 2. 複雑なデータ型を含むモデル
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class ComplexItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    price: Decimal
    created_at: datetime
    updated_date: date
    processing_time: time
    status: StatusEnum
    file_path: Path
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

@app.post("/complex-items/")
def create_complex_item(item: ComplexItem):
    """
    複雑なデータ型の変換例
    - UUID → 文字列
    - Decimal → float
    - datetime → ISO形式文字列
    - date → ISO形式文字列
    - time → ISO形式文字列
    - Enum → 値（文字列）
    - Path → 文字列
    """
    # 元のオブジェクト
    print("Original object:", item)
    print("Original types:")
    print(f"  id: {type(item.id)}")
    print(f"  price: {type(item.price)}")
    print(f"  created_at: {type(item.created_at)}")
    
    # JSON互換形式に変換
    json_compatible_data = jsonable_encoder(item)
    
    print("Converted data:", json_compatible_data)
    print("Converted types:")
    print(f"  id: {type(json_compatible_data['id'])}")
    print(f"  price: {type(json_compatible_data['price'])}")
    print(f"  created_at: {type(json_compatible_data['created_at'])}")
    
    # データベースに保存
    item_id = str(item.id)
    fake_db[item_id] = json_compatible_data
    
    return {
        "message": "Complex item created",
        "item_id": item_id,
        "json_compatible_data": json_compatible_data
    }


# --------------------------------------------------
# ネストされたモデルの変換
# --------------------------------------------------

# 3. ネストされたモデル
class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    created_at: datetime
    last_login: Union[datetime, None] = None
    address: Union[Address, None] = None
    preferences: Dict[str, Union[str, int, bool]] = {}

@app.post("/users/")
def create_user(user: User):
    """
    ネストされたモデルの変換例
    - 再帰的にすべてのネストされたオブジェクトを変換
    - Addressモデルもdictに変換される
    """
    # JSON互換形式に変換
    json_compatible_user = jsonable_encoder(user)
    
    # データベースに保存
    user_id = str(user.id)
    fake_db[user_id] = json_compatible_user
    
    return {
        "message": "User created",
        "user_id": user_id,
        "converted_data": json_compatible_user,
        "address_type": type(json_compatible_user.get("address", None))
    }


# --------------------------------------------------
# リストとディクショナリの変換
# --------------------------------------------------

# 4. リストとディクショナリを含むモデル
class Product(BaseModel):
    name: str
    variants: List[Dict[str, Union[str, float, datetime]]]
    specifications: Dict[str, Union[str, int, float, bool]]
    reviews: List['Review'] = []

class Review(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime
    reviewer_name: str

# Pydantic v2での前方参照解決
Product.model_rebuild()

@app.post("/products/")
def create_product(product: Product):
    """
    リストとディクショナリの変換例
    - リスト内のすべての要素も変換
    - ディクショナリ内のすべての値も変換
    - ネストされたReviewモデルも変換
    """
    json_compatible_product = jsonable_encoder(product)
    
    # データベースに保存
    product_id = str(uuid4())
    fake_db[product_id] = json_compatible_product
    
    return {
        "message": "Product created",
        "product_id": product_id,
        "converted_data": json_compatible_product
    }


# --------------------------------------------------
# 実戦的な使用例
# --------------------------------------------------

# 5. データベース操作のヘルパー関数
def save_to_db(collection: str, data: Any) -> str:
    """
    データベース保存ヘルパー
    - 任意のPydanticモデルをJSON互換形式で保存
    """
    json_data = jsonable_encoder(data)
    record_id = str(uuid4())
    
    if collection not in fake_db:
        fake_db[collection] = {}
    
    fake_db[collection][record_id] = json_data
    return record_id

def get_from_db(collection: str, record_id: str) -> Union[Dict, None]:
    """データベースから取得"""
    return fake_db.get(collection, {}).get(record_id)

@app.post("/save-any-model/")
def save_any_model(model_type: str, data: Dict[str, Any]):
    """
    汎用モデル保存エンドポイント
    - jsonable_encoderを使用して任意のデータを保存
    """
    # データをそのまま保存（既にdictの場合）
    if isinstance(data, dict):
        json_data = jsonable_encoder(data)
    else:
        json_data = jsonable_encoder(data)
    
    record_id = save_to_db(model_type, json_data)
    
    return {
        "message": f"{model_type} saved successfully",
        "record_id": record_id,
        "saved_data": json_data
    }


# --------------------------------------------------
# キャッシングとログ記録の例
# --------------------------------------------------

# 6. キャッシング用の変換
class CacheableData(BaseModel):
    key: str
    value: Any
    expires_at: datetime
    metadata: Dict[str, Any] = {}

# 偽のキャッシュストレージ
cache_storage = {}

@app.post("/cache/")
def cache_data(data: CacheableData):
    """
    キャッシュデータの保存
    - JSON互換形式でキャッシュに保存
    - Redisなどの外部キャッシュシステムとの互換性
    """
    json_compatible_cache_data = jsonable_encoder(data)
    
    # キャッシュに保存（実際の実装ではRedisなどを使用）
    cache_storage[data.key] = json_compatible_cache_data
    
    return {
        "message": "Data cached successfully",
        "cache_key": data.key,
        "cached_data": json_compatible_cache_data
    }

# 7. ログ記録用の変換
class LogEntry(BaseModel):
    level: str
    message: str
    timestamp: datetime
    user_id: Union[UUID, None] = None
    request_data: Dict[str, Any] = {}
    response_data: Dict[str, Any] = {}

@app.post("/log/")
def create_log_entry(log_entry: LogEntry):
    """
    ログエントリの作成
    - 構造化ログをJSON形式で記録
    - ログ分析システムとの互換性
    """
    json_log_data = jsonable_encoder(log_entry)
    
    # ログファイルに書き込み（実際の実装ではloggingライブラリを使用）
    print("LOG:", json.dumps(json_log_data, indent=2))
    
    return {
        "message": "Log entry created",
        "log_data": json_log_data
    }


# --------------------------------------------------
# 外部API連携の例
# --------------------------------------------------

# 8. 外部API用のデータ変換
class ExternalAPIPayload(BaseModel):
    transaction_id: UUID
    amount: Decimal
    currency: str
    timestamp: datetime
    customer_data: Dict[str, Any]

@app.post("/external-api/")
def send_to_external_api(payload: ExternalAPIPayload):
    """
    外部API連携用のデータ変換
    - 外部APIが期待するJSON形式に変換
    - HTTP クライアントでの送信準備
    """
    json_payload = jsonable_encoder(payload)
    
    # 実際の実装では、httpxやrequestsを使用して外部APIに送信
    # response = httpx.post("https://external-api.com/endpoint", json=json_payload)
    
    return {
        "message": "Data prepared for external API",
        "json_payload": json_payload,
        "payload_ready_for_json_dumps": True
    }


# --------------------------------------------------
# デバッグとテスト用のエンドポイント
# --------------------------------------------------

# 9. 変換結果の比較
@app.post("/compare-conversion/")
def compare_conversion(item: Item):
    """
    変換前後の比較デモ
    - 元のオブジェクトと変換後のデータを比較
    - デバッグやテスト用
    """
    original_data = {
        "object": item,
        "type": str(type(item)),
        "timestamp_type": str(type(item.timestamp)),
        "can_json_dumps": False
    }
    
    # JSON互換形式に変換
    converted_data = jsonable_encoder(item)
    
    # json.dumps()でテスト
    try:
        json_string = json.dumps(converted_data)
        can_dumps = True
    except Exception as e:
        json_string = str(e)
        can_dumps = False
    
    converted_info = {
        "object": converted_data,
        "type": str(type(converted_data)),
        "timestamp_type": str(type(converted_data.get("timestamp"))),
        "can_json_dumps": can_dumps,
        "json_string": json_string if can_dumps else None
    }
    
    return {
        "original": original_data,
        "converted": converted_info
    }

# 10. データベース内容確認
@app.get("/db-contents/")
def get_db_contents():
    """
    データベース内容確認
    - 保存されたJSON互換データの確認
    """
    return {
        "message": "Database contents",
        "total_records": len(fake_db),
        "collections": list(fake_db.keys()) if isinstance(fake_db, dict) else "Not a dict",
        "sample_data": dict(list(fake_db.items())[:3]) if fake_db else {}
    }


# --------------------------------------------------
# 重要なポイント
## 1. JSON文字列ではなく、Python標準データ構造（dict等）を返す
## 2. 再帰的にすべてのネストされたオブジェクトを変換
## 3. Pydanticの直列化ルールに従う
## 4. json.dumps()で直接JSON文字列に変換可能
## 5. データベース保存、キャッシング、外部API連携に有用
## 6. FastAPI内部でも広範囲に使用されている
## 7. 元のデータ構造を保持しながら型のみ変換
## 8. パフォーマンスが最適化されている
# --------------------------------------------------