from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.models.common import HealthResponse
from app.routers import files, jobs, lyrics, lrc, music, projects, prompt_presets, publish

app = FastAPI(title="Backend API")

app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(lyrics.router)
app.include_router(prompt_presets.router)
app.include_router(files.router)
app.include_router(music.router)
app.include_router(lrc.router)
app.include_router(publish.router)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT, RELOAD

    uvicorn.run(app, host=HOST, port=PORT, reload=RELOAD)
