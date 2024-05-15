fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| filter @timestamp >= '2024-05-15T12:46:00Z' and @timestamp <= '2024-05-15T12:48:00Z'
| sort @timestamp desc
| limit 1000
