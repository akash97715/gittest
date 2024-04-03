{
    "Version": "2012-10-17",
    "Id": "Policy1568001010746",
    "Statement": [{
        "Sid": "Stmt1568000712531",
        "Effect": "Allow",
        "Principal": {
            "AWS": ["arn:aws:iam::808950231959:role/CUSPFE-ias-prod-vsl-doc-os-migration", "arn:aws:iam::808950231959:role/CUSPFE-ias-prod-vsl-doc-os-migration-role"]
        },
        "Action": "s3:*",
        "Resource": "arn:aws:s3:::test-docinsight-opensearch-migration"
    }, {
        "Sid": "Stmt1568001007239",
        "Effect": "Allow",
        "Principal": {
            "AWS": ["arn:aws:iam::808950231959:role/CUSPFE-ias-prod-vsl-doc-os-migration", "arn:aws:iam::808950231959:role/CUSPFE-ias-prod-vsl-doc-os-migration-role"]
        },
        "Action": "s3:*",
        "Resource": "arn:aws:s3:::test-docinsight-opensearch-migration/*"
    }]
}
 
 
{
 
            "Sid": "DelegateS3Access",
 
            "Effect": "Allow",
 
            "Principal": {
 
                "AWS": "arn:aws:iam::808950231959:role/PFE-RAPID-CUSTOMER-ADMIN-SSO"
 
            },
