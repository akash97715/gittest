fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| sort @timestamp desc
| limit 1000
