from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import logging

# Configure logging to save logs to a file
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

info_handler = logging.FileHandler('info-log.log')
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(info_formatter)

# Create an error handler to store error messages in the 'error-log.log' file
error_handler = logging.FileHandler('error-log.log')
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_handler.setFormatter(error_formatter)

# Create a warning handler to store warning messages in the 'warning-log.log' file
warning_handler = logging.FileHandler('warning-log.log')
warning_handler.setLevel(logging.WARNING)
warning_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
warning_handler.setFormatter(warning_formatter)

# Get the root logger and add the error and warning handlers
root_logger = logging.getLogger()
root_logger.addHandler(error_handler)
root_logger.addHandler(warning_handler)

# Create a separate logger for info messages and add the info handler
info_logger = logging.getLogger('info_logger')
info_logger.addHandler(info_handler)


app = FastAPI()

# In-memory database as a list
fake_db = []


# Pydantic model for the data
class Item(BaseModel):
    name: str
    description: str


# Create operation
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    fake_db.append(item)
    info_logger.info(
        msg=f"Item created: {item.name}",
        extra={"endpoint": "POST API END POINT http://127.0.0.1:8000/items"}
    )
    return item


# Read operation (get all items)
@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 10):
    logging.info(
        msg=f"Items retrieved (skip={skip}, limit={limit})",
        extra={"endpoint": "GET API END POINT http://127.0.0.1:8000/items"}
    )
    return fake_db[skip:skip + limit]


# Read operation (get a single item by ID)
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    if item_id < 0 or item_id >= len(fake_db):
        root_logger.error(
            msg=f"Item not found (ID={item_id})",
            extra={"endpoint": "GET API END POINT http://127.0.0.1:8000/items"}
        )
        raise HTTPException(status_code=404, detail="Item not found")

    logging.info(
        msg=f"Item retrieved by ID: {item_id}",
        extra={"endpoint": "GET API END POINT http://127.0.0.1:8000/items"}
    )
    
    return fake_db[item_id]


# Update operation
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(fake_db):
        logging.error(
            msg=f"Item not found for update (ID={item_id})",
            extra={"endpoint": "PUT API END POINT http://127.0.0.1:8000/items"}
        )
        raise HTTPException(status_code=404, detail="Item not found")

    fake_db[item_id] = item
    logging.info(
        msg=f"Item updated: {item.name}",
        extra={"endpoint": "PUT API END POINT http://127.0.0.1:8000/items"}
    )
    return item


# Delete operation
@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(fake_db):
        logging.error(
            msg=f"Item not found for deletion (ID={item_id})",
            extra={"endpoint": "DELETE API END POINT http://127.0.0.1:8000/items"}
        )
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = fake_db.pop(item_id)
    logging.info(
        msg=f"Item deleted: {deleted_item.name}",
        extra={"endpoint": "DELETE API END POINT http://127.0.0.1:8000/items"}
    )
    return deleted_item

# Run the application using Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
