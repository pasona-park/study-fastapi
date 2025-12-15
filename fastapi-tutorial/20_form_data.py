from typing import Annotated, Union
from fastapi import FastAPI, Form, HTTPException, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

# --------------------------------------------------
# フォームデータ（Form Data）
## JSONの代わりにHTMLフォーム形式でデータを受信する方式
## 主な用途：
### 1. Webブラウザの<form>タグとの連携
### 2. OAuth2認証（パスワードフロー）
### 3. ファイルアップロードとの組み合わせ
### 4. 従来のWeb標準との互換性
## 注意：python-multipart のインストールが必要
# --------------------------------------------------

# 1. 基本的なフォームデータの使用
@app.post("/login/")
async def login(
    username: Annotated[str, Form()], 
    password: Annotated[str, Form()]
):
    """
    基本的なログインフォーム
    Content-Type: application/x-www-form-urlencoded
    """
    # 実際の実装では認証処理を行う
    if username == "admin" and password == "secret":
        return {"message": "Login successful", "username": username}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


# --------------------------------------------------
# フォームデータの検証とオプション
## Body、Query、Pathと同じ機能をすべて使用可能
# --------------------------------------------------

# 2. バリデーション付きフォームデータ
@app.post("/register/")
async def register(
    username: Annotated[str, Form(min_length=3, max_length=20)],
    email: Annotated[str, Form()],  # EmailStrは直接使用できないため、手動検証
    password: Annotated[str, Form(min_length=8)],
    full_name: Annotated[Union[str, None], Form()] = None,
    age: Annotated[Union[int, None], Form(ge=18, le=120)] = None
):
    """
    ユーザー登録フォーム（バリデーション付き）
    - username: 3-20文字
    - password: 8文字以上
    - age: 18-120歳（オプション）
    """
    # 簡単なメール形式チェック
    if "@" not in email or "." not in email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email format"
        )
    
    return {
        "message": "User registered successfully",
        "username": username,
        "email": email,
        "full_name": full_name,
        "age": age
    }


# --------------------------------------------------
# OAuth2標準に準拠したフォーム
## OAuth2仕様では username と password をフォームフィールドで送信
# --------------------------------------------------

# 3. OAuth2パスワードフロー準拠のフォーム
@app.post("/token/")
async def login_for_access_token(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    grant_type: Annotated[Union[str, None], Form()] = None,
    scope: Annotated[Union[str, None], Form()] = None,
    client_id: Annotated[Union[str, None], Form()] = None,
    client_secret: Annotated[Union[str, None], Form()] = None
):
    """
    OAuth2標準のトークン取得エンドポイント
    grant_type, scope, client_id, client_secret はOAuth2仕様のオプションフィールド
    """
    # 実際の実装では：
    # 1. ユーザー認証
    # 2. JWTトークン生成
    # 3. トークン返却
    
    if username == "testuser" and password == "testpass":
        return {
            "access_token": "fake-jwt-token",
            "token_type": "bearer",
            "expires_in": 3600
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )


# --------------------------------------------------
# フォームデータの高度な使用例
# --------------------------------------------------

# 4. 複雑なフォームデータの例
@app.post("/contact/")
async def submit_contact_form(
    name: Annotated[str, Form(min_length=1, max_length=100)],
    email: Annotated[str, Form()],
    subject: Annotated[str, Form(min_length=1, max_length=200)],
    message: Annotated[str, Form(min_length=10, max_length=1000)],
    phone: Annotated[Union[str, None], Form()] = None,
    company: Annotated[Union[str, None], Form()] = None,
    newsletter: Annotated[bool, Form()] = False  # チェックボックス
):
    """
    お問い合わせフォーム
    - 必須項目：名前、メール、件名、メッセージ
    - オプション項目：電話番号、会社名、ニュースレター購読
    """
    # 実際の実装では：
    # 1. メール送信
    # 2. データベース保存
    # 3. 自動返信メール送信
    
    contact_data = {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
        "phone": phone,
        "company": company,
        "newsletter_subscription": newsletter
    }
    
    return {
        "message": "Contact form submitted successfully",
        "contact_id": 12345,
        "data": contact_data
    }


# --------------------------------------------------
# フォームデータとPydanticモデルの組み合わせ
## 注意：FormとBodyを同時に使用することはできない
# --------------------------------------------------

# 5. フォームデータ用のレスポンスモデル
class LoginResponse(BaseModel):
    message: str
    username: str
    user_id: int
    last_login: Union[str, None] = None

class UserRegistrationResponse(BaseModel):
    message: str
    user_id: int
    username: str
    email: str
    created_at: str

@app.post("/login-with-response/", response_model=LoginResponse)
async def login_with_structured_response(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    remember_me: Annotated[bool, Form()] = False
):
    """
    構造化されたレスポンスを返すログインエンドポイント
    """
    # 実際の実装では認証とユーザー情報取得
    if username == "john" and password == "secret123":
        return LoginResponse(
            message="Login successful",
            username=username,
            user_id=1,
            last_login="2024-01-15T10:30:00Z" if remember_me else None
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )


# --------------------------------------------------
# エラーハンドリングとフォームデータ
# --------------------------------------------------

# 6. フォームデータのエラーハンドリング例
@app.post("/profile-update/")
async def update_profile(
    current_password: Annotated[str, Form()],
    new_password: Annotated[Union[str, None], Form(min_length=8)] = None,
    confirm_password: Annotated[Union[str, None], Form()] = None,
    display_name: Annotated[Union[str, None], Form(max_length=50)] = None,
    bio: Annotated[Union[str, None], Form(max_length=500)] = None
):
    """
    プロフィール更新フォーム
    パスワード変更時の確認処理を含む
    """
    # 現在のパスワード確認
    if current_password != "current_secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # 新しいパスワードの確認
    if new_password and confirm_password:
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password and confirmation do not match"
            )
    elif new_password and not confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password confirmation is required"
        )
    
    # 更新処理
    updates = {}
    if new_password:
        updates["password"] = "hashed_" + new_password
    if display_name:
        updates["display_name"] = display_name
    if bio:
        updates["bio"] = bio
    
    return {
        "message": "Profile updated successfully",
        "updated_fields": list(updates.keys())
    }


# --------------------------------------------------
# 実戦的な例：商品レビューフォーム
# --------------------------------------------------

# 7. 商品レビューフォームの例
@app.post("/products/{product_id}/reviews/")
async def submit_product_review(
    product_id: int,
    reviewer_name: Annotated[str, Form(min_length=1, max_length=100)],
    reviewer_email: Annotated[str, Form()],
    rating: Annotated[int, Form(ge=1, le=5)],  # 1-5星評価
    title: Annotated[str, Form(min_length=1, max_length=200)],
    review_text: Annotated[str, Form(min_length=10, max_length=2000)],
    recommend: Annotated[bool, Form()] = False,  # 推奨するかどうか
    verified_purchase: Annotated[bool, Form()] = False  # 購入確認済みかどうか
):
    """
    商品レビュー投稿フォーム
    - 評価：1-5星（必須）
    - レビュータイトル：1-200文字（必須）
    - レビュー本文：10-2000文字（必須）
    - 推奨フラグ：チェックボックス（オプション）
    """
    # 実際の実装では：
    # 1. 商品存在確認
    # 2. 重複レビューチェック
    # 3. データベース保存
    # 4. 商品評価の再計算
    
    review_data = {
        "product_id": product_id,
        "reviewer_name": reviewer_name,
        "reviewer_email": reviewer_email,
        "rating": rating,
        "title": title,
        "review_text": review_text,
        "recommend": recommend,
        "verified_purchase": verified_purchase,
        "created_at": "2024-01-15T10:30:00Z"
    }
    
    return {
        "message": "Review submitted successfully",
        "review_id": 67890,
        "review": review_data
    }


# --------------------------------------------------
# 重要なポイント
## 1. python-multipart のインストールが必要
## 2. FormはBodyから直接継承（同じ機能を使用可能）
## 3. FormとBodyを同時に使用することはできない（HTTP制限）
## 4. application/x-www-form-urlencoded でエンコード
## 5. OAuth2などのWeb標準に準拠
# --------------------------------------------------


# 8. フォームデータの制限事項を示す例
class UserData(BaseModel):
    name: str
    age: int

# ❌ これは動作しない：FormとBodyの同時使用
# @app.post("/mixed-data/")
# async def mixed_data_endpoint(
#     form_field: Annotated[str, Form()],
#     json_data: UserData  # これはJSONとして解釈される
# ):
#     # HTTPプロトコルの制限により、リクエストボディは
#     # application/json または application/x-www-form-urlencoded
#     # のどちらか一つしか使用できない
#     pass

# ✅ 正しい方法：すべてフォームデータとして受信
@app.post("/form-only-data/")
async def form_only_data(
    name: Annotated[str, Form()],
    age: Annotated[int, Form()],
    email: Annotated[str, Form()]
):
    """
    すべてのデータをフォームフィールドとして受信
    """
    return {
        "message": "Data received via form",
        "data": {
            "name": name,
            "age": age,
            "email": email
        }
    }

# ✅ または、すべてJSONとして受信
@app.post("/json-only-data/")
async def json_only_data(user_data: UserData):
    """
    すべてのデータをJSONとして受信
    """
    return {
        "message": "Data received via JSON",
        "data": user_data.dict()
    }