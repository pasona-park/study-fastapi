from enum import Enum
from fastapi import FastAPI

# 標準PythonのEnumクラスを継承してモデル名を事前定義
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# FastAPIインスタンスを作成
app = FastAPI()

# ルートエンドポイントのため、127.0.0.1:8000/にアクセスすると"Hello World!"が画面に表示される
@app.get("/")
def read_root():
    return {"message": "Hello World!"}

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
## 事前定義したモデル名に基づいて異なるレスポンスを返す
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}