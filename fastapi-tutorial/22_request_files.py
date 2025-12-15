from typing import Annotated, Union, List
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse
import shutil
import os
from pathlib import Path

app = FastAPI()

# --------------------------------------------------
# ファイルアップロード（Request Files）
## クライアントがサーバーにファイルを送信する機能
## FastAPIでは File と UploadFile を使用してファイルアップロードを処理
## 主な用途：
### 1. 画像アップロード（プロフィール写真、商品画像など）
### 2. ドキュメントアップロード（PDF、Word文書など）
### 3. 大容量ファイル処理（動画、圧縮ファイルなど）
### 4. バッチアップロード（複数ファイル同時処理）
## 注意：python-multipart のインストールが必要
# --------------------------------------------------

# 1. 基本的なファイルアップロード - bytes方式
@app.post("/files/")
async def create_file(file: bytes = File()):
    """
    小さなファイル用のアップロード（bytes方式）
    - ファイル全体がメモリに保存される
    - 小さなファイルに適している
    - ファイルサイズの制限に注意
    """
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
    
    return {
        "file_size": len(file),
        "message": f"Received file of {len(file)} bytes"
    }


# 2. 推奨方式 - UploadFile
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    """
    大容量ファイル用のアップロード（UploadFile方式）推奨
    - スプールファイルを使用（メモリ効率的）
    - メタデータ取得可能
    - 非同期インターフェース
    - 他のライブラリとの互換性
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    # ファイル内容を読み取り
    contents = await file.read()
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(contents),
        "message": f"Successfully uploaded {file.filename}"
    }


# --------------------------------------------------
# UploadFileの詳細な使用例
# --------------------------------------------------

# 3. UploadFileの属性とメソッドの活用
@app.post("/file-info/")
async def get_file_info(file: UploadFile):
    """
    UploadFileの全属性とメソッドを活用した例
    - filename: ファイル名
    - content_type: MIMEタイプ
    - file: SpooledTemporaryFileオブジェクト
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # ファイルの先頭に移動
    await file.seek(0)
    
    # ファイル内容を読み取り
    contents = await file.read()
    
    # 再度先頭に移動（必要に応じて）
    await file.seek(0)
    
    # ファイル情報を詳細に取得
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(contents),
        "file_extension": Path(file.filename).suffix,
        "file_stem": Path(file.filename).stem
    }
    
    return file_info


# --------------------------------------------------
# ファイル保存の例
# --------------------------------------------------

# 4. ファイルをディスクに保存
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/save-file/")
async def save_file(file: UploadFile):
    """
    アップロードされたファイルをディスクに保存
    実際のアプリケーションでは：
    - ファイル名の重複チェック
    - ファイルタイプの検証
    - ウイルススキャン
    - ファイルサイズ制限
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # 安全なファイル名の生成（実際の実装ではより厳密に）
    safe_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    try:
        # ファイルを保存
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "File saved successfully",
            "filename": safe_filename,
            "file_path": file_path,
            "file_size": os.path.getsize(file_path)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )


# --------------------------------------------------
# ファイルタイプの検証
# --------------------------------------------------

# 5. 画像ファイルのみ許可する例
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload-image/")
async def upload_image(file: UploadFile):
    """
    画像ファイルのみを受け入れるアップロード
    - ファイルタイプ検証
    - ファイルサイズ制限
    - 画像形式チェック
    """
    # ファイルが選択されているかチェック
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    # ファイルタイプチェック
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed types: {ALLOWED_IMAGE_TYPES}"
        )
    
    # ファイル内容を読み取り
    contents = await file.read()
    
    # ファイルサイズチェック
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {len(contents)} exceeds maximum allowed size {MAX_FILE_SIZE}"
        )
    
    # 実際の実装では画像処理ライブラリ（Pillow等）で詳細検証
    
    return {
        "message": "Image uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(contents)
    }


# --------------------------------------------------
# 複数ファイルアップロード
# --------------------------------------------------

# 6. 複数ファイルの同時アップロード - bytes方式
@app.post("/files/multiple/")
async def create_files(files: List[bytes] = File()):
    """
    複数ファイルの同時アップロード（bytes方式）
    小さなファイル群に適している
    """
    if not files or all(len(file) == 0 for file in files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )
    
    file_sizes = [len(file) for file in files]
    total_size = sum(file_sizes)
    
    return {
        "files_count": len(files),
        "file_sizes": file_sizes,
        "total_size": total_size,
        "message": f"Received {len(files)} files with total size {total_size} bytes"
    }


# 7. 複数ファイルの同時アップロード - UploadFile方式（推奨）
@app.post("/uploadfiles/multiple/")
async def create_upload_files(files: List[UploadFile]):
    """
    複数ファイルの同時アップロード（UploadFile方式）推奨
    大容量ファイル群や混合ファイルタイプに適している
    """
    if not files or all(not file.filename for file in files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files selected"
        )
    
    file_info_list = []
    total_size = 0
    
    for file in files:
        if file.filename:  # ファイルが選択されている場合のみ処理
            contents = await file.read()
            file_size = len(contents)
            total_size += file_size
            
            file_info_list.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file_size
            })
            
            # ファイルポインタを先頭に戻す（必要に応じて）
            await file.seek(0)
    
    return {
        "files_count": len(file_info_list),
        "files_info": file_info_list,
        "total_size": total_size,
        "message": f"Successfully processed {len(file_info_list)} files"
    }


# --------------------------------------------------
# 実戦的な例：プロフィール画像アップロード
# --------------------------------------------------

# 8. プロフィール画像アップロードの完全な例
@app.post("/users/{user_id}/profile-image/")
async def upload_profile_image(user_id: int, file: UploadFile):
    """
    ユーザープロフィール画像アップロード
    実際のアプリケーションレベルの実装例
    """
    # ファイル選択チェック
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file selected"
        )
    
    # 画像ファイルタイプチェック
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # ファイル内容読み取り
    contents = await file.read()
    
    # ファイルサイズチェック
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image file too large"
        )
    
    # 実際の実装では：
    # 1. ユーザー存在確認
    # 2. 既存プロフィール画像削除
    # 3. 画像リサイズ・最適化
    # 4. ファイル名生成（UUID等）
    # 5. クラウドストレージ保存
    # 6. データベース更新
    
    # ユニークなファイル名生成（簡単な例）
    import uuid
    file_extension = Path(file.filename).suffix
    unique_filename = f"profile_{user_id}_{uuid.uuid4()}{file_extension}"
    
    return {
        "message": "Profile image uploaded successfully",
        "user_id": user_id,
        "filename": unique_filename,
        "content_type": file.content_type,
        "file_size": len(contents),
        "image_url": f"/static/profiles/{unique_filename}"  # 実際のURL
    }


# --------------------------------------------------
# ファイルアップロード用のHTMLフォーム（テスト用）
# --------------------------------------------------

# 9. ファイルアップロードテスト用のHTMLページ
@app.get("/", response_class=HTMLResponse)
async def upload_form():
    """
    ファイルアップロードテスト用のHTMLフォーム
    開発・テスト時に便利
    """
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Upload Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .form-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
            input[type="file"] { margin: 10px 0; }
            input[type="submit"] { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>FastAPI File Upload Test</h1>
        
        <div class="form-section">
            <h3>Single File Upload (bytes)</h3>
            <form action="/files/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" required>
                <input type="submit" value="Upload File (bytes)">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Single File Upload (UploadFile)</h3>
            <form action="/uploadfile/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" required>
                <input type="submit" value="Upload File (UploadFile)">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Multiple Files Upload</h3>
            <form action="/uploadfiles/multiple/" enctype="multipart/form-data" method="post">
                <input name="files" type="file" multiple required>
                <input type="submit" value="Upload Multiple Files">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Image Upload Only</h3>
            <form action="/upload-image/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept="image/*" required>
                <input type="submit" value="Upload Image">
            </form>
        </div>
        
        <div class="form-section">
            <h3>Profile Image Upload</h3>
            <form action="/users/123/profile-image/" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept="image/*" required>
                <input type="submit" value="Upload Profile Image">
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)


# --------------------------------------------------
# 重要なポイント
## 1. python-multipart のインストールが必要
## 2. 大容量ファイルには UploadFile を使用（推奨）
## 3. ファイルは "multipart/form-data" でエンコード
## 4. File と Form を同時使用可能、Body との同時使用は不可
## 5. 全ファイルメソッドは非同期（await が必要）
## 6. セキュリティ：ファイルタイプ・サイズ検証必須
## 7. メタデータ活用でファイル管理を効率化
# --------------------------------------------------


# 10. エラーハンドリングの例
@app.post("/secure-upload/")
async def secure_file_upload(file: UploadFile):
    """
    セキュアなファイルアップロードの例
    包括的なエラーハンドリングとセキュリティチェック
    """
    try:
        # 基本チェック
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        # ファイル拡張子チェック
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".docx"}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {file_extension} not allowed"
            )
        
        # ファイル内容読み取り
        contents = await file.read()
        
        # 空ファイルチェック
        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file not allowed"
            )
        
        # ファイルサイズチェック
        max_size = 10 * 1024 * 1024  # 10MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {max_size} bytes"
            )
        
        # 実際の実装では：
        # - ウイルススキャン
        # - ファイル内容の詳細検証
        # - 重複ファイルチェック
        # - データベース記録
        
        return {
            "message": "File uploaded securely",
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(contents),
            "file_extension": file_extension
        }
        
    except HTTPException:
        # HTTPExceptionは再発生
        raise
    except Exception as e:
        # その他のエラーは500エラーとして処理
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )