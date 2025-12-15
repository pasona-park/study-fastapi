from typing import Annotated, Union
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

app = FastAPI()

# --------------------------------------------------
# エラーハンドリング（Handling Errors）
## API使用中に発生する様々なエラー状況をクライアントに適切に通知する機能
## HTTP ステータスコードと構造化されたエラー情報を提供
## 主なエラー状況：
### 1. 権限不足：クライアントが該当操作を実行する権限がない
### 2. アクセス拒否：リソースへのアクセス権限がない
### 3. リソース不存在：要求されたアイテムが存在しない（404エラー）
### 4. 不正なリクエスト：クライアントが間違ったデータを送信
# --------------------------------------------------

# テストデータ
items = {"foo": "The Foo Wrestlers"}
users = {
    1: {"name": "Alice", "email": "alice@example.com"},
    2: {"name": "Bob", "email": "bob@example.com"}
}

# 1. 基本的なHTTPExceptionの使用
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    """
    基本的なHTTPException使用例
    - 存在しないアイテムに対して404エラーを返す
    - HTTPExceptionはPython例外なので raise で使用
    """
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}


# --------------------------------------------------
# HTTPExceptionの詳細な使用例
# --------------------------------------------------

# 2. 様々なエラーケースの処理
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """
    様々なエラーケースを処理する例
    - 存在しないユーザー：404
    - 特定条件での403（権限エラー）
    """
    # ユーザー存在チェック
    if user_id not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 特定ユーザーへのアクセス制限例
    if user_id == 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this user is forbidden"
        )
    
    return {"user": users[user_id]}


# 3. 詳細なエラー情報を含むHTTPException
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """
    詳細なエラー情報を提供する例
    - detail フィールドに辞書やリストも使用可能
    - JSON変換可能な任意の値を設定可能
    """
    if user_id not in users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "User not found",
                "user_id": user_id,
                "available_users": list(users.keys()),
                "suggestion": "Please check the user ID and try again"
            }
        )
    
    # 管理者ユーザーの削除を防ぐ例
    if user_id == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Cannot delete admin user",
                "user_id": user_id,
                "user_role": "admin",
                "message": "Admin users cannot be deleted for security reasons"
            }
        )
    
    # 実際の実装では、ここでユーザーを削除
    del users[user_id]
    return {"message": f"User {user_id} deleted successfully"}


# --------------------------------------------------
# カスタムヘッダー付きHTTPException
# --------------------------------------------------

# 4. カスタムヘッダーを含むエラーレスポンス
@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    """
    カスタムヘッダー付きエラーレスポンス
    - セキュリティ用途などで追加ヘッダーが必要な場合
    - WWW-Authenticate ヘッダーなど
    """
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
            headers={
                "X-Error": "There goes my error",
                "X-Request-ID": "12345",
                "Cache-Control": "no-cache"
            }
        )
    return {"item": items[item_id]}


# --------------------------------------------------
# カスタム例外クラスとハンドラー
# --------------------------------------------------

# 5. カスタム例外クラスの定義
class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

class BusinessLogicException(Exception):
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code

# カスタム例外ハンドラー
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    """
    カスタム例外ハンドラー
    - アプリケーション固有の例外を処理
    - 統一されたエラーレスポンス形式を提供
    """
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Oops! {exc.name} did something. There goes a rainbow...",
            "exception_type": "UnicornException",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    )

@app.exception_handler(BusinessLogicException)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """
    ビジネスロジック例外ハンドラー
    - ビジネスルール違反時の統一エラー処理
    """
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "type": "business_logic_error"
        }
    )

# カスタム例外を使用するエンドポイント
@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    """カスタム例外を発生させる例"""
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

@app.post("/business-operation/")
async def business_operation(value: int):
    """ビジネスロジック例外の例"""
    if value < 0:
        raise BusinessLogicException(
            message="Negative values are not allowed in this operation",
            error_code="NEGATIVE_VALUE_ERROR"
        )
    if value > 1000:
        raise BusinessLogicException(
            message="Value exceeds maximum allowed limit",
            error_code="VALUE_TOO_LARGE"
        )
    return {"result": value * 2}


# --------------------------------------------------
# デフォルト例外ハンドラーのオーバーライド
# --------------------------------------------------

# 6. リクエスト検証エラーのカスタムハンドラー
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    リクエスト検証エラーのカスタムハンドラー
    - デフォルトのJSONエラーをプレーンテキストに変更
    - より読みやすいエラーメッセージを提供
    """
    message = "Validation errors:"
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        message += f"\nField: {field}, Error: {error['msg']}"
    
    return PlainTextResponse(message, status_code=400)

# 7. HTTPException ハンドラーのオーバーライド
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler_override(request: Request, exc: StarletteHTTPException):
    """
    HTTPExceptionハンドラーのオーバーライド
    - デフォルトのJSONレスポンスをプレーンテキストに変更
    """
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


# --------------------------------------------------
# 検証エラー時のリクエストボディ情報を含む例
# --------------------------------------------------

# 8. リクエストボディを含む検証エラーハンドラー
class Item(BaseModel):
    title: str
    size: int

# 別のバリデーションエラーハンドラー（リクエストボディ付き）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler_with_body(request: Request, exc: RequestValidationError):
    """
    リクエストボディを含む検証エラーハンドラー
    - 開発時のデバッグに有用
    - 受信したデータと一緒にエラー情報を返す
    """
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Validation failed for the provided data"
        })
    )

@app.post("/items/")
async def create_item(item: Item):
    """アイテム作成（検証エラーテスト用）"""
    return item


# --------------------------------------------------
# デフォルトハンドラーの再利用
# --------------------------------------------------

# 9. デフォルト例外ハンドラーの再利用
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    デフォルトハンドラーを再利用するカスタムハンドラー
    - ログ出力などの追加処理を行った後、デフォルト処理を実行
    """
    print(f"OMG! An HTTP error!: {repr(exc)}")
    # ここで追加のログ処理、監視システムへの通知などを実行
    
    # デフォルトハンドラーを呼び出し
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler_with_logging(request: Request, exc: RequestValidationError):
    """
    ログ付きバリデーションエラーハンドラー
    """
    print(f"OMG! The client sent invalid data!: {exc}")
    # ここで詳細なログ記録、エラー分析などを実行
    
    # デフォルトハンドラーを呼び出し
    return await request_validation_exception_handler(request, exc)


# --------------------------------------------------
# 実戦的なエラーハンドリングの例
# --------------------------------------------------

# 10. 実戦的なAPIエラーハンドリング
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """
    統一されたAPIエラーハンドラー
    - 全てのAPIエラーを統一形式で処理
    - エラーコード、メッセージ、タイムスタンプを含む
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code or "GENERIC_ERROR",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )

@app.get("/protected-resource/{resource_id}")
async def get_protected_resource(resource_id: int):
    """
    保護されたリソースへのアクセス例
    - 様々なエラーケースを統一されたAPIErrorで処理
    """
    # リソース存在チェック
    if resource_id not in range(1, 101):
        raise APIError(
            message="Resource not found",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND"
        )
    
    # 権限チェック（例）
    if resource_id > 50:
        raise APIError(
            message="Insufficient permissions to access this resource",
            status_code=403,
            error_code="INSUFFICIENT_PERMISSIONS"
        )
    
    # レート制限チェック（例）
    if resource_id == 42:
        raise APIError(
            message="Rate limit exceeded. Please try again later",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )
    
    return {
        "resource_id": resource_id,
        "data": f"Protected data for resource {resource_id}"
    }


# --------------------------------------------------
# 重要なポイント
## 1. HTTPExceptionはPython例外（raiseで使用）
## 2. 例外発生時は関数実行が即座に中断
## 3. detailフィールドにはJSON変換可能な任意の値を設定可能
## 4. カスタムヘッダーでセキュリティ情報などを追加可能
## 5. カスタム例外ハンドラーで統一されたエラー処理を実現
## 6. デフォルトハンドラーをオーバーライドして独自の形式に変更可能
## 7. FastAPIとStarletteのHTTPExceptionの違いに注意
## 8. デフォルトハンドラーの再利用で一貫性を保持
# --------------------------------------------------


# 11. エラーレスポンスの統一化例
class StandardErrorResponse(BaseModel):
    success: bool = False
    error: dict
    timestamp: str
    request_id: str

def create_error_response(message: str, error_code: str, status_code: int) -> dict:
    """標準エラーレスポンス作成ヘルパー"""
    return {
        "success": False,
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code
        },
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req_12345"
    }

@app.get("/standardized-error-example/{item_id}")
async def standardized_error_example(item_id: str):
    """
    標準化されたエラーレスポンスの例
    - 全てのエラーが同じ形式で返される
    - フロントエンドでの処理が統一される
    """
    if item_id == "error":
        error_response = create_error_response(
            message="This is a standardized error example",
            error_code="EXAMPLE_ERROR",
            status_code=400
        )
        return JSONResponse(
            status_code=400,
            content=error_response
        )
    
    return {"item_id": item_id, "message": "Success"}