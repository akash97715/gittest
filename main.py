content_list = await content_fetcher.fetch_content_from_uuids_or_type(
    uuids,
    uids_request.content_type.value if uids_request.content_type is not None else None,
    uuids_request.request_id
)
