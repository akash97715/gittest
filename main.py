@router.get(
    "/ingestion-info",
    status_code=200,
    tags=["API Module Service"],
    description="This endpoint provides the list of documents used by the given client",
    response_model=Dict[str, Union[List[IngestionInfoResponse], int, str]],
)
@async_token_validation_and_metering()
async def get_ingestion_info(
    request: fastapi_request,
    db: Session = Depends(get_db),
    page_limit: Optional[int] = 25,
    request_id: Optional[str] = '',
    page_number: Optional[int] = 1,
    sort_order: Order_By = Order_By.ASC,
    status: Optional[StatusList] = None,
 
    is_file_deleted: Optional[bool] = None,
):
    try:
        logger.info("Fetching client header")
        client_id = (
            request.headers.get("x-agw-client_id")
            if request.headers.get("x-agw-client_id") is not None
            else None
        )
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
            print("fetched record",record)
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
                    table_figure_metadata=record.table_figure_metadata
                )
            else:
                raise HTTPException(
                    status_code=404, detail="No record found with the provided request_id"
                )
        if page_number >= 1:
            if page_number > 1 and page_limit is None:
                logger.error("Pa
