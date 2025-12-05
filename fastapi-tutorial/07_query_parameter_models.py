from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


# --------------------------------------------------
# クエリパラメータモデル
## クエリパラメータをPydanticモデル内で宣言し、モデルをQueryとして宣言することが可能
# --------------------------------------------------

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items_with_filter(filter_query: Annotated[FilterParams, Query()]):
    return {
        "filter_params": filter_query,
        "message": f"検索条件: limit={filter_query.limit}, offset={filter_query.offset}"
    }
# クエリパラメータをPydanticモデルで管理
## /docsでlimit、offset、order_by、tagsの4つのパラメータが表示される

# Annotatedの説明：
## - タイプヒント機能で、タイプに追加情報（メタデータ）を添付
## - パラメータがどのように処理されるかを指示

# filter_query: Annotated[FilterParams, Query()]の意味：
## - FilterParams: 実際のデータタイプ
## - Query(): FastAPIにこのパラメータをクエリパラメータとして処理するよう指示


# --------------------------------------------------
# 追加クエリパラメータ禁止
## 許可するクエリパラメータを制限する必要がある場合（あまり一般的ではない）
## Pydanticモデル設定でextraフィールドをforbidに設定
# --------------------------------------------------

class StrictFilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/strict-items/")
async def read_strict_items(filter_query: Annotated[StrictFilterParams, Query()]):
    return {
        "filter_params": filter_query,
        "message": "厳密なフィルタリングが適用されました"
    }
# 追加クエリパラメータを禁止する例
## /strict-items/?limit=10&tool=plumbus のように
## 追加クエリパラメータを送信しようとすると許可しないエラーが発生


class ProductSearchParams(BaseModel):
    category: str = Field("all", description="商品カテゴリ")
    min_price: int = Field(0, ge=0, description="最低価格")
    max_price: int = Field(10000, ge=0, le=100000, description="最高価格")
    in_stock: bool = Field(True, description="在庫ありのみ")
    sort_by: Literal["price", "name", "rating"] = "name"
    page: int = Field(1, ge=1, description="ページ番号")
    per_page: int = Field(20, ge=1, le=100, description="1ページあたりの件数")


@app.get("/products/search/")
async def search_products(search_params: Annotated[ProductSearchParams, Query()]):
    return {
        "search_conditions": search_params,
        "results": f"カテゴリ'{search_params.category}'で価格{search_params.min_price}円〜{search_params.max_price}円の商品を検索",
        "pagination": f"ページ{search_params.page}（{search_params.per_page}件表示）"
    }
# 実用的な商品検索API
# 複数の検索条件をPydanticモデルで管理


class DateRange(BaseModel):
    start_date: str = Field("2024-01-01", description="開始日（YYYY-MM-DD）")
    end_date: str = Field("2024-12-31", description="終了日（YYYY-MM-DD）")

class AdvancedFilterParams(BaseModel):
    basic_filter: str = Field("", description="基本検索キーワード")
    date_range: DateRange = DateRange()
    status: list[Literal["active", "inactive", "pending"]] = ["active"]

@app.get("/advanced-search/")
async def advanced_search(filters: Annotated[AdvancedFilterParams, Query()]):
    return {
        "advanced_filters": filters,
        "message": "高度な検索条件が適用されました"
    }
# ネストしたモデルを使用した高度な検索
# 注意：ネストしたオブジェクトはクエリパラメータでは制限がある