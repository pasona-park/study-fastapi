from typing import Annotated, Union, List
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
from pathlib import Path
import uuid

app = FastAPI()

# --------------------------------------------------
# フォームとファイルの同時リクエスト（Request Forms and Files）
## 一つのリクエストでファイルとフォームデータを同時に受信する機能
## 実際のWebアプリケーションでよく使用されるパターン
## 主な用途：
### 1. プロフィール更新（ユーザー情報 + プロフィール画像）
### 2. 商品登録（商品情報 + 商品画像）
### 3. ドキュメント提出（メタデータ + 添付ファイル）
### 4. 投稿作成（テキスト内容 + 画像/ファイル）
## 注意：python-multipart のインストールが必要
# --------------------------------------------------

# 1. 基本的なフォーム + ファイルの組み合わせ
@app.post("/files/")
async def create_file(
    file: bytes = File(),           # 小さなファイル用
    fileb: UploadFile = File(),     # 大容量ファイル用
    token: str = Form()             # フォームデータ
):
    """
    基本的なフォーム + ファイルの同時受信
    - bytes と UploadFile を混在使用可能
    - フォームフィールドと組み合わせ
    - multipart/form-data でエンコード
    """
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
        "fileb_filename": fileb.filename
    }


# --------------------------------------------------
# 実戦的な例：ユーザープロフィール更新
# --------------------------------------------------

# 2. プロフィール更新（情報 + 画像）
@app.post("/users/{user_id}/profile/")
async def update_user_profile(
    user_id: int,
    # フォームデータ
    display_name: Annotated[str, Form(min_length=1, max_length=50)],
    bio: Annotated[Union[str, None], Form(max_length=500)] = None,
    website: Annotated[Union[str, None], Form()] = None,
    location: Annotated[Union[str, None], Form(max_length=100)] = None,
    # ファイルデータ
    profile_image: Annotated[Union[UploadFile, None], File()] = None,
    cover_image: Annotated[Union[UploadFile, None], File()] = None
):
    """
    ユーザープロフィール更新
    - フォームデータ：表示名、自己紹介、ウェブサイト、場所
    - ファイルデータ：プロフィール画像、カバー画像（オプション）
    """
    # プロフィール情報の更新
    profile_data = {
        "user_id": user_id,
        "display_name": display_name,
        "bio": bio,
        "website": website,
        "location": location
    }
    
    # 画像ファイルの処理
    uploaded_images = {}
    
    if profile_image and profile_image.filename:
        # プロフィール画像の検証と処理
        if not profile_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile image must be an image file"
            )
        
        contents = await profile_image.read()
        uploaded_images["profile_image"] = {
            "filename": profile_image.filename,
            "content_type": profile_image.content_type,
            "size": len(contents)
        }
    
    if cover_image and cover_image.filename:
        # カバー画像の検証と処理
        if not cover_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cover image must be an image file"
            )
        
        contents = await cover_image.read()
        uploaded_images["cover_image"] = {
            "filename": cover_image.filename,
            "content_type": cover_image.content_type,
            "size": len(contents)
        }
    
    return {
        "message": "Profile updated successfully",
        "profile_data": profile_data,
        "uploaded_images": uploaded_images
    }


# --------------------------------------------------
# 商品登録の例
# --------------------------------------------------

# 3. 商品登録（商品情報 + 複数画像）
@app.post("/products/")
async def create_product(
    # 商品基本情報
    name: Annotated[str, Form(min_length=1, max_length=200)],
    description: Annotated[str, Form(min_length=10, max_length=2000)],
    price: Annotated[float, Form(gt=0)],
    category: Annotated[str, Form()],
    brand: Annotated[Union[str, None], Form()] = None,
    # 在庫・配送情報
    stock_quantity: Annotated[int, Form(ge=0)] = 0,
    weight: Annotated[Union[float, None], Form(gt=0)] = None,
    # 商品画像（複数）
    images: List[UploadFile] = File(...),
    # 商品マニュアル（オプション）
    manual: Annotated[Union[UploadFile, None], File()] = None
):
    """
    商品登録
    - 基本情報：名前、説明、価格、カテゴリなど
    - 画像：複数の商品画像（必須）
    - マニュアル：PDF等のドキュメント（オプション）
    """
    # 画像ファイルの検証
    if not images or all(not img.filename for img in images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one product image is required"
        )
    
    # 商品基本情報
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "brand": brand,
        "stock_quantity": stock_quantity,
        "weight": weight
    }
    
    # 画像処理
    processed_images = []
    for i, image in enumerate(images):
        if image.filename:
            # 画像ファイルタイプチェック
            if not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {image.filename} is not an image"
                )
            
            contents = await image.read()
            processed_images.append({
                "order": i + 1,
                "filename": image.filename,
                "content_type": image.content_type,
                "size": len(contents)
            })
    
    # マニュアル処理
    manual_info = None
    if manual and manual.filename:
        # PDFファイルチェック（簡単な例）
        if manual.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manual must be a PDF file"
            )
        
        contents = await manual.read()
        manual_info = {
            "filename": manual.filename,
            "content_type": manual.content_type,
            "size": len(contents)
        }
    
    return {
        "message": "Product created successfully",
        "product_id": 12345,  # 実際の実装ではDBから取得
        "product_data": product_data,
        "images": processed_images,
        "manual": manual_info
    }


# --------------------------------------------------
# ブログ投稿の例
# --------------------------------------------------

# 4. ブログ投稿作成（記事内容 + 添付ファイル）
@app.post("/blog/posts/")
async def create_blog_post(
    # 記事基本情報
    title: Annotated[str, Form(min_length=1, max_length=200)],
    content: Annotated[str, Form(min_length=10)],
    summary: Annotated[Union[str, None], Form(max_length=500)] = None,
    tags: Annotated[Union[str, None], Form()] = None,  # カンマ区切り
    # 公開設定
    is_published: Annotated[bool, Form()] = False,
    publish_date: Annotated[Union[str, None], Form()] = None,
    # 添付ファイル
    featured_image: Annotated[Union[UploadFile, None], File()] = None,
    attachments: List[UploadFile] = File(default=[])
):
    """
    ブログ投稿作成
    - 記事情報：タイトル、内容、要約、タグ
    - 公開設定：公開フラグ、公開日時
    - ファイル：アイキャッチ画像、添付ファイル
    """
    # 記事データ
    post_data = {
        "title": title,
        "content": content,
        "summary": summary,
        "tags": tags.split(",") if tags else [],
        "is_published": is_published,
        "publish_date": publish_date
    }
    
    # アイキャッチ画像処理
    featured_image_info = None
    if featured_image and featured_image.filename:
        if not featured_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Featured image must be an image file"
            )
        
        contents = await featured_image.read()
        featured_image_info = {
            "filename": featured_image.filename,
            "content_type": featured_image.content_type,
            "size": len(contents)
        }
    
    # 添付ファイル処理
    processed_attachments = []
    for attachment in attachments:
        if attachment.filename:
            contents = await attachment.read()
            
            # ファイルサイズ制限（例：10MB）
            max_size = 10 * 1024 * 1024
            if len(contents) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File {attachment.filename} exceeds size limit"
                )
            
            processed_attachments.append({
                "filename": attachment.filename,
                "content_type": attachment.content_type,
                "size": len(contents)
            })
    
    return {
        "message": "Blog post created successfully",
        "post_id": 67890,
        "post_data": post_data,
        "featured_image": featured_image_info,
        "attachments": processed_attachments
    }


# --------------------------------------------------
# 複雑な例：求人応募フォーム
# --------------------------------------------------

# 5. 求人応募フォーム（個人情報 + 履歴書 + ポートフォリオ）
@app.post("/jobs/{job_id}/applications/")
async def submit_job_application(
    job_id: int,
    # 個人情報
    full_name: Annotated[str, Form(min_length=1, max_length=100)],
    email: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    # 職歴情報
    current_position: Annotated[Union[str, None], Form()] = None,
    years_of_experience: Annotated[int, Form(ge=0)] = 0,
    expected_salary: Annotated[Union[float, None], Form(gt=0)] = None,
    # 自由記述
    cover_letter: Annotated[Union[str, None], Form(max_length=2000)] = None,
    # 必須ファイル
    resume: UploadFile = File(...),  # 履歴書（必須）
    # オプションファイル
    portfolio: Annotated[Union[UploadFile, None], File()] = None,
    certificates: List[UploadFile] = File(default=[])  # 資格証明書
):
    """
    求人応募フォーム
    - 個人情報：氏名、連絡先
    - 職歴情報：現職、経験年数、希望給与
    - 必須ファイル：履歴書
    - オプションファイル：ポートフォリオ、資格証明書
    """
    # 履歴書ファイルチェック（必須）
    if not resume.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file is required"
        )
    
    # 履歴書ファイルタイプチェック
    allowed_resume_types = ["application/pdf", "application/msword", 
                           "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if resume.content_type not in allowed_resume_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be PDF or Word document"
        )
    
    # 応募者情報
    applicant_data = {
        "job_id": job_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "current_position": current_position,
        "years_of_experience": years_of_experience,
        "expected_salary": expected_salary,
        "cover_letter": cover_letter
    }
    
    # 履歴書処理
    resume_contents = await resume.read()
    resume_info = {
        "filename": resume.filename,
        "content_type": resume.content_type,
        "size": len(resume_contents)
    }
    
    # ポートフォリオ処理
    portfolio_info = None
    if portfolio and portfolio.filename:
        portfolio_contents = await portfolio.read()
        portfolio_info = {
            "filename": portfolio.filename,
            "content_type": portfolio.content_type,
            "size": len(portfolio_contents)
        }
    
    # 資格証明書処理
    processed_certificates = []
    for cert in certificates:
        if cert.filename:
            cert_contents = await cert.read()
            processed_certificates.append({
                "filename": cert.filename,
                "content_type": cert.content_type,
                "size": len(cert_contents)
            })
    
    return {
        "message": "Job application submitted successfully",
        "application_id": str(uuid.uuid4()),
        "applicant_data": applicant_data,
        "resume": resume_info,
        "portfolio": portfolio_info,
        "certificates": processed_certificates
    }


# --------------------------------------------------
# テスト用HTMLフォーム
# --------------------------------------------------

# 6. フォーム + ファイルテスト用のHTMLページ
@app.get("/", response_class=HTMLResponse)
async def form_and_file_test():
    """
    フォーム + ファイル同時送信テスト用のHTMLページ
    """
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Form and File Upload Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .form-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 3px; }
            input[type="submit"] { width: auto; background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            input[type="file"] { padding: 3px; }
        </style>
    </head>
    <body>
        <h1>FastAPI Form + File Upload Test</h1>
        
        <div class="form-section">
            <h3>Basic Form + File</h3>
            <form action="/files/" enctype="multipart/form-data" method="post">
                <div class="form-group">
                    <label>Token:</label>
                    <input name="token" type="text" required>
                </div>
                <div class="form-group">
                    <label>File (bytes):</label>
                    <input name="file" type="file" required>
                </div>
                <div class="form-group">
                    <label>File (UploadFile):</label>
                    <input name="fileb" type="file" required>
                </div>
                <input type="submit" value="Submit Basic Form">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Profile Update</h3>
            <form action="/users/123/profile/" enctype="multipart/form-data" method="post">
                <div class="form-group">
                    <label>Display Name:</label>
                    <input name="display_name" type="text" required>
                </div>
                <div class="form-group">
                    <label>Bio:</label>
                    <textarea name="bio" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>Website:</label>
                    <input name="website" type="url">
                </div>
                <div class="form-group">
                    <label>Location:</label>
                    <input name="location" type="text">
                </div>
                <div class="form-group">
                    <label>Profile Image:</label>
                    <input name="profile_image" type="file" accept="image/*">
                </div>
                <div class="form-group">
                    <label>Cover Image:</label>
                    <input name="cover_image" type="file" accept="image/*">
                </div>
                <input type="submit" value="Update Profile">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Product Registration</h3>
            <form action="/products/" enctype="multipart/form-data" method="post">
                <div class="form-group">
                    <label>Product Name:</label>
                    <input name="name" type="text" required>
                </div>
                <div class="form-group">
                    <label>Description:</label>
                    <textarea name="description" rows="4" required></textarea>
                </div>
                <div class="form-group">
                    <label>Price:</label>
                    <input name="price" type="number" step="0.01" required>
                </div>
                <div class="form-group">
                    <label>Category:</label>
                    <input name="category" type="text" required>
                </div>
                <div class="form-group">
                    <label>Brand:</label>
                    <input name="brand" type="text">
                </div>
                <div class="form-group">
                    <label>Stock Quantity:</label>
                    <input name="stock_quantity" type="number" value="0">
                </div>
                <div class="form-group">
                    <label>Product Images:</label>
                    <input name="images" type="file" accept="image/*" multiple required>
                </div>
                <div class="form-group">
                    <label>Manual (PDF):</label>
                    <input name="manual" type="file" accept=".pdf">
                </div>
                <input type="submit" value="Register Product">
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)


# --------------------------------------------------
# 重要なポイント
## 1. File と Form を同時に使用可能
## 2. Body（JSON）との同時使用は不可（HTTP制限）
## 3. multipart/form-data でエンコード
## 4. bytes と UploadFile を混在使用可能
## 5. 複数ファイルとフォームフィールドの組み合わせ可能
## 6. 実際のWebフォームと同じ動作
## 7. バリデーション機能をフル活用可能
# --------------------------------------------------