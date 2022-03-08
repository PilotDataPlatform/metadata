import uvicorn

from app.config import ConfigClass

if __name__ == '__main__':
    uvicorn.run('app.main:app', host=ConfigClass.HOST, port=ConfigClass.PORT, log_level='info', reload=True)
