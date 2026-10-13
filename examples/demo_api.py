from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="AGASTYA Demo API",
    version="1.0.0",
)

items: dict[int, dict[str, object]] = {
    1: {"id": 1, "name": "Demo item"}
}

next_item_id = 2


class ItemInput(BaseModel):
    name: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/items")
def list_items():
    return list(items.values())


@app.post("/items", status_code=201)
def create_item(payload: ItemInput):
    global next_item_id

    item = {
        "id": next_item_id,
        "name": payload.name,
    }

    items[next_item_id] = item
    next_item_id += 1

    return item


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = items.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return item