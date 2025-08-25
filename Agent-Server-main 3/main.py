import uvicorn

from fastapi import FastAPI

from routers import chat
from config import settings
from chroma_db_tools.model_localizer import download_model_to_local
from log import set_log

app = FastAPI(title="Agent-Server", version="1.0.0")

app.include_router(chat.router)


if __name__ == "__main__":
    print("""
   _____ _                 _                            _   
  / ____| |               | |     /\                   | |  
 | |    | | ___  _   _  __| |    /  \   __ _  ___ _ __ | |_ 
 | |    | |/ _ \| | | |/ _` |   / /\ \ / _` |/ _ \ '_ \| __|
 | |____| | (_) | |_| | (_| |  / ____ \ (_| |  __/ | | | |_ 
  \_____|_|\___/ \__,_|\__,_| /_/    \_\__, |\___|_| |_|\__|
                                        __/ |               
                                       |___/                            
    """)
    set_log()
    download_model_to_local()
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)