from typing import Union
from fastapi import FastAPI, Path, Query

app = FastAPI()


# --------------------------------------------------
# メタデータ（metadata）とは？
## データに対するデータ：title、description、exampleなど
## 用途：
### - Swagger UIのAPI文書自動生成
### - 開発者ガイド（他の開発者が参考可能）
### - コードの可読性向上
# --------------------------------------------------


# パスパラメータとメタデータの基本例
@app.get("/items/{item_id}")
async def read_items_with_metadata(
    item_id: int = Path(title="取得するアイテムのID"),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    """
    item_idというパラメータにメタデータを設定
    パスパラメータは経路の一部のため常に必須
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# --------------------------------------------------
# パラメータの順序について
## Python文法規則上、デフォルト値がある変数は後に来る必要がある
# --------------------------------------------------

# ❌ Python でエラーが発生する例
# def my_function(item_id: int = Path(), q: str):  # デフォルト値があるものが前に来るとダメ
#     pass

# ✅ 解決方法1: 順序を変更
@app.get("/items1/{item_id}")
async def read_item_reordered(q: str, item_id: int = Path(title="アイテムID")):
    """順序を変更してデフォルト値なしのパラメータを先に配置"""
    return {"item_id": item_id, "q": q}


# ✅ 解決方法2: すべてのパラメータにデフォルト値を設定
@app.get("/items2/{item_id}")
async def read_item_all_defaults(
    item_id: int = Path(title="アイテムID"), 
    q: str = Query(title="検索クエリ")
):
    """すべてのパラメータにデフォルト値を設定"""
    return {"item_id": item_id, "q": q}


# ✅ 解決方法3: * を使用（キーワード専用引数）
@app.get("/items3/{item_id}")
async def read_item_keyword_only(*, item_id: int = Path(title="アイテムID"), q: str):
    """
    * を使用してキーワード専用引数にする
    FastAPIはパラメータ名と定義を見て自動処理するため順序を気にする必要なし
    """
    return {"item_id": item_id, "q": q}


# --------------------------------------------------
# 数値検証
## item_idを1以上の数に制限したい場合、ge（greater equal）を設定可能
# --------------------------------------------------

# 基本的な数値検証（1以上）
@app.get("/validated-items/{item_id}")
async def read_validated_items(
    *, 
    item_id: int = Path(title="取得するアイテムのID", ge=1), 
    q: str
):
    """
    item_idを1以上の値に制限
    ge = greater or equal（以上）
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# 複数の数値検証を組み合わせた例
@app.get("/advanced-items/{item_id}")
async def read_advanced_items(
    *,
    item_id: int = Path(
        title="アイテムID",
        description="1以上1000以下のアイテムID",
        ge=1,
        le=1000
    ),
    size: float = Query(
        title="サイズ",
        description="0より大きく100未満のサイズ",
        gt=0,
        lt=100
    )
):
    """
    複数の数値検証キーワード：
    - gt: より大きい（greater than）
    - ge: 以上（greater or equal）
    - lt: より小さい（less than）
    - le: 以下（less or equal）
    
    float型にも数値検証が適用可能（例：lt=10.5）
    """
    return {
        "item_id": item_id,
        "size": size,
        "message": f"アイテム{item_id}のサイズは{size}です"
    }


# 実用的な例：ページネーション
@app.get("/products/{category_id}")
async def get_products_by_category(
    *,
    category_id: int = Path(
        title="カテゴリID", 
        description="商品カテゴリのID（1以上）",
        ge=1
    ),
    page: int = Query(
        default=1,
        title="ページ番号",
        description="表示するページ番号（1以上）",
        ge=1
    ),
    per_page: int = Query(
        default=10,
        title="1ページあたりの件数",
        description="1ページに表示する商品数（1以上100以下）",
        ge=1,
        le=100
    )
):
    """
    実用的なページネーション例
    カテゴリIDは必須のパスパラメータ
    ページ番号と1ページあたりの件数はオプションのクエリパラメータ
    """
    return {
        "category_id": category_id,
        "page": page,
        "per_page": per_page,
        "message": f"カテゴリ{category_id}の商品一覧（{page}ページ目、{per_page}件表示）"
    }