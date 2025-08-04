import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.telegram.middlewares.error_logger import ErrorLoggerMiddleware


async def test_error_logger_middleware():
    """Test that ErrorLoggerMiddleware logs exceptions and re-raises them."""
    middleware = ErrorLoggerMiddleware()
    
    # Mock handler that raises an exception
    async def failing_handler(event, data):
        raise ValueError("Test exception")
    
    # Mock event and data
    event = MagicMock()
    event.__class__.__name__ = "TestEvent"
    data = {}
    
    # Test that the exception is logged and re-raised
    try:
        await middleware(failing_handler, event, data)
        assert False, "Exception should have been raised"
    except ValueError as e:
        assert str(e) == "Test exception"
        print("✅ ErrorLoggerMiddleware correctly re-raises exceptions")
    
    # Test normal handler execution
    async def normal_handler(event, data):
        return "success"
    
    result = await middleware(normal_handler, event, data)
    assert result == "success"
    print("✅ ErrorLoggerMiddleware correctly passes through normal execution")


if __name__ == "__main__":
    asyncio.run(test_error_logger_middleware()) 