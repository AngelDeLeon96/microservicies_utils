import logging
import os
import stat
import traceback
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import tempfile


class Logger:

    @staticmethod
    def _fix_permissions(path, is_directory=True):
        """
        Fix permissions for a file or directory to ensure proper access.

        Args:
            path (Path): Path to the file or directory
            is_directory (bool): Whether the path is a directory
        """
        try:
            if is_directory:
                # Directory permissions: rwxrwxr-x (775)
                # Owner and group have full access, others can read/execute
                path.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
            else:
                # File permissions: rw-rw-r-- (664)
                # Owner and group can read/write, others can only read
                path.chmod(
                    stat.S_IRUSR
                    | stat.S_IWUSR
                    | stat.S_IRGRP
                    | stat.S_IWGRP
                    | stat.S_IROTH
                )
        except PermissionError as e:
            print(f"Warning: Could not set permissions for {path}: {e}")
        except Exception as e:
            print(f"Warning: Unexpected error setting permissions for {path}: {e}")

    @staticmethod
    def _ensure_log_directory(log_directory):
        """
        Ensures that the log directory exists with proper permissions.
        Handles permission conflicts and provides multiple fallback options.
        """
        log_path = Path(log_directory)

        # Strategy 1: Try to create/use the requested directory
        try:
            log_path.mkdir(parents=True, exist_ok=True)
            Logger._fix_permissions(log_path, is_directory=True)

            # Test write access by creating a temporary file
            test_file = log_path / ".write_test"
            try:
                test_file.write_text("test", encoding="utf-8")
                test_file.unlink()  # Clean up test file
                return str(log_path)
            except (PermissionError, OSError) as e:
                print(f"Write test failed for {log_path}: {e}")
                raise PermissionError(f"Cannot write to {log_path}")

        except (PermissionError, OSError) as e:
            print(f"Cannot use primary log directory {log_directory}: {e}")

        # Strategy 2: Try user-specific directory in home
        try:
            user_log_dir = Path.home() / ".pms_backend" / "logs"
            user_log_dir.mkdir(parents=True, exist_ok=True)
            Logger._fix_permissions(user_log_dir, is_directory=True)

            test_file = user_log_dir / ".write_test"
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink()

            return str(user_log_dir)

        except (PermissionError, OSError) as e:
            print(f"Cannot use user log directory: {e}")

        # Strategy 3: Try system temp directory
        try:
            temp_log_dir = Path(tempfile.gettempdir()) / "pms_backend_logs"
            temp_log_dir.mkdir(parents=True, exist_ok=True)
            Logger._fix_permissions(temp_log_dir, is_directory=True)

            test_file = temp_log_dir / ".write_test"
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink()

            return str(temp_log_dir)

        except (PermissionError, OSError) as e:
            print(f"Cannot use temp log directory: {e}")

        # Strategy 4: Fallback to current working directory
        try:
            fallback_dir = Path.cwd() / "logs"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            Logger._fix_permissions(fallback_dir, is_directory=True)

            test_file = fallback_dir / ".write_test"
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink()

            return str(fallback_dir)

        except (PermissionError, OSError) as e:
            print(f"Cannot use fallback log directory: {e}")

        # Strategy 5: Last resort - use a truly temporary directory
        temp_dir = Path(tempfile.mkdtemp(prefix="pms_logs_"))
        return str(temp_dir)

    def __set_access_logger(self):
        # Use absolute path based on project root
        project_root = Path(__file__).parent.parent.parent
        log_directory = project_root / "src" / "utils" / "log"
        log_filename = "access.log"

        # Ensure log directory exists with improved error handling
        log_dir_path = self._ensure_log_directory(log_directory)

        logger = logging.getLogger("access")
        logger.setLevel(logging.DEBUG)

        log_path = Path(log_dir_path) / log_filename

        try:
            # Create log file if it doesn't exist and set proper permissions
            if not log_path.exists():
                log_path.touch()
                self._fix_permissions(log_path, is_directory=False)

            # Use TimedRotatingFileHandler for daily rotation at midnight
            file_handler = TimedRotatingFileHandler(
                str(log_path),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)

            if logger.hasHandlers():
                logger.handlers.clear()

            logger.addHandler(file_handler)

            # Test write access
            test_record = logging.LogRecord(
                name="access",
                level=logging.DEBUG,
                pathname="",
                lineno=0,
                msg="Logger initialization test",
                args=(),
                exc_info=None,
            )
            file_handler.emit(test_record)

        except (PermissionError, OSError) as e:
            print(f"Permission error setting up access logger: {e}")
            # Try alternative file name in case of permission conflicts
            try:
                import uuid

                alternative_name = f"access_{uuid.uuid4().hex[:8]}.log"
                alternative_path = Path(log_dir_path) / alternative_name
                alternative_path.touch()
                self._fix_permissions(alternative_path, is_directory=False)

                file_handler = TimedRotatingFileHandler(
                    str(alternative_path),
                    when="midnight",
                    interval=1,
                    backupCount=30,
                    encoding="utf-8",
                )
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            except Exception as e2:
                print(f"Failed to create alternative access log: {e2}")
                # Fallback to console logging
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

        except Exception as e:
            print(f"Error setting up access logger: {e}")
            # Fallback to console logging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            logger.addHandler(console_handler)

        return logger

    def __set_error_logger(self):
        # Use absolute path based on project root
        project_root = Path(__file__).parent.parent.parent
        log_directory = project_root / "src" / "utils" / "log"
        log_filename = "error.log"

        # Ensure log directory exists with improved error handling
        log_dir_path = self._ensure_log_directory(log_directory)

        logger = logging.getLogger("error")
        logger.setLevel(logging.WARNING)

        log_path = Path(log_dir_path) / log_filename

        try:
            # Create log file if it doesn't exist and set proper permissions
            if not log_path.exists():
                log_path.touch()
                self._fix_permissions(log_path, is_directory=False)

            # Use TimedRotatingFileHandler for daily rotation at midnight
            file_handler = TimedRotatingFileHandler(
                str(log_path),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.WARNING)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)

            if logger.hasHandlers():
                logger.handlers.clear()

            logger.addHandler(file_handler)

            # Test write access
            test_record = logging.LogRecord(
                name="error",
                level=logging.WARNING,
                pathname="",
                lineno=0,
                msg="Logger initialization test",
                args=(),
                exc_info=None,
            )
            file_handler.emit(test_record)

        except (PermissionError, OSError) as e:
            print(f"Permission error setting up error logger: {e}")
            # Try alternative file name in case of permission conflicts
            try:
                import uuid

                alternative_name = f"error_{uuid.uuid4().hex[:8]}.log"
                alternative_path = Path(log_dir_path) / alternative_name
                alternative_path.touch()
                self._fix_permissions(alternative_path, is_directory=False)

                file_handler = TimedRotatingFileHandler(
                    str(alternative_path),
                    when="midnight",
                    interval=1,
                    backupCount=30,
                    encoding="utf-8",
                )
                file_handler.setLevel(logging.WARNING)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            except Exception as e2:
                print(f"Failed to create alternative error log: {e2}")
                # Fallback to console logging
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.WARNING)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

        except Exception as e:
            print(f"Error setting up error logger: {e}")
            # Fallback to console logging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            logger.addHandler(console_handler)

        return logger

    @classmethod
    def add_to_log(cls, level, message):
        """
        Adds a message to the appropriate log file based on the log level.

        Args:
            level (str): The log level ('debug', 'info', 'warn', 'error', 'critical')
            message (str): The message to log
        """
        try:
            # Validate inputs
            if not isinstance(level, str) or not level.strip():
                raise ValueError("Log level must be a non-empty string")

            if not isinstance(message, str):
                message = str(message)

            level = level.lower().strip()

            # Determine which logger to use
            if level in ["debug", "info"]:
                logger = cls.__set_access_logger(cls)
            elif level in ["warn", "warning", "error", "critical"]:
                logger = cls.__set_error_logger(cls)
            else:
                # Default to error logger for unknown levels
                logger = cls.__set_error_logger(cls)
                message = f"[UNKNOWN_LEVEL:{level}] {message}"
                level = "error"

            # Log the message with appropriate level
            if level == "critical":
                logger.critical(message)
            elif level == "debug":
                logger.debug(message)
            elif level == "error":
                logger.error(message)
            elif level == "info":
                logger.info(message)
            elif level in ["warn", "warning"]:
                logger.warning(message)

        except Exception as ex:
            # Enhanced error reporting
            error_msg = (
                f"Logger error: {str(ex)}\nOriginal message: {message}\nLevel: {level}"
            )
            print(f"LOGGER ERROR: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")

            # Try to log to console as last resort
            try:
                print(f"[{level.upper()}] {message}")
            except:
                print("Failed to log message to console as well")

    @classmethod
    def debug(cls, message):
        """Log a debug message"""
        cls.add_to_log("debug", message)

    @classmethod
    def info(cls, message):
        """Log an info message"""
        cls.add_to_log("info", message)

    @classmethod
    def warning(cls, message):
        """Log a warning message"""
        cls.add_to_log("warn", message)

    @classmethod
    def error(cls, message):
        """Log an error message"""
        cls.add_to_log("error", message)

    @classmethod
    def critical(cls, message):
        """Log a critical message"""
        cls.add_to_log("critical", message)

    @classmethod
    def get_log_directory(cls):
        """Get the current log directory path"""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "src" / "utils" / "log"

    @classmethod
    def cleanup_old_logs(cls, days_to_keep=30):
        """
        Clean up log files older than the specified number of days

        Args:
            days_to_keep (int): Number of days to keep log files (default: 30)
        """
        try:
            log_dir = cls.get_log_directory()
            if not log_dir.exists():
                return

            import time

            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    try:
                        log_file.unlink()
                    except Exception as e:
                        print(f"Failed to delete log file {log_file}: {e}")

        except Exception as e:
            print(f"Error during log cleanup: {e}")

    @classmethod
    def check_permissions(cls):
        """
        Check and report the current permission status of log directory and files.

        Returns:
            dict: Status information about permissions
        """
        try:
            log_dir = cls.get_log_directory()
            status = {
                "log_directory": str(log_dir),
                "directory_exists": log_dir.exists(),
                "directory_writable": False,
                "files": {},
            }

            if log_dir.exists():
                status["directory_writable"] = os.access(log_dir, os.W_OK)

                # Check individual log files
                for log_file in ["access.log", "error.log", "app.log"]:
                    file_path = log_dir / log_file
                    if file_path.exists():
                        status["files"][log_file] = {
                            "exists": True,
                            "readable": os.access(file_path, os.R_OK),
                            "writable": os.access(file_path, os.W_OK),
                            "permissions": oct(file_path.stat().st_mode)[-3:],
                        }
                    else:
                        status["files"][log_file] = {"exists": False}

            return status

        except Exception as e:
            return {"error": f"Failed to check permissions: {e}"}

    @classmethod
    def fix_all_permissions(cls):
        """
        Attempt to fix permissions for all log files and directories.

        Returns:
            bool: True if all permissions were fixed successfully
        """
        try:
            log_dir = cls.get_log_directory()

            if not log_dir.exists():
                cls._ensure_log_directory(log_dir)
                return True

            # Fix directory permissions
            try:
                cls._fix_permissions(log_dir, is_directory=True)
            except Exception as e:
                print(f"Could not fix directory permissions: {e}")
                return False

            # Fix file permissions
            success = True
            for log_file in log_dir.glob("*.log*"):
                try:
                    cls._fix_permissions(log_file, is_directory=False)
                except Exception as e:
                    print(f"Could not fix permissions for {log_file}: {e}")
                    success = False

            return success

        except Exception as e:
            print(f"Error fixing permissions: {e}")
            return False

    @classmethod
    def get_effective_log_directory(cls):
        """
        Get the actual log directory that will be used, considering permission constraints.
        This may differ from get_log_directory() if there are permission issues.

        Returns:
            Path: The effective log directory path
        """
        project_root = Path(__file__).parent.parent.parent
        preferred_log_dir = project_root / "src" / "utils" / "log"

        # Use the same logic as _ensure_log_directory to determine actual directory
        effective_dir = cls._ensure_log_directory(preferred_log_dir)
        return Path(effective_dir)

    @classmethod
    def diagnose_logging_issues(cls):
        """
        Comprehensive diagnostic tool for logging issues.

        Returns:
            dict: Detailed diagnostic information
        """
        diagnosis = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "preferred_directory": str(cls.get_log_directory()),
            "effective_directory": str(cls.get_effective_log_directory()),
            "permission_status": cls.check_permissions(),
            "current_user": os.getuid() if hasattr(os, "getuid") else "unknown",
            "current_group": os.getgid() if hasattr(os, "getgid") else "unknown",
            "umask": oct(os.umask(0o022)) if hasattr(os, "umask") else "unknown",
        }

        # Reset umask if we changed it
        if hasattr(os, "umask"):
            os.umask(0o022)

        # Test write capabilities
        try:
            test_logger = cls()
            test_logger._ensure_log_directory(cls.get_effective_log_directory())
            diagnosis["write_test"] = "success"
        except Exception as e:
            diagnosis["write_test"] = f"failed: {e}"

        return diagnosis
