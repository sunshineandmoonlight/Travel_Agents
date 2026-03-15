"""简单的测试服务器，验证staged_planning路由"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from app.routers.staged_planning import router as staged_router

app = FastAPI()

# 直接注册路由，不添加额外prefix
app.include_router(staged_router)

@app.get("/")
async def root():
    return {"message": "Test server is running", "staged_routes": len(staged_router.routes)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
