from fastapi import FastAPI

app = FastAPI(title="AI Atlas India content engine API")


@app.get("/health")
def health():
    return {"ok": True}
