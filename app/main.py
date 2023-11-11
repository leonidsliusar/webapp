import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import app, admin

origins = [
    "http://localhost:80",
    "http://0.0.0.0:80",
    "*"
]

web = FastAPI(title='Property WebSite')
web.add_middleware(
     CORSMiddleware,
     allow_origins=origins,
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)
web.include_router(app, tags=['app'])
web.include_router(admin, tags=['admin panel'])
web.mount('/static', web, 'static')


if __name__ == '__main__':
    uvicorn.run(web, host='0.0.0.0', port=8000)
