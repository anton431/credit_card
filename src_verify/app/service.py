"""main modul."""
import uvicorn

from src_verify.app.config.config import HOST, PORT_SRC
from src_verify.app.views.verify import app

if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host=HOST,  # noqa: S104
        port=PORT_SRC,
    )  # noqa: WPS432
