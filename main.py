{
  "Comment": "State Machine to ensure all embeddings are created for parquet file",
  "StartAt": "ProcessParquetFile",
  "States": {
    "ProcessParquetFile": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:ProcessParquetLambda",
      "ResultPath": "$.processResult",
      "Next": "CheckFileType"
    },
    "CheckFileType": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.processResult.fileType",
          "StringEquals": "parquet",
          "Next": "LoadParquetAndProcess"
        },
        {
          "Or": [
            {
              "Variable": "$.processResult.fileType",
              "StringEquals": "csv"
            },
            {
              "Variable": "$.processResult.fileType",
              "StringEquals": "xlsx"
            }
          ],
          "Next": "Success"
        }
      ],
      "Default": "Fail"
    },
    "LoadParquetAndProcess": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:ProcessLambda",
      "ResultPath": "$.lambdaResult",
      "Next": "CheckCompletion"
    },
    "CheckCompletion": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.lambdaResult.complete",
          "BooleanEquals": true,
          "Next": "Success"
        },
        {
          "Variable": "$.lambdaResult.complete",
          "BooleanEquals": false,
          "Next": "LoadParquetAndProcess"
        }
      ],
      "Default": "Fail"
    },
    "Success": {
      "Type": "Succeed"
    },
    "Fail": {
      "Type": "Fail",
      "Error": "ProcessFailed",
      "Cause": "The embeddings creation process failed."
    }
  }
}
