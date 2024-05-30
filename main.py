push_metrics(req_arrival_time=request.headers["x_agw_request_time"],
                                    client_id=request.headers["x-agw-client_id"],
                                    api_id=request.headers["x_agw_api_id"],
                                    url=str(request.url),
                                    uom_val=total_pages,
                                    engine=rw.engine,
                                    purpose="openai")
