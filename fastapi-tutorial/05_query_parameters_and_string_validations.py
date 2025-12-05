from typing import Union
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/basic/")
async def read_basic(q: Union[str, None] = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# パラメータqは文字列だけど、オプショナルなためNoneも許容
# Query関数を使って、qの最大長を50に制限している（max_length）
## min_lengthで最小長も指定可能


# --------------------------------------------------
# Query関数とは？
## FastAPIでクエリパラメータの詳細な設定を行うための関数

## 提供機能
### 1. 検証：max_length, min_length, patternなどのバリデーションルールを設定可能
### 2. デフォルト値の設定：default=Noneはオプショナル、default=は必須パラメータ
### 3. メタデータの追加：title, descriptionなどのドキュメント用メタデータを追加可能
### 4. その他の制約：gt（greater than）, lt（less than）
### 5. 正規表現検証：patternパラメータで文字列形式を制限可能
# --------------------------------------------------


@app.get("/regex/")
async def read_regex(
    q: Union[str, None] = Query(
        default=None, min_length=3, max_length=50, pattern="^fixedquery$"  # 正規表現パターン
    ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# 現在のパターン解析: "^fixedquery$"
## ^ : 文字列の開始を意味
## fixedquery : 正確にこの文字列が順序通りに存在する必要がある
## $ : 文字列の終了を意味
## → つまり、正確に "fixedquery" という文字列のみ許可

# 実行結果例
## http://127.0.0.1:8000/regex/?q=fixedquery
## → {"items":[{"item_id":"Foo"},{"item_id":"Bar"}],"q":"fixedquery"}
## http://127.0.0.1:8000/regex/
## → {"items":[{"item_id":"Foo"},{"item_id":"Bar"}]} (qがないため if q が実行されない)


# --------------------------------------------------
# 正規表現（Regular Expression = regex）の詳細
# --------------------------------------------------
## 正規表現とは？
### 文字列のパターンを表現する特別な文法
### 特定の規則を持つ文字列を検索や検証する際に使用

## その他の正規表現例
### 数字のみ許可（3桁）
# pattern="^[0-9]{3}$"  # "123" ✅, "12" ❌, "abc" ❌

### メールアドレス形式（簡単版）
# pattern="^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$"

### 電話番号（010-1234-5678形式）
# pattern="^010-[0-9]{4}-[0-9]{4}$"
# --------------------------------------------------


# --------------------------------------------------
# 必須Queryパラメータ作成
# --------------------------------------------------

# 1. デフォルト値を設定しない
@app.get("/required1/")
async def read_required1(q: str):  # デフォルト値なし = 必須
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"q": q})
    return results

# 2. Query()でデフォルト値を省略、制限追加
@app.get("/required2/")
async def read_required2(q: str = Query(min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"q": q})
    return results

# 3. ...を使った明示的必須宣言
@app.get("/required3/")
async def read_required3(q: str = Query(..., min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"q": q})
    return results


# --------------------------------------------------
# クエリパラメータリスト / 複数値
# --------------------------------------------------
from typing import List

# 複数の値を受け取るクエリパラメータ
@app.get("/list/")
async def read_list(q: Union[List[str], None] = Query(default=None)):
    query_items = {"q": q}
    return query_items
# 使用例: /list/?q=foo&q=bar
# 結果: {"q": ["foo", "bar"]}
# /docsでも複数パラメータ入力可能

# デフォルト値をリストで指定
@app.get("/list-default/")
async def read_list_default(q: List[str] = Query(default=["foo", "bar"])):
    query_items = {"q": q}
    return query_items

# List[str]の代わりにlistを直接使用も可能
@app.get("/list-simple/")
async def read_list_simple(q: list = Query(default=[])):
    query_items = {"q": q}
    return query_items


# --------------------------------------------------
# メタデータの追加
# --------------------------------------------------

@app.get("/metadata/")
async def read_metadata(
    q: Union[str, None] = Query(
        default=None,
        title="検索クエリ",
        description="データベース内のアイテムを検索するためのクエリ文字列",
        min_length=3,
    ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# titleとdescriptionがAPI仕様書に表示される


# --------------------------------------------------
# エイリアス（別名）パラメータ
# --------------------------------------------------

@app.get("/alias/")
async def read_alias(q: Union[str, None] = Query(default=None, alias="item-query")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# 使用例: /alias/?item-query=foo
# Pythonでは無効な変数名（item-query）をURLパラメータとして使用可能


# --------------------------------------------------
# 非推奨（deprecated）パラメータ
# --------------------------------------------------

@app.get("/deprecated/")
async def read_deprecated(
    q: Union[str, None] = Query(
        default=None,
        alias="item-query",
        title="検索クエリ",
        description="データベース内のアイテムを検索するためのクエリ文字列",
        min_length=3,
        max_length=50,
        pattern="^fixedquery$",
        deprecated=True,  # 非推奨マーク
    ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
# /docsで非推奨として表示される
# 既存のコードとの互換性を保ちながら、将来的に削除予定であることを明示