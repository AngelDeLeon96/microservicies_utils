# Microservices Utils 

A reusable Python package for utils.

## Features

- Standardized response formats for success and error cases
- Support for common HTTP status codes
- Configurable messages
- Framework-agnostic design (no Flask dependency)
- Centralized logging with file rotation and permission management
- Predefined message enums for consistency

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Usage

```python
from response_handler import ResponseHandler

# Success response
response, status = ResponseHandler.success(data={"key": "value"}, message="Operation successful")
# response is a dict, status is int

# For Flask
from flask import jsonify
return jsonify(response), status

# For other frameworks, use their JSON response method

# Error response
response, status = ResponseHandler.error(message="Something went wrong", status_code=400)

# Specific error types
response, status = ResponseHandler.not_found("User")
response, status = ResponseHandler.forbidden()
```

```python
from logger import Logger

# Log messages
Logger.add_to_log("info", "Service started")
Logger.add_to_log("error", "An error occurred")
```

## API

### ResponseHandler

- `success(data=None, message="Success", status_code=200)`: Returns success response
- `error(message="Error", status_code=400, error_details=None)`: Returns error response
- `created(data=None, message="Success")`: Returns 201 Created response
- `not_found(resource_name="Resource")`: Returns 404 Not Found response
- `forbidden(message="Forbidden")`: Returns 403 Forbidden response
- `unauthorized(message="Unauthorized")`: Returns 401 Unauthorized response
- `bad_request(message="Bad Request", error_details=None)`: Returns 400 Bad Request response
- `conflict(message="Conflict", error_details=None)`: Returns 409 Conflict response
- `server_error(message="Internal Server Error", error_details=None)`: Returns 500 Server Error response
- `from_result(result, resource_name="Resource")`: Handles result tuples
- `to_json(response_dict)`: Converts response dict to JSON string

### Messages

Predefined message enums for consistency:

- `GeneralMessages`
- `UserMessages`
- `AuthMessages`
- etc.

### Logger

- `add_to_log(level, message)`: Logs a message at the specified level (debug, info, warn, error, critical)

## License

MIT