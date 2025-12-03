FastAPI学習用リポジトリ

## 📖 概要
FastAPI公式チュートリアル（https://fastapi.tiangolo.com/tutorial/）を参考に学習した内容を、機能別にファイルを分けて整理しています。

## 📁 プロジェクト構成
```
study-project/
  └── 01_basic_routing.py    # 基本ルーティング
  └── 02_path_parameters.py    # パスパラメータ
  └── 03_query_parameters.py    # クエリパラメータ
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