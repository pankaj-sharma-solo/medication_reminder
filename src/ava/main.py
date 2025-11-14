import uvicorn
from fastapi import FastAPI
app = FastAPI()

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)