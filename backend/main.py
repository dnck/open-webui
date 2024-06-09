import time

import uvicorn

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.ollama.main import app as ollama_app
from apps.openai.main import app as openai_app
from apps.audio.main import app as audio_app
from apps.web.main import app as webui_app
from apps.rag.main import app as rag_app
from apps.metrics.main import app as metrics_app

from config import ENV, FRONTEND_BUILD_DIR


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


app = FastAPI(docs_url="/docs" if ENV == "dev" else None, redoc_url=None)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def check_url(request: Request, call_next):
    start_time = int(time.time())
    response = await call_next(request)
    process_time = int(time.time()) - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


app.mount("/api/v1", webui_app)
app.mount("/ollama/api", ollama_app)
app.mount("/openai/api", openai_app)
app.mount("/audio/api/v1", audio_app)
app.mount("/rag/api/v1", rag_app)
# The metrics won't get served properly without 
# making it such that the single page app 
# proxies the response properly 
app.mount("/metrics", metrics_app)
app.mount(
    "/",
    SPAStaticFiles(directory=FRONTEND_BUILD_DIR, html=True),
    name="spa-static-files",
)


if __name__ == "__main__":
    uconfig = uvicorn.Config(app="main:app", host="0.0.0.0", port=3000)
    uconfig.forwarded_allow_ips = "*"
    server = uvicorn.Server(uconfig)
    server.run()
