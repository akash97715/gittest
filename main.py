result = json.loads(response_data.get('result', '{}')) if isinstance(response_data.get('result'), str) else response_data.get('result', {})
logger.info(f"Parsed result: {result}")  # Check what this contains
