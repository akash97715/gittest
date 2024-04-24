    def serialize(self, obj):
        """Helper function to serialize objects to JSON."""
        if isinstance(obj, Document) or not isinstance(obj, str):
           
            return json.dumps(dict(obj))
        else:
           
            return json.dumps(obj)
 
    def deserialize(self, data):
        """Helper function to deserialize JSON to Python objects."""
        # Implement logic here if you need to deserialize into Document objects
        return json.loads(data)
