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
    request_id: str,
    db: Session = Depends(get_db),
    page_limit: Optional[int] = 25,
   
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
        client_id_list = await client_id_info(client_id=client_id, db=db)
 
 
        if request_id:  # Check if request_id is provided in the query
            logger.info(f"Fetching record for request_id: {request_id}")
            record = (
                db.query(DataIngestionStatusTableNew)
                .filter(
                    DataIngestionStatusTableNew.request_id == request_id
                   
                )
                .first()
            )
            logger.info(f"Fetching client info for {record}")
            print("fetched record",record)
            document_list=[]
            if record:
                document_list.append(
                    IngestionInfoResponse(
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
                )
               
               
                return {
                    "ingestion_data": document_list,
                   
                    }
            else:
                raise HTTPException(
                    status_code=404, detail="No record found with the provided request_id"
                )
        if page_number >= 1:
            if page_number > 1 and page_limit is None:
                logger.error("Page limit is also required with page number")
                raise HTTPException(
                    status_code=400,
                    detail="Page limit is also required with page number",
                )
            elif page_limit is not None and page_limit <= 0:
                logger.error("Page limit cannot be less than 1")
                raise HTTPException(
                    status_code=400, detail="Page limit cannot be less than 1"
                )
            elif page_limit is not None and page_limit > 1000:
                logger.error("Page limit cannot be greater than 1000")
                raise HTTPException(
                    status_code=400, detail="Page limit cannot be greater than 1000"
                )
        elif page_number < 1:
            logger.error("Page number cannot be less than 1")
            raise HTTPException(
                status_code=400, detail="Page number cannot be less than 1"
            )
 
        # Apply ordering and sorting
        order_column = DataIngestionStatusTableNew.modified_ts
        if sort_order == Order_By.DESC:
            order_column = desc(order_column)
 
        client_id_list = await client_id_info(client_id=client_id, db=db)
        query = (
            db.query(DataIngestionStatusTableNew)
            .filter(DataIngestionStatusTableNew.client_id.in_(client_id_list))
            .order_by(order_column)
        )
 
        # Applying status filter if provided
        if status:
            query = query.filter(
                func.lower(DataIngestionStatusTableNew.status) == status.lower()
            )
 
        # Applying is_file_deleted filter if provided
        if is_file_deleted is not None:
            query = query.filter(
                DataIngestionStatusTableNew.is_file_deleted == is_file_deleted
            )
 
        total_count = query.count()
 
        # Calculate total number of pages based on page_limit and total_count
        page_size = -(
            -total_count // page_limit
        )  # Ceiling division to get a positive integer
 
        # Apply pagination
        if page_limit is not None:
            start_index = (page_number - 1) * page_limit
            end_index = start_index + page_limit
            query = query.offset(start_index).limit(page_limit)
 
        ingestion_info = query.all()
        ingestion_data = []
 
        if len(ingestion_info):
            logger.info(f"Fetching details containing {total_count} entries")
            for row in ingestion_info:
                ingestion_data.append(
                    IngestionInfoResponse(
                        request_id=row.request_id,
                        index=row.index,
                        document_name=row.document,
                        document_md5=row.document_md5,
                        attached_metadata=row.attached_metadata,
                        status=row.status,
                        error_msg=row.error_message,
                        is_file_deleted=row.is_file_deleted,
                        created_ts=row.created_ts,
                        queued_ts=row.queued_ts,
                        inprogress_ts=row.inprogress_ts,
                        completed_errored_ts=row.completed_errored_ts,
                        modified_ts=row.modified_ts,
                    )
                )
        else:
            logger.error("No records found in DB")
 
        # Check if requested page_number exceeds page_size
        if page_number > page_size:
            logger.error("Requested page_number exceeds available page_size.")
            raise HTTPException(
                status_code=400,
                detail="Requested page_number exceeds available page_size.",
            )
 
        # Return a dictionary containing both ingestion data and pagination information
        return {
            "ingestion_data": ingestion_data,
            "total_count": total_count,
            "page_number": page_number,
            "page_limit": page_limit,
            "page_size": page_size,
        }
    except Exception as e:
        raise e
