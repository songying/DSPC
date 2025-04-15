from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .routers import users, datasets, computations, analytics
from .auth import get_current_active_user, create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from .models import Token
from datetime import timedelta

app = FastAPI(
    title="Privacy Data Trading Protocol",
    description="A protocol for privacy-preserving data trading and computing with Web3",
    version="0.1.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(users.router)
app.include_router(datasets.router)
app.include_router(computations.router)
app.include_router(analytics.router)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Privacy Data Trading Protocol API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
