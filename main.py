The libzip package has below limitations identified:
Formdata endpoints are not supported – need for support
Any request that does not have a JSON payload fails to be metered (this includes not just GET/DELETE but also POST or PUT endpoints that have an optional payload) – need for support of endpoints that are metered even without a JSON payload
