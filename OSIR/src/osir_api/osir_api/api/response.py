API_VERSION = "1.0"

def SUCCESS_RESPONSE(data: dict) -> dict:
    return {
        "version": API_VERSION,
        "status": 200,
        "response": data
    }

def ERROR_RESPONSE(status: int, message: str) -> dict:
    return {
        "version": API_VERSION,
        "status": status,
        "response": {
            "error": message
        }
    }