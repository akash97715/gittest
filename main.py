AWSTemplateFormatVersion: '2010-09-09'
Resources:
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: [lambda.amazonaws.com]
            Action: ['sts:AssumeRole']
      Policies:
        - PolicyName: LambdaExecutionPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: '*'

  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        ZipFile: |
          import json
          def lambda_handler(event, context):
              # Your Lambda function logic here
              return {
                  'statusCode': 200,
                  'body': json.dumps('Hello from Lambda!')
              }
      Handler: index.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Runtime: python3.8
      Timeout: 120  # Adjust based on your expected execution time

  StepFunctionsExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: [states.amazonaws.com]
            Action: ['sts:AssumeRole']
      Policies:
        - PolicyName: StepFunctionsLambdaInvocationPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource: !GetAtt MyLambdaFunction.Arn

  MyStateMachine:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      DefinitionString:
        !Sub |
          {
            "Comment": "State machine to ensure 99 parallel Lambda executions",
            "StartAt": "DistributeTasks",
            "States": {
              "DistributeTasks": {
                "Type": "Map",
                "InputPath": "$.payloads",
                "ItemsPath": "$",
                "MaxConcurrency": 99,
                "Iterator": {
                  "StartAt": "InvokeLambda",
                  "States": {
                    "InvokeLambda": {
                      "Type": "Task",
                      "Resource": "${MyLambdaFunction.Arn}",
                      "End": true
                    }
                  }
                },
                "End": true
              }
            }
          }
      RoleArn: !GetAtt StepFunctionsExecutionRole.Arn
