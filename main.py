fields @timestamp, @message, @logStream, @log
| parse @timestamp "*T*Z" as date, time
| filter date = '2024-05-15' and time >= '12:46:00' and time <= '12:48:00'
| filter @message like /localhost/ and @message like /textract/
| sort @timestamp desc
| limit 1000




fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| filter @timestamp >= '2024-05-15T12:46:00.000+05:30' and @timestamp <= '2024-05-15T12:48:00.000+05:30'
| sort @timestamp desc
| limit 1000
