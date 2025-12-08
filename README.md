FastAPI学習用リポジトリ

## 📖 概要
FastAPI公式チュートリアル（https://fastapi.tiangolo.com/tutorial/）を参考に学習した内容を、機能別にファイルを分けて整理しています。

## 📁 プロジェクト構成
```
fastapi-tutorial/
  └── 01_basic_routing.py                      # 基本ルーティング
  └── 02_path_parameters.py                    # パスパラメータ
  └── 03_query_parameters.py                   # クエリパラメータ
  └── 04_request_body.py                       # リクエストボディ
  └── 05_query_parameters_and_string_validations.py  # クエリパラメータと文字列検証
  └── 06_path_parameters_and_numeric_validations.py  # パスパラメータと数値検証
  └── 07_query_parameter_models.py             # クエリパラメータモデル
  └── 08_body_multiple_parameters.py           # ボディ - 複数パラメータ
  └── 09_body_fields.py                        # ボディ - フィールド
  └── 10_body_nested_models.py                 # ボディ - ネストされたモデル
  └── 11_declare_request_example_data.py       # リクエスト例データの宣言
  └── 12_extra_data_types.py                   # 追加データ型
  └── 13_cookie_parameters.py                  # クッキーパラメータ
  └── 14_header_parameters.py                  # ヘッダーパラメータ
  └── 15_cookie_parameter_models.py            # クッキーパラメータモデル
  └── 16_header_parameter_models.py            # ヘッダーパラメータモデル

sqlalchemy/
  └── 01_crud.py    # SQL AlchemyのCRUDテスト実行
```

## 実行方法
各ファイルを以下のコマンドで実行できます：
```
uvicorn {ファイル名}:app --reload  
```
※ ファイル名は拡張子(.py)を除いて指定してください

**実行例：**
```bash
uvicorn 01_basic_routing:app --reload
uvicorn 02_path_parameters:app --reload
```