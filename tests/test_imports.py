"""
Tests for microservices_utils package imports
"""

import pytest
import tempfile
import os


def test_package_imports():
    """Test that all main components can be imported from the package"""
    try:
        from microservices_utils import (
            Messages,
            GeneralMessages,
            ResponseHandler,
            Logger,
            JwtHandler,
        )

        assert Messages is not None
        assert GeneralMessages is not None
        assert ResponseHandler is not None
        assert Logger is not None
        assert JwtHandler is not None
    except ImportError as e:
        pytest.fail(f"Failed to import package components: {e}")


def test_response_handler_functionality():
    """Test basic ResponseHandler functionality"""
    from microservices_utils import ResponseHandler

    # Test success response
    response = ResponseHandler.success({"test": "data"})
    assert response["status_code"] == 200
    assert response["success"] is True
    assert "data" in response
    assert response["data"]["test"] == "data"

    # Test error response
    response = ResponseHandler.error("Test error")
    assert response["status_code"] == 400
    assert response["Success"] is False  # Note: Capital S
    assert response["Message"] == "Test error"


def test_messages_enum():
    """Test Messages enum functionality"""
    from microservices_utils import GeneralMessages

    # Test that GeneralMessages has expected attributes
    assert hasattr(GeneralMessages, "SUCCESS")
    assert hasattr(GeneralMessages, "ERROR")
    assert hasattr(GeneralMessages, "NOT_FOUND")

    # Test values
    assert GeneralMessages.SUCCESS.value == "Operación completada con éxito"
    assert GeneralMessages.ERROR.value == "Se produjo un error"
    assert GeneralMessages.NOT_FOUND.value == "Recurso no encontrado"


def test_logger_functionality():
    """Test Logger functionality"""
    from microservices_utils import Logger

    # Test logging functionality (Logger uses class methods)
    # Create a temporary directory for logs
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test info logging
        Logger.info("Test message")
        # The logger should work without explicit initialization
        assert Logger is not None


def test_jwt_handler_functionality():
    """Test JwtHandler functionality"""
    from microservices_utils import JwtHandler

    # Test JWT creation (skip password hashing due to bcrypt issues in test environment)
    test_data = {"user_id": 123, "username": "testuser"}
    token = JwtHandler.create_access_token(test_data)
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    # Basic check that it looks like a JWT (has dots)
    assert token.count(".") == 2


def test_messages_class():
    """Test Messages class functionality"""
    from microservices_utils import Messages

    # Test that Messages has the expected attributes
    assert hasattr(Messages, "general")
    assert hasattr(Messages, "user")
    assert Messages.general is not None

    # Test get_by_code method
    message_404 = Messages.get_by_code(404)
    assert message_404 == "Recurso no encontrado"

    message_200 = Messages.get_by_code(200, "Default message")
    assert message_200 == "Default message"  # 200 not in map


if __name__ == "__main__":
    # Run basic import test if executed directly
    test_package_imports()
    print("✅ All imports successful!")

    test_response_handler_functionality()
    print("✅ ResponseHandler functionality test passed!")

    test_messages_enum()
    print("✅ Messages enum test passed!")

    test_logger_functionality()
    print("✅ Logger functionality test passed!")

    test_jwt_handler_functionality()
    print("✅ JwtHandler functionality test passed!")

    test_messages_class()
    print("✅ Messages class test passed!")

    print("🎉 All tests passed!")
