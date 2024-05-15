fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| filter @timestamp >= '2024-05-15T07:16:00.000Z' and @timestamp <= '2024-05-15T07:18:00.000Z'
| sort @timestamp desc
| limit 1000
