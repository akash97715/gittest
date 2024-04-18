import json

parse_citations = lambda data: json.loads(data['citations']) if isinstance(data['citations'], str) else data['citations']
