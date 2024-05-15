fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| filter @timestamp >= '2024-05-15T00:00:00.000+05:30' and @timestamp <= '2024-05-15T23:59:59.999+05:30'
| sort @timestamp desc
| limit 1000
