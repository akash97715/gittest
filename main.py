 [await request_response_metering(
                    request,
                    r_parent_wf_req_id=request_id,
                    r_vendor_id=vendors.AZURE
                    if engine.startswith("gpt")
                    else vendors.AWS,
                    r_uom_id=uom.TOTAL_TOKENS,
                    r_uom_val=token_consumed,
                )                
 
                [
                    push_metrics(
                        req_arrival_time=request.headers["x_agw_request_time"],
                        client_id=request.headers["x-agw-client_id"],
                        api_id=request.headers["x_agw_api_id"],
                        url=str(request.url),
                        uom_val=param["total_token"],
                        engine=param["engine"],
                        purpose=(
                            "openai"
                            if param["engine"].startswith(("gpt", "text"))
                            else "bedrock"
                        ),
                    )
                    for param in metering_dict
                ]
