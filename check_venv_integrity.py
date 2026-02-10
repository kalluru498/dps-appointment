
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

try:
    import fastapi  # type: ignore
    print(f"FastAPI version: {fastapi.__version__}")
except ImportError:
    print("FastAPI NOT FOUND")

try:
    from agent.booking_engine import BookingEngine  # type: ignore
    print("BookingEngine imported successfully")
except Exception as e:
    print(f"Error importing BookingEngine: {e}")

try:
    from api.websocket import ConnectionManager  # type: ignore
    print("ConnectionManager imported successfully")
except Exception as e:
    print(f"Error importing ConnectionManager: {e}")
