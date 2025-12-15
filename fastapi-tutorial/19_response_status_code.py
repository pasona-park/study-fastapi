from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Union

app = FastAPI()

# --------------------------------------------------
# 応答ステータスコード（Response Status Code）
## HTTP応答に含まれる3桁の数字で、リクエスト処理結果を表す
## FastAPIでは status_code パラメータで簡単に設定可能
## 主な役割：
### 1. クライアントに処理結果を通知
### 2. OpenAPIスキーマに自動文書化
### 3. 適切なHTTPセマンティクスの実装
# --------------------------------------------------

# 1. 基本的なステータスコードの使用
@app.post("/items/", status_code=201)
async def create_item_basic(name: str):
    return {"name": name}
# 201 = Created（作成済み）を数値で直接指定

# より読みやすい方法：status定数を使用（推奨）
@app.post("/items-improved/", status_code=status.HTTP_201_CREATED)
async def create_item_improved(name: str):
    return {"name": name}
# IDEの自動補完機能が使える + 可読性向上


# --------------------------------------------------
# HTTPステータスコードの分類と使い分け
# --------------------------------------------------

# 2. 2xx系 - 成功レスポンス（最も多用）
class Item(BaseModel):
    id: int
    name: str
    description: Union[str, None] = None

class ItemCreate(BaseModel):
    name: str
    description: Union[str, None] = None

# 200 OK - デフォルト（明示的に指定する必要なし）
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"id": item_id, "name": "Sample Item", "description": "A great item"}

# 201 Created - 新しいリソース作成時
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    # 実際の実装ではDBに保存
    new_item = {"id": 1, **item.dict()}
    return new_item

# 204 No Content - 成功したが返すコンテンツなし
@app.put("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(item_id: int, item: ItemCreate):
    # 実際の実装ではDBを更新
    print(f"Item {item_id} updated with {item.dict()}")
    # 204の場合、レスポンスボディは返さない（FastAPIが自動処理）

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    # 実際の実装ではDBから削除
    print(f"Item {item_id} deleted")
    # 204の場合、レスポンスボディなし


# --------------------------------------------------
# 4xx系 - クライアントエラー（2番目に多用）
# --------------------------------------------------

# 3. クライアントエラーの例
@app.get("/items-with-validation/{item_id}")
async def get_item_with_validation(item_id: int):
    # 実際の実装では存在チェックを行う
    if item_id == 999:  # 存在しないアイテムの例
        # FastAPIが自動的に404を返すが、明示的に指定も可能
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return {"id": item_id, "name": "Found Item"}


# --------------------------------------------------
# 実戦的な例：ユーザー管理API
# --------------------------------------------------

# 4. 実戦例：ユーザー管理システムでの適切なステータスコード使用
class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    username: Union[str, None] = None
    email: Union[str, None] = None
    is_active: Union[bool, None] = None

# ユーザー一覧取得 - 200 OK（デフォルト）
@app.get("/users/")
async def get_users():
    return [
        {"id": 1, "username": "john", "email": "john@example.com", "is_active": True},
        {"id": 2, "username": "jane", "email": "jane@example.com", "is_active": True}
    ]

# ユーザー作成 - 201 Created
@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # 実際の実装では：
    # 1. パスワードをハッシュ化
    # 2. DBに保存
    # 3. 作成されたユーザー情報を返す
    new_user = {
        "id": 3,
        "username": user.username,
        "email": user.email,
        "is_active": True
    }
    return new_user

# ユーザー情報取得 - 200 OK
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 実際の実装では存在チェックとDB取得
    return {
        "id": user_id,
        "username": "john",
        "email": "john@example.com",
        "is_active": True
    }

# ユーザー情報更新 - 200 OK（更新後のデータを返す場合）
@app.put("/users/{user_id}")
async def update_user_with_response(user_id: int, user: UserUpdate):
    # 実際の実装ではDBを更新し、更新後のデータを返す
    updated_user = {
        "id": user_id,
        "username": user.username or "john",
        "email": user.email or "john@example.com",
        "is_active": user.is_active if user.is_active is not None else True
    }
    return updated_user

# ユーザー情報更新 - 204 No Content（更新のみ、データを返さない場合）
@app.patch("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_no_response(user_id: int, user: UserUpdate):
    # 実際の実装ではDBを更新するが、レスポンスボディは返さない
    print(f"User {user_id} updated with {user.dict(exclude_unset=True)}")
    # 204の場合、returnは不要（FastAPIが自動処理）

# ユーザー削除 - 204 No Content
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    # 実際の実装ではDBから削除
    print(f"User {user_id} deleted")
    # レスポンスボディなし


# --------------------------------------------------
# 高度な例：条件付きステータスコード
# --------------------------------------------------

# 5. 条件に応じて異なるステータスコードを返す例
@app.post("/users/{user_id}/activate")
async def activate_user(user_id: int):
    # 実際の実装では：
    # 1. ユーザーの存在確認
    # 2. 現在のアクティブ状態確認
    # 3. 状態に応じて適切なレスポンス
    
    # 例：ユーザーが既にアクティブな場合
    user_already_active = True  # 実際はDBから取得
    
    if user_already_active:
        # 304 Not Modified - 変更する必要がない
        from fastapi import Response
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    else:
        # 200 OK - アクティベーション成功
        return {"message": f"User {user_id} activated successfully"}


# --------------------------------------------------
# よく使用されるステータスコード一覧
# --------------------------------------------------

# 6. 主要なステータスコードの使用例まとめ
class StatusCodeExamples:
    """
    よく使用されるHTTPステータスコードの例
    
    2xx - 成功:
    - 200 OK: 一般的な成功（デフォルト）
    - 201 Created: リソース作成成功
    - 204 No Content: 成功したがコンテンツなし
    
    4xx - クライアントエラー:
    - 400 Bad Request: 一般的なクライアントエラー
    - 401 Unauthorized: 認証が必要
    - 403 Forbidden: 認証済みだが権限なし
    - 404 Not Found: リソースが見つからない
    - 422 Unprocessable Entity: バリデーションエラー
    
    5xx - サーバーエラー:
    - 500 Internal Server Error: 一般的なサーバーエラー
    """
    pass

# 実際の使用例
@app.get("/status-examples/success", status_code=status.HTTP_200_OK)
async def success_example():
    return {"message": "Success"}

@app.post("/status-examples/created", status_code=status.HTTP_201_CREATED)
async def created_example():
    return {"message": "Resource created"}

@app.put("/status-examples/no-content", status_code=status.HTTP_204_NO_CONTENT)
async def no_content_example():
    pass  # レスポンスボディなし

@app.get("/status-examples/not-modified")
async def not_modified_example():
    from fastapi import Response
    return Response(status_code=status.HTTP_304_NOT_MODIFIED)


# --------------------------------------------------
# 重要なポイント
## 1. status_codeはデコレータのパラメータ（関数パラメータではない）
## 2. 数値または status 定数を使用可能
## 3. OpenAPI文書に自動含有
## 4. 一部のステータスコードは応答ボディなしを意味
## 5. 適切なHTTPセマンティクスの実装が重要
# --------------------------------------------------


# 7. 実戦的なRESTful APIの例
class BlogPost(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    published: bool = False

class BlogPostCreate(BaseModel):
    title: str
    content: str
    author_id: int

class BlogPostUpdate(BaseModel):
    title: Union[str, None] = None
    content: Union[str, None] = None
    published: Union[bool, None] = None

# RESTful APIの完全な例
@app.get("/posts/")  # 200 OK（デフォルト）
async def list_posts():
    return [
        {"id": 1, "title": "First Post", "content": "Hello World", "author_id": 1, "published": True}
    ]

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: BlogPostCreate):
    new_post = {"id": 1, **post.dict(), "published": False}
    return new_post

@app.get("/posts/{post_id}")  # 200 OK（デフォルト）
async def get_post(post_id: int):
    return {"id": post_id, "title": "Sample Post", "content": "Content", "author_id": 1, "published": True}

@app.put("/posts/{post_id}")  # 200 OK（更新後のデータを返す）
async def update_post(post_id: int, post: BlogPostUpdate):
    updated_post = {"id": post_id, "title": "Updated Title", "content": "Updated Content", "author_id": 1, "published": True}
    return updated_post

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    pass  # 削除成功、レスポンスボディなし

# 公開/非公開の切り替え
@app.patch("/posts/{post_id}/publish", status_code=status.HTTP_204_NO_CONTENT)
async def publish_post(post_id: int):
    # 実際の実装では published = True に更新
    pass

@app.patch("/posts/{post_id}/unpublish", status_code=status.HTTP_204_NO_CONTENT)
async def unpublish_post(post_id: int):
    # 実際の実装では published = False に更新
    pass