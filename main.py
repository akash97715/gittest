return generic_exception_handler(exc, request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\opensearchindexfix\vessel-services\docinsight\app\utils\universal_exceptions.py", line 58, in generic_exception_handler
    pre_formatted_exc = str(exc).replace("\n", "\r")
                        ^^^^^^^^
  File "pydantic\error_wrappers.py", line 71, in pydantic.error_wrappers.ValidationError.__str__
  File "pydantic\error_wrappers.py", line 63, in pydantic.error_wrappers.ValidationError.errors
  File "C:\Program Files\Python311\Lib\typing.py", line 1272, in __getattr__
    raise AttributeError(attr)
AttributeError: __pydantic_model__
