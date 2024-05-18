def fetch_actual_doc(client_id: str, grabber: list, db: Session):
    try:
        val_to_fetch = grabber
        max_timestamp_subquery = (
            db.query(
                DataIngestionStatusTableNew.document,
                func.max(DataIngestionStatusTableNew.completed_errored_ts).label(
                    "max_timestamp"
                ),
            )
            .filter(
                DataIngestionStatusTableNew.client_id == client_id,
                DataIngestionStatusTableNew.document.in_(val_to_fetch),
                DataIngestionStatusTableNew.status == "Completed",
                DataIngestionStatusTableNew.is_file_deleted == False,
            )
            .group_by(DataIngestionStatusTableNew.document)
            .subquery()
        )
        files = (
            db.query(DataIngestionStatusTableNew)
            .join(
                max_timestamp_subquery,
                and_(
                    DataIngestionStatusTableNew.document
                    == max_timestamp_subquery.c.document,
                    DataIngestionStatusTableNew.completed_errored_ts
                    == max_timestamp_subquery.c.max_timestamp,
                ),
            )
            .filter(
                DataIngestionStatusTableNew.client_id == client_id,
                DataIngestionStatusTableNew.document.in_(val_to_fetch),
                DataIngestionStatusTableNew.status == "Completed",
            )
            .all()
        )
 
        if len(files) != 0:
            file_safe_values_custom = [file.document_md5 for file in files]
            return file_safe_values_custom
        else:
            logger.info("No Document Found")
 
        return []
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Error while fetching document")
 
 
def fetch_actual_md5(md5_list: list, indices: list, db: Session, client_id_list: list):
    try:
        # Filter for specific indexes
        files = (
            db.query(DataIngestionStatusTableNew)
            .filter(
                DataIngestionStatusTableNew.client_id.in_(client_id_list),
                DataIngestionStatusTableNew.index.in_(indices),
                DataIngestionStatusTableNew.document_md5.in_(md5_list),
                DataIngestionStatusTableNew.status == "Completed",
                DataIngestionStatusTableNew.is_file_deleted == False,
            )
            .all()
        )
 
        if len(files):
            document_md5_list = list(set([file.document_md5 for file in files]))
            return document_md5_list
        else:
            logger.info("No Documents MD5 Found")
 
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail="Error while fetching actual md5")
