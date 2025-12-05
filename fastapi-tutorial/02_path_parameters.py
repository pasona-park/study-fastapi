from enum import Enum
from fastapi import FastAPI

# 標準PythonのEnumクラスを継承して飲み物の種類を事前定義
class DrinkType(str, Enum):
    coffee = "coffee"
    tea = "tea"
    juice = "juice"

# FastAPIインスタンスを作成
app = FastAPI()


# item_idをパスパラメータとして受け取るエンドポイント・例: 127.0.0.1:8000/items/5
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

# パスパラメータのタイプを指定（文字列）
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}



# Enumを使用したパスパラメータの例
## 事前定義した飲み物の種類に基づいて異なるレスポンスを返す
@app.get("/drinks/{drink_type}")
async def get_drink(drink_type: DrinkType):
    if drink_type is DrinkType.coffee:
        return {"drink_type": drink_type, "message": "Perfect for morning energy!"}

    if drink_type.value == "tea":
        return {"drink_type": drink_type, "message": "Relaxing and healthy choice"}

    return {"drink_type": drink_type, "message": "Fresh and vitamin-rich!"}

# --------------------------------------------------
# Enumとは？
## Pythonの標準ライブラリで提供される列挙型（Enumeration）を定義するためのクラス
## 一連の関連する定数に名前を付けてグループ化する

# 使い方
## 1. 事前定義した値だけ使用
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

# 使用
color = Color.RED  # ✅ OK
color = Color.YELLOW  # ❌ エラー!


## 2. Enumの属性とアクセス方法
class Animal(str, Enum):
    cat = "cat"
    dog = "dog"

# Enum要素そのもの
print(Animal.cat)        # Animal.cat
## Enum要素をprint()で出力すると、Pythonは__str__()メソッドを呼び出し、クラス名.要素名の形式で表示される

# 要素の名前を取得
print(Animal.cat.name)   # "cat"

# 要素の値を取得
print(Animal.cat.value)  # "cat"
## name, valueはEnumが自動で提供する属性、要素の値を取得
# --------------------------------------------------



# パスを含んだパスパラメータ
# 一般的なパスパラメータ（file_pathにスラッシュ不可）
## 例： /files1/myfile.txt はOK
##      /files1/home/johndoe/myfile.txt はNG
@app.get("/files1/{file_path}")
async def read_file_normal(file_path: str):
    return {"file_path": file_path, "type": "normal"}

# パス変換器を使用したパスパラメータ（file_pathにスラッシュ可）
## 例： /files2/myfile.txt はOK
##      /files2/home/johndoe/myfile.txt はOK
@app.get("/files2/{file_path:path}")
async def read_file_with_path(file_path: str):
    return {"file_path": file_path, "type": "with_path_converter"}