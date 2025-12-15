FastAPI学習用

## 📖 概要
FastAPI公式チュートリアル（https://fastapi.tiangolo.com/tutorial/）を参考に学習した内容を、内容別にファイルを分けて整理しています。

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
  └── 17_response_model_return_type.py         # レスポンスモデル戻り値型
  └── 18_extra_models.py                       # 追加モデル
  └── 19_response_status_code.py               # レスポンスステータスコード
  └── 20_form_data.py                          # フォームデータ
  └── 21_form_models.py                        # フォームモデル
  └── 22_request_files.py                      # リクエストファイル
  └── 23_request_forms_and_files.py            # リクエストフォームとファイル
  └── 24_handling_errors.py                    # エラーハンドリング
  └── 25_path_operation_configuration.py       # パス操作設定
  └── 26_JSON_compatible_encoder.py            # JSON互換エンコーダー
  └── 27_body_updates.py                       # ボディ更新
  └── 28_dependencies.py                       # 依存性システム完全ガイド
```

## 🚀 実行方法
各ファイルを以下のコマンドで実行できます：
```bash
uvicorn {ファイル名}:app --reload  
```
※ ファイル名は拡張子(.py)を除いて指定してください

**実行例：**
```bash
uvicorn 01_basic_routing:app --reload
uvicorn 28_dependencies:app --reload
```

**アクセス先：**
- APIドキュメント: http://localhost:8000/docs
- 代替ドキュメント: http://localhost:8000/redoc