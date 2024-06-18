df['embedding'] = df['embedding'].apply(lambda x: x[0] if isinstance(x, list) and len(x) == 1 and isinstance(x[0], list) else x)
