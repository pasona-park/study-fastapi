from fastapi import FastAPI

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