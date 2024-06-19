---------------------------------------------------------------------------
PydanticUserError                         Traceback (most recent call last)
Cell In[7], line 8
      5 from IPython.display import Image, display
      6 from pydantic import BaseModel, root_validator
----> 8 class LambdaWrapper(BaseModel):
      9     """Wrapper for AWS Lambda SDK."""
     10     lambda_client: Any  #: :meta private:

Cell In[7], line 15
     12 awslambda_tool_name: Optional[str] = None
     13 awslambda_tool_description: Optional[str] = None
---> 15 @root_validator()
     16 def validate_environment(cls, values: Dict) -> Dict:
     17     try:
     18         import boto3

File c:\Users\akasdeep\Downloads\langgraphmain\agentsenv\Lib\site-packages\pydantic\deprecated\class_validators.py:249, in root_validator(pre, skip_on_failure, allow_reuse, *__args)
    247 mode: Literal['before', 'after'] = 'before' if pre is True else 'after'
    248 if pre is False and skip_on_failure is not True:
--> 249     raise PydanticUserError(
    250         'If you use `@root_validator` with pre=False (the default) you MUST specify `skip_on_failure=True`.'
    251         ' Note that `@root_validator` is deprecated and should be replaced with `@model_validator`.',
    252         code='root-validator-pre-skip',
    253     )
    255 wrap = partial(_decorators_v1.make_v1_generic_root_validator, pre=pre)
    257 def dec(f: Callable[..., Any] | classmethod[Any, Any, Any] | staticmethod[Any, Any]) -> Any:

PydanticUserError: If you use `@root_validator` with pre=False (the default) you MUST specify `skip_on_failure=True`. Note that `@root_validator` is deprecated and should be replaced with `@model_validator`.

For further information visit https://errors.pydantic.dev/2.7/u/root-validator-pre-skip
