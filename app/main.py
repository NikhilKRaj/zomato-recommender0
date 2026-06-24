from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.dependencies import lifespan
from app.api.routes import metadata, recommend
from app.core.config import settings
from app.core.exceptions import AppError, DataLoadError, LLMError, NoCandidatesError

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metadata.router)
app.include_router(recommend.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


@app.exception_handler(NoCandidatesError)
async def no_candidates_handler(request: Request, exc: NoCandidatesError) -> JSONResponse:
    del request
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DataLoadError)
async def data_load_handler(request: Request, exc: DataLoadError) -> JSONResponse:
    del request
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
    del request
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    del request
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict:
    data_loaded = False
    restaurant_count = 0
    loader = getattr(app.state, "data_loader", None)
    if loader is not None:
        data_loaded = True
        restaurant_count = len(loader.get_restaurant_store())

    return {
        "status": "ok",
        "data_loaded": data_loaded,
        "restaurant_count": restaurant_count,
    }
