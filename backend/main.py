def main():
    print("Hello from backend!")


if __name__ == "__main__":
    main()

from fastapi import FastAPI
from routes.query_routes import router

app = FastAPI(title="NL2SQL API")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "running"}
    