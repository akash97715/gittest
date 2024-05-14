content_list = await content_fetcher.fetch_content_from_uuids_or_type(
            uuids,
            uuids_request.content_type.value,
            uuids_request.request_id
        )
