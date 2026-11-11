import functools
from utils.errors.error_codes import ErrorCode
from utils.errors.error_log import log_error
from utils.errors.http_status import HttpStatusCode
import inspect
import os
from models.custome_app_exepction import CustomAppException


def handle_errors(message: str = None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            
            except Exception as e:
                # Get exact file name and function name automatically
                file_name = os.path.basename(inspect.getfile(func))
                func_name = func.__name__

                log_error(file_name, func_name, str(e))
                raise CustomAppException(
                    message=f" [{file_name} -> {func_name}] {message or func_name} error: {str(e)}",
                    code=ErrorCode.INTERNAL_SERVER_ERROR,
                    status_code=HttpStatusCode.INTERNAL_SERVER_ERROR,
                )
        return wrapper
    return decorator