from app.main import app

if __name__ == "__main__":
    """
    This script runs the application using uvicorn server.
    It starts the server on the specified host and port.
    """
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        pass
