from app.main import app
import uvicorn

if __name__ == "__main__":
    """
    This script runs the application using uvicorn server.
    It starts the server on the specified host and port.
    """
    server = uvicorn.Server(config=uvicorn.Config(app, host="0.0.0.0", port=8000))
    try:
        server.run()
    except KeyboardInterrupt:
        server.shutdown()
        print("\nServer stopped.")