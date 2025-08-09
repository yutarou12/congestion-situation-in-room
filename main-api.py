import json
import os
import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])   


def verify_token(token: str = Depends(oauth2_scheme)):
    if token != os.getenv("API_TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permission to access this API.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.get("/")
async def root():
    return {"message": "Hello Worlds!"}

@app.post("/api/get/people-count")
async def get_people(token: str = Depends(verify_token)):
    with open("./data/room_status.json", encoding="utf-8") as f:
        data = json.load(f)

    count = data.get("peopleCount")

    return {"count": count}

@app.post("/api/get/status")
async def get_status(token: str = Depends(verify_token)):
    with open("./data/room_status.json", encoding="utf-8") as f:
        data = json.load(f)

    room_status = data.get("roomStatus")

    return {"status": room_status}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=int(os.getenv("API_PORT", "8080")), log_level="debug")
