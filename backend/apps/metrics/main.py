from fastapi import FastAPI, Request, Response, HTTPException, Depends

from fastapi.middleware.cors import CORSMiddleware

from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def handle_metrics(request: Request) -> Response:
    registry = REGISTRY
    headers = {"Content-Type": CONTENT_TYPE_LATEST}
    return Response(generate_latest(registry), status_code=200, headers=headers)
