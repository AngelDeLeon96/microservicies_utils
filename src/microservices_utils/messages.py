"""
Módulo para centralizar todos los mensajes de la aplicación.
Este enfoque permite mantener la consistencia de los mensajes, facilitar la internacionalización
y simplificar el mantenimiento de los textos en toda la aplicación.
"""

from enum import Enum


class BaseMessages(Enum):
    """Clase base para todas las enumeraciones de mensajes"""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        """Convierte los nombres de enumeración en formato snake_case a una cadena legible"""
        return name.lower().replace("_", " ").capitalize()

    @property
    def message(self):
        """Retorna el mensaje asociado a la enumeración"""
        return self.value


class GeneralMessages(BaseMessages):
    """Mensajes generales de la aplicación"""

    SUCCESS = "Operación completada con éxito"
    ERROR = "Se produjo un error"
    INTERNAL_SERVER_ERROR = "Error interno del servidor"
    NOT_FOUND = "Recurso no encontrado"
    FORBIDDEN = "Acceso denegado"
    UNAUTHORIZED = "Acceso no autorizado"
    BAD_REQUEST = "Solicitud incorrecta"
    CONFLICT = "Conflicto con el recurso existente"
    INVALID_INPUT = "Datos de entrada inválidos"
    MISSING_REQUIRED_FIELDS = "Faltan campos requeridos"
    INVALID_CREDENTIALS = "Credenciales inválidas"
    SESSION_EXPIRED = "Sesión expirada"
    OPERATION_NOT_ALLOWED = "Operación no permitida"


class UserMessages(BaseMessages):
    """Mensajes relacionados con usuarios"""

    USER_CREATED = "Usuario creado exitosamente"
    USER_UPDATED = "Usuario actualizado exitosamente"
    USER_DELETED = "Usuario eliminado exitosamente"
    USER_NOT_FOUND = "Usuario no encontrado"
    USER_ALREADY_EXISTS = "El usuario ya existe"
    USER_INACTIVE = "El usuario está inactivo"
    INVALID_PASSWORD = "Contraseña inválida"
    PASSWORD_UPDATED = "Contraseña actualizada correctamente"
    EMAIL_ALREADY_EXISTS = "El correo electrónico ya está registrado"
    INVALID_EMAIL_FORMAT = "Formato de correo electrónico inválido"
    ROLE_ASSIGNED = "Rol asignado correctamente"
    ROLE_NOT_FOUND = "Rol no encontrado"
    PERMISSION_DENIED = "Permiso denegado"


class AuthMessages(BaseMessages):
    """Mensajes relacionados con autenticación"""

    LOGIN_SUCCESS = "Inicio de sesión exitoso"
    LOGIN_FAILED = "Inicio de sesión fallido"
    LOGOUT_SUCCESS = "Cierre de sesión exitoso"
    TOKEN_EXPIRED = "Token expirado"
    TOKEN_INVALID = "Token inválido"
    TOKEN_REVOKED = "Token revocado"
    TOKEN_REFRESH_SUCCESS = "Token actualizado correctamente"


class ReportMessages(BaseMessages):
    """Mensajes relacionados con reportes"""

    REPORT_CREATED = "Reporte creado exitosamente"
    REPORT_UPDATED = "Reporte actualizado exitosamente"
    REPORT_DELETED = "Reporte eliminado exitosamente"
    REPORT_NOT_FOUND = "Reporte no encontrado"
    REPORT_ALREADY_EXISTS = "El reporte ya existe"
    REPORT_PART_UPDATED = "Parte del reporte actualizada correctamente"
    REPORT_FINISHED = "Reporte finalizado correctamente"
    INVALID_REPORT_NUMBER = "Número de reporte inválido"
    REPORT_NOT_EDITABLE = "El reporte no puede ser editado"


class ClientMessages(BaseMessages):
    """Mensajes relacionados con clientes"""

    CLIENT_CREATED = "Cliente creado exitosamente"
    CLIENT_UPDATED = "Cliente actualizado exitosamente"
    CLIENT_DELETED = "Cliente eliminado exitosamente"
    CLIENT_NOT_FOUND = "Cliente no encontrado"
    CLIENT_ALREADY_EXISTS = "El cliente ya existe"


class RoleMessages(BaseMessages):
    """Mensajes relacionados con roles"""

    ROLE_RETRIEVED = "Rol recuperado exitosamente"
    ROLE_CREATED = "Rol creado exitosamente"
    ROLE_UPDATED = "Rol actualizado exitosamente"
    ROLE_DELETED = "Rol eliminado exitosamente"
    ROLE_NOT_FOUND = "Rol no encontrado"
    ROLE_ALREADY_EXISTS = "El rol ya existe"
    PERMISSION_ADDED_TO_ROLE = "Permiso agregado al rol correctamente"
    PERMISSION_REMOVED_FROM_ROLE = "Permiso eliminado del rol correctamente"
    INVALID_ROLE_NAME = "Nombre de rol inválido"


class PermissionMessages(BaseMessages):
    """Mensajes relacionados con permisos"""

    PERMISSION_CREATED = "Permiso creado exitosamente"
    PERMISSION_UPDATED = "Permiso actualizado exitosamente"
    PERMISSION_DELETED = "Permiso eliminado exitosamente"
    PERMISSION_NOT_FOUND = "Permiso no encontrado"
    PERMISSION_ALREADY_EXISTS = "El permiso ya existe"
    INVALID_PERMISSION_NAME = "Nombre de permiso inválido"
    PERMISSION_ASSIGNED_TO_ROLE = "Permiso asignado al rol correctamente"
    PERMISSION_REMOVED_FROM_ROLE = "Permiso eliminado del rol correctamente"


class Messages:
    """
    Clase principal para acceder a todos los mensajes de la aplicación.
    Agrupa todas las categorías de mensajes para facilitar su uso.
    """

    general = GeneralMessages
    user = UserMessages
    auth = AuthMessages
    report = ReportMessages
    client = ClientMessages
    role = RoleMessages
    permission = PermissionMessages

    @staticmethod
    def format(message_enum, **kwargs):
        """
        Formatea un mensaje con parámetros dinámicos.

        Args:
            message_enum: La enumeración del mensaje a formatear
            **kwargs: Parámetros para formatear el mensaje

        Returns:
            str: El mensaje formateado
        """
        return message_enum.value.format(**kwargs)

    @staticmethod
    def get_by_code(code, default=None):
        """
        Obtiene un mensaje basado en un código de error.
        Útil para mapear códigos HTTP a mensajes específicos.

        Args:
            code: El código de error (por ejemplo, código HTTP)
            default: Mensaje por defecto si no se encuentra el código

        Returns:
            str: El mensaje correspondiente al código
        """
        code_map = {
            400: GeneralMessages.BAD_REQUEST.value,
            401: GeneralMessages.UNAUTHORIZED.value,
            403: GeneralMessages.FORBIDDEN.value,
            404: GeneralMessages.NOT_FOUND.value,
            409: GeneralMessages.CONFLICT.value,
            500: GeneralMessages.INTERNAL_SERVER_ERROR.value,
        }
        return code_map.get(code, default or GeneralMessages.ERROR.value)
