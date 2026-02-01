import json
from .messages import Messages, GeneralMessages


class ResponseHandler:
    """
    Clase para manejar las respuestas de la API de forma estandarizada.
    Proporciona métodos para generar respuestas con formatos consistentes.
    """

    @staticmethod
    def success(data=None, message=GeneralMessages.SUCCESS.value, status_code=200):
        """
        Genera una respuesta exitosa con formato estándar

        Args:
            data: Los datos a incluir en la respuesta (opcional)
            message: Mensaje descriptivo de la operación (opcional, por defecto 'Success')
            status_code: Código HTTP de estado (opcional, por defecto 200)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
        }

        return response, status_code

    @staticmethod
    def error(message=GeneralMessages.ERROR.value, status_code=400, error_details=None):
        """
        Genera una respuesta de error con formato estándar

        Args:
            message: Mensaje descriptivo del error (opcional, por defecto 'Error')
            status_code: Código HTTP de estado (opcional, por defecto 400)
            error_details: Detalles adicionales del error (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado
        """
        response = {
            "Success": False,
            "Message": message,
        }

        if error_details is not None:
            response["ErrorDetails"] = error_details

        return response, status_code

    @staticmethod
    def created(data=None, message=GeneralMessages.SUCCESS.value):
        """
        Genera una respuesta para recursos creados exitosamente (HTTP 201)

        Args:
            data: Los datos del recurso creado (opcional)
            message: Mensaje descriptivo (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 201
        """
        return ResponseHandler.success(data, message, 201)

    @staticmethod
    def not_found(resource_name="Resource"):
        """
        Genera una respuesta para recursos no encontrados (HTTP 404)

        Args:
            resource_name: Nombre del recurso no encontrado (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 404
        """
        message = f"{resource_name} not found"
        return ResponseHandler.error(message, 404)

    @staticmethod
    def forbidden(message=GeneralMessages.FORBIDDEN.value):
        """
        Genera una respuesta para accesos denegados (HTTP 403)

        Args:
            message: Mensaje descriptivo (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 403
        """
        return ResponseHandler.error(message, 403)

    @staticmethod
    def unauthorized(message=GeneralMessages.UNAUTHORIZED.value):
        """
        Genera una respuesta para accesos no autorizados (HTTP 401)

        Args:
            message: Mensaje descriptivo (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 401
        """
        return ResponseHandler.error(message, 401)

    @staticmethod
    def bad_request(message=GeneralMessages.BAD_REQUEST.value, error_details=None):
        """
        Genera una respuesta para solicitudes incorrectas (HTTP 400)

        Args:
            message: Mensaje descriptivo (opcional)
            error_details: Detalles adicionales del error (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 400
        """
        return ResponseHandler.error(message, 400, error_details)

    @staticmethod
    def conflict(message=GeneralMessages.CONFLICT.value, error_details=None):
        """
        Genera una respuesta para conflictos, como recursos duplicados (HTTP 409)

        Args:
            message: Mensaje descriptivo (opcional)
            error_details: Detalles adicionales del error (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 409
        """
        return ResponseHandler.error(message, 409, error_details)

    @staticmethod
    def server_error(
        message=GeneralMessages.INTERNAL_SERVER_ERROR.value, error_details=None
    ):
        """
        Genera una respuesta para errores internos del servidor (HTTP 500)

        Args:
            message: Mensaje descriptivo (opcional)
            error_details: Detalles adicionales del error (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado 500
        """
        return ResponseHandler.error(message, 500, error_details)

    @staticmethod
    def _handle_status_code(data, status_code, resource_name):
        """
        Maneja la respuesta según el código de estado HTTP

        Args:
            data: Los datos a incluir en la respuesta
            status_code: Código HTTP de estado
            resource_name: Nombre del recurso para mensajes de error

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado
        """
        message = data if isinstance(data, str) else None

        status_handlers = {
            404: lambda: ResponseHandler.not_found(resource_name),
            400: lambda: ResponseHandler.bad_request(
                message or Messages.get_by_code(400)
            ),
            409: lambda: ResponseHandler.conflict(
                message or f"{resource_name} already exists"
            ),
            401: lambda: ResponseHandler.unauthorized(
                message or Messages.get_by_code(401)
            ),
            403: lambda: ResponseHandler.forbidden(
                message or Messages.get_by_code(403)
            ),
            500: lambda: ResponseHandler.server_error(
                message or Messages.get_by_code(500)
            ),
            201: lambda: ResponseHandler.created(data),
        }

        # Usar el manejador específico o devolver éxito con el código proporcionado
        return status_handlers.get(
            status_code, lambda: ResponseHandler.success(data, "Success", status_code)
        )()

    @staticmethod
    def from_result(result, resource_name="Resource"):
        """
        Genera una respuesta basada en el resultado de una operación

        Args:
            result: El resultado de la operación, que puede ser un objeto o una tupla (resultado, status_code)
            resource_name: Nombre del recurso para mensajes de error (opcional)

        Returns:
            tuple: Una tupla con el diccionario de respuesta y el código de estado apropiado
        """
        # Si el resultado es una tupla, asumimos que tiene el formato (data, status_code)
        if (
            isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[1], int)
        ):
            data, status_code = result
            return ResponseHandler._handle_status_code(data, status_code, resource_name)

        # Si no es una tupla o no tiene el formato esperado, asumimos éxito
        return ResponseHandler.success(result)

    @staticmethod
    def to_json(response_dict):
        """
        Convierte el diccionario de respuesta a una cadena JSON.

        Args:
            response_dict: El diccionario de respuesta

        Returns:
            str: La respuesta en formato JSON
        """
        return json.dumps(response_dict, ensure_ascii=False)
