fields @timestamp, @message, @logStream, @log
| filter @message like /localhost/ and @message like /textract/
| parse @timestamp "*T*:*:*.*+05:30" as date, time, rest
| filter time >= '12:46:00' and time <= '12:48:00'
| sort @timestamp desc
| limit 1000
