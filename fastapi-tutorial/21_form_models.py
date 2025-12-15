from typing import Annotated, Union
from fastapi import FastAPI, Form, HTTPException, status
from pydantic import BaseModel, Field, validator
from datetime import datetime

app = FastAPI()

# --------------------------------------------------
# フォームモデル（Form Models）
## Pydanticモデルを使用してフォームフィールドを構造化して宣言・処理する機能
## FastAPI 0.113.0+ で利用可能
## 主な利点：
### 1. 構造化されたデータ管理
### 2. コードの再利用性
### 3. 型安全性とバリデーション
### 4. 自動ドキュメント化
### 5. 保守性の向上
## 注意：python-multipart のインストールが必要
# --------------------------------------------------

# 1. 基本的なフォームモデルの使用
class LoginForm(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[LoginForm, Form()]):
    """
    基本的なログインフォーム（Pydanticモデル使用）
    従来の個別Form()パラメータの代わりにモデル全体をフォームとして受信
    """
    # 実際の実装では認証処理
    if data.username == "admin" and data.password == "secret":
        return {
            "message": "Login successful",
            "username": data.username,
            "login_time": datetime.now().isoformat()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


# --------------------------------------------------
# 従来の方式との比較
# --------------------------------------------------

# 従来の方式：個別フィールド
@app.post("/login-old-style/")
async def login_old_style(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()]
):
    """従来の個別Form()パラメータを使用した方式"""
    return {"username": username, "method": "old_style"}

# 新しい方式：モデル使用（推奨）
@app.post("/login-new-style/")
async def login_new_style(data: Annotated[LoginForm, Form()]):
    """新しいPydanticモデルを使用した方式（推奨）"""
    return {"username": data.username, "method": "new_style"}


# --------------------------------------------------
# バリデーション付きフォームモデル
# --------------------------------------------------

# 2. 高度なバリデーション機能を持つフォームモデル
class UserRegistrationForm(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="ユーザー名（3-20文字）")
    email: str = Field(description="メールアドレス")
    password: str = Field(min_length=8, description="パスワード（8文字以上）")
    confirm_password: str = Field(description="パスワード確認")
    full_name: Union[str, None] = Field(None, max_length=100, description="フルネーム（オプション）")
    age: Union[int, None] = Field(None, ge=18, le=120, description="年齢（18-120歳、オプション）")
    newsletter: bool = Field(False, description="ニュースレター購読")
    
    @validator('email')
    def validate_email(cls, v):
        """簡単なメール形式チェック"""
        if "@" not in v or "." not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """パスワード確認"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

@app.post("/register/")
async def register_user(data: Annotated[UserRegistrationForm, Form()]):
    """
    ユーザー登録フォーム（高度なバリデーション付き）
    - Pydanticの全バリデーション機能を使用可能
    - カスタムバリデータでビジネスロジック実装
    """
    # 実際の実装では：
    # 1. ユーザー名重複チェック
    # 2. パスワードハッシュ化
    # 3. データベース保存
    
    return {
        "message": "User registered successfully",
        "user_data": {
            "username": data.username,
            "email": data.email,
            "full_name": data.full_name,
            "age": data.age,
            "newsletter": data.newsletter
        }
    }


# --------------------------------------------------
# 追加フィールド禁止機能（FastAPI 0.114.0+）
# --------------------------------------------------

# 3. 追加フィールドを禁止するフォームモデル
class StrictLoginForm(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}  # 追加フィールドを禁止

@app.post("/strict-login/")
async def strict_login(data: Annotated[StrictLoginForm, Form()]):
    """
    厳密なログインフォーム
    定義されていない追加フィールドが送信された場合、エラーを返す
    セキュリティ強化とデータ整合性保証
    """
    return {
        "message": "Strict login successful",
        "username": data.username
    }
# クライアントが extra フィールドを送信すると：
# {"detail": [{"type": "extra_forbidden", "loc": ["body", "extra"], 
#             "msg": "Extra inputs are not permitted", "input": "value"}]}


# --------------------------------------------------
# 複雑なフォームモデルの例
# --------------------------------------------------

# 4. 商品レビューフォームモデル
class ProductReviewForm(BaseModel):
    reviewer_name: str = Field(min_length=1, max_length=100)
    reviewer_email: str = Field(description="レビュアーのメールアドレス")
    rating: int = Field(ge=1, le=5, description="評価（1-5星）")
    title: str = Field(min_length=1, max_length=200, description="レビュータイトル")
    review_text: str = Field(min_length=10, max_length=2000, description="レビュー本文")
    recommend: bool = Field(False, description="この商品を推奨しますか？")
    verified_purchase: bool = Field(False, description="購入確認済み")
    
    @validator('reviewer_email')
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError('Invalid email format')
        return v

@app.post("/products/{product_id}/reviews/")
async def submit_review(
    product_id: int,
    review: Annotated[ProductReviewForm, Form()]
):
    """
    商品レビュー投稿フォーム
    複雑なバリデーションルールとビジネスロジックを含む
    """
    # 実際の実装では：
    # 1. 商品存在確認
    # 2. 重複レビューチェック
    # 3. データベース保存
    # 4. 商品評価再計算
    
    return {
        "message": "Review submitted successfully",
        "product_id": product_id,
        "review_id": 12345,
        "review_data": review.dict()
    }


# --------------------------------------------------
# 設定フォームの例
# --------------------------------------------------

# 5. ユーザー設定フォームモデル
class UserSettingsForm(BaseModel):
    display_name: Union[str, None] = Field(None, max_length=50)
    bio: Union[str, None] = Field(None, max_length=500)
    timezone: str = Field("UTC", description="タイムゾーン")
    language: str = Field("en", description="言語設定")
    email_notifications: bool = Field(True, description="メール通知")
    push_notifications: bool = Field(True, description="プッシュ通知")
    privacy_level: str = Field("public", description="プライバシーレベル")
    
    @validator('privacy_level')
    def validate_privacy_level(cls, v):
        allowed_levels = ["public", "friends", "private"]
        if v not in allowed_levels:
            raise ValueError(f'Privacy level must be one of: {allowed_levels}')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        # 簡単なタイムゾーン検証
        common_timezones = ["UTC", "JST", "EST", "PST", "GMT"]
        if v not in common_timezones:
            # 実際の実装ではpytzなどを使用してより厳密に検証
            pass
        return v

@app.put("/user/settings/")
async def update_user_settings(settings: Annotated[UserSettingsForm, Form()]):
    """
    ユーザー設定更新フォーム
    複数の設定項目を一度に更新
    """
    return {
        "message": "Settings updated successfully",
        "updated_settings": settings.dict(exclude_unset=True)
    }


# --------------------------------------------------
# ファイルアップロードと組み合わせた例（次章で詳細説明）
# --------------------------------------------------

# 6. プロフィール更新フォーム（将来のファイルアップロードとの組み合わせ例）
class ProfileUpdateForm(BaseModel):
    display_name: Union[str, None] = Field(None, max_length=50)
    bio: Union[str, None] = Field(None, max_length=200)
    website: Union[str, None] = Field(None, description="ウェブサイトURL")
    location: Union[str, None] = Field(None, max_length=100)
    
    @validator('website')
    def validate_website(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('Website URL must start with http:// or https://')
        return v

@app.put("/profile/")
async def update_profile(profile: Annotated[ProfileUpdateForm, Form()]):
    """
    プロフィール更新フォーム
    注意：実際のファイルアップロード（プロフィール画像など）は次章で説明
    """
    return {
        "message": "Profile updated successfully",
        "profile_data": profile.dict(exclude_unset=True)
    }


# --------------------------------------------------
# 動的フォームモデルの例
# --------------------------------------------------

# 7. 動的な設定項目を持つフォーム
class DynamicConfigForm(BaseModel):
    config_name: str = Field(min_length=1, max_length=100)
    config_value: str = Field(min_length=1)
    config_type: str = Field(description="設定の種類")
    is_public: bool = Field(False, description="公開設定")
    
    @validator('config_type')
    def validate_config_type(cls, v):
        allowed_types = ["string", "number", "boolean", "json"]
        if v not in allowed_types:
            raise ValueError(f'Config type must be one of: {allowed_types}')
        return v
    
    @validator('config_value')
    def validate_config_value(cls, v, values):
        """設定タイプに応じた値の検証"""
        if 'config_type' not in values:
            return v
            
        config_type = values['config_type']
        
        if config_type == "number":
            try:
                float(v)
            except ValueError:
                raise ValueError('Config value must be a valid number')
        elif config_type == "boolean":
            if v.lower() not in ["true", "false", "1", "0"]:
                raise ValueError('Config value must be a valid boolean')
        elif config_type == "json":
            import json
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Config value must be valid JSON')
        
        return v

@app.post("/config/")
async def create_config(config: Annotated[DynamicConfigForm, Form()]):
    """
    動的設定作成フォーム
    設定タイプに応じて値の検証を行う
    """
    return {
        "message": "Configuration created successfully",
        "config": config.dict()
    }


# --------------------------------------------------
# 重要なポイント
## 1. FastAPI 0.113.0+ で利用可能
## 2. 追加フィールド禁止は 0.114.0+ で利用可能
## 3. Pydanticの全機能（バリデーション、カスタムバリデータなど）を使用可能
## 4. 従来の個別Form()パラメータより構造化されて保守しやすい
## 5. 同じモデルを複数のエンドポイントで再利用可能
## 6. OpenAPI文書に構造化されたフォームとして表示
# --------------------------------------------------


# 8. フォームモデルの利点を示す比較例
class ContactForm(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=10, max_length=1000)
    phone: Union[str, None] = None
    company: Union[str, None] = None
    
    @validator('email')
    def validate_email(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError('Invalid email format')
        return v

# 同じモデルを複数のエンドポイントで再利用
@app.post("/contact/")
async def submit_contact_form(contact: Annotated[ContactForm, Form()]):
    """お問い合わせフォーム投稿"""
    return {"message": "Contact form submitted", "contact_id": 123}

@app.post("/support/")
async def submit_support_request(contact: Annotated[ContactForm, Form()]):
    """サポートリクエスト投稿（同じフォーム構造）"""
    return {"message": "Support request submitted", "ticket_id": 456}

# モデルの再利用により、一貫性のあるAPI設計と保守性を実現