{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": [
                "Service": "es.amazonaws.com",
				"AWS": "arn:aws:iam::420737321821:role/CUSPFE-ias-test-vsl-docinsight-opensearch-migration"
				],
            "Action": "sts:AssumeRole"
        }
    ]
}
