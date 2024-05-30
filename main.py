Statement:
  - Effect: Allow
    Action:
      - logs:CreateLogGroup
      - logs:CreateLogStream
      - logs:PutLogEvents
    Resource:
      - !Sub "arn:aws:logs:*:${AWS::AccountId}:log-group:/aws/lambda/${Env}-vsl-${Name}-ingestion-embedding*"
      - !Sub "arn:aws:logs:*:${AWS::AccountId}:log-group:/aws/lambda/${Env}-vsl-${Name}-ingestion-store*"
      - !Sub "arn:aws:logs:*:${AWS::AccountId}:log-group:/aws/states/${Env}-vsl-${Name}-ingestion*"
  - Effect: Allow
    Action:
      - ec2:DescribeNetworkInterfaces
      - ec2:CreateNetworkInterface
      - ec2:DeleteNetworkInterface
      - ec2:DescribeInstances
      - ec2:AttachNetworkInterface
    Resource: "*"
  - Effect: Allow
    Action:
      - "secretsmanager:GetSecretValue"
    Resource: !Sub "arn:aws:secretsmanager:*:${AWS::AccountId}:secret:${Env}-vsl-${Name}-secrets*"
  - Effect: Allow
    Action:
      - "lambda:InvokeFunction"
    Resource:
      - !Sub "arn:aws:lambda:*:${AWS::AccountId}:function:${Env}-vsl-${Name}-ingestion-process"
      - !Sub "arn:aws:lambda:*:${AWS::AccountId}:function:${Env}-vsl-${Name}-ingestion-embedding"
      - !Sub "arn:aws:lambda:*:${AWS::AccountId}:function:${Env}-vsl-${Name}-ingestion-store"
  - Effect: Allow
    Action:
      - sqs:*
      - sqs:GetQueueUrl
    Resource: !Sub "arn:aws:sqs:*:${AWS::AccountId}:${Env}-vsl-${Name}-*"
