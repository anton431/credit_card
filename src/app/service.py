"""main modul."""
import uvicorn

from src.app.config.config import HOST, PORT_SRC
from src.app.views.user import app


    
if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT_SRC)  # noqa: WPS432, S104
