async def get_ingestion_info(
    request: fastapi_request,
    db: Session = Depends(get_db),
    request_id: Optional[str] = None,  # Add request_id as an optional parameter
    page_limit: Optional[int] = 25,
    page_number: Optional[int] = 1,
    sort_order: Order_By = Order_By.ASC,
    status: Optional[StatusList] = None,
    is_file_deleted: Optional[bool] = None,
):
    try:
        logger.info("Fetching client header")
        client_id = request.headers.get("x-agw-client_id")

        if not client_id:
            raise HTTPException(
                status_code=400, detail="Client Id is not sent in headers"
            )

        if request_id:  # Check if request_id is provided in the query
            logger.info(f"Fetching record for request_id: {request_id}")
            record = (
                db.query(DataIngestionStatusTableNew)
                .filter(DataIngestionStatusTableNew.request_id == request_id)
                .first()
            )
            if record:
                return IngestionInfoResponse(
                    request_id=record.request_id,
                    index=record.index,
                    document_name=record.document,
                    document_md5=record.document_md5,
                    attached_metadata=record.attached_metadata,
                    status=record.status,
                    error_msg=record.error_message,
                    is_file_deleted=record.is_file_deleted,
                    created_ts=record.created_ts,
                    queued_ts=record.queued_ts,
                    inprogress_ts=record.inprogress_ts,
                    completed_errored_ts=record.completed_errored_ts,
                    modified_ts=record.modified_ts,
                )
            else:
                raise HTTPException(
                    status_code=404, detail="No record found with the provided request_id"
                )

        # Rest of your original code here to handle pagination and other filtering if no request_id is provided
        # ...
        
    except Exception as e:
        raise e
