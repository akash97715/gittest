@root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        values["openai_proxy"] = get_from_dict_or_env(values, "openai_proxy", "OPENAI_PROXY", default="")
        client_params = {
            "api_key": values["bearer_token"],
            "organization": values["x_vsl_client_id"],
            "base_url": None,
            "timeout": values["request_timeout"],
            "max_retries": values["max_retries"],
            "default_headers": values["default_headers"],
            "default_query": values["default_query"],
        }
        if not values.get("client"):
            try:
                import openai
            except ImportError as e:
                raise ImportError(
                    "Could not import openai python package. Please install it with `pip install openai`."
                ) from e
            values["client"] = openai.OpenAI(**client_params).chat.completions
Collapse
has context menu


has context menu
