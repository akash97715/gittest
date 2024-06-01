AWSTemplateFormatVersion: '2010-09-09'
Description: Child stack to provision Lambda functions and Step Function.

Parameters:
  Env:
    Type: String
  DefaultEnv:
    Type: String
  Name:
    Type: String
  CfnBucketName:
    Type: String
  StepFunctionDefinitionS3ObjKey:
    Type: String
  IngestionProcessTabularDataLambdaImageUri:
    Type: String
  IngestionProcessNonTabularDataLambdaImageUri:
    Type: String
  IngestionEmbeddingLambdaImageUri:
    Type: String
  IngestionStoreLambdaImageUri:
    Type: String
  IngestionInvokeLambdaImageUri:
    Type: String
  CostCenterID:
    Type: String
  PrimaryOwner:
    Type: String
  SecondaryOwner:
    Type: String

Resources:
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - sts:AssumeRole
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
                Resource: "*"

  StepFunctionExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - states.amazonaws.com
            Action:
              - sts:AssumeRole
      Policies:
        - PolicyName: StepFunctionExecutionPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: "*"
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource: "*"

  IngestionProcessTabularDataLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${Name}-ingestion-process-tabular-data"
      Role: !GetAtt LambdaExecutionRole.Arn
      PackageType: Image
      Code:
        ImageUri: !Ref IngestionProcessTabularDataLambdaImageUri
      MemorySize: 128
      Timeout: 300

  IngestionProcessNonTabularDataLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${Name}-ingestion-process-non-tabular-data"
      Role: !GetAtt LambdaExecutionRole.Arn
      PackageType: Image
      Code:
        ImageUri: !Ref IngestionProcessNonTabularDataLambdaImageUri
      MemorySize: 128
      Timeout: 300

  IngestionEmbeddingLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${Name}-ingestion-embedding"
      Role: !GetAtt LambdaExecutionRole.Arn
      PackageType: Image
      Code:
        ImageUri: !Ref IngestionEmbeddingLambdaImageUri
      MemorySize: 128
      Timeout: 300

  IngestionStoreLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${Name}-ingestion-store"
      Role: !GetAtt LambdaExecutionRole.Arn
      PackageType: Image
      Code:
        ImageUri: !Ref IngestionStoreLambdaImageUri
      MemorySize: 128
      Timeout: 300

  IngestionInvokeLambda:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "${Name}-ingestion-invoke"
      Role: !GetAtt LambdaExecutionRole.Arn
      PackageType: Image
      Code:
        ImageUri: !Ref IngestionInvokeLambdaImageUri
      MemorySize: 128
      Timeout: 300

  DocinsightIngestStateMachine:
    Type: "AWS::StepFunctions::StateMachine"
    DependsOn:
      - IngestionProcessTabularDataLambda
      - IngestionProcessNonTabularDataLambda
      - IngestionEmbeddingLambda
      - IngestionStoreLambda
    Properties:
      StateMachineName: !Sub ${Env}-vsl-${Name}-ingestion-process
      DefinitionS3Location:
        Bucket: !Ref CfnBucketName
        Key: !Ref StepFunctionDefinitionS3ObjKey
      DefinitionSubstitutions:
        IngestionProcessNonTabularDataLambdaArn: !GetAtt IngestionProcessNonTabularDataLambda.Arn
        IngestionEmbeddingLambdaArn: !GetAtt IngestionEmbeddingLambda.Arn
        IngestionStoreLambdaArn: !GetAtt IngestionStoreLambda.Arn
      RoleArn: !Sub "arn:aws:iam::${AWS::AccountId}:role/CUSPFE-ias-${Env}-vsl-${Name}-ingestion-process"

Outputs:
  IngestionProcessTabularDataLambdaArn:
    Description: ARN of the ingestion-process-tabular-data Lambda function
    Value: !GetAtt IngestionProcessTabularDataLambda.Arn
  IngestionProcessNonTabularDataLambdaArn:
    Description: ARN of the ingestion-process-non-tabular-data Lambda function
    Value: !GetAtt IngestionProcessNonTabularDataLambda.Arn
  IngestionEmbeddingLambdaArn:
    Description: ARN of the ingestion-embedding Lambda function
    Value: !GetAtt IngestionEmbeddingLambda.Arn
  IngestionStoreLambdaArn:
    Description: ARN of the ingestion-store Lambda function
    Value: !GetAtt IngestionStoreLambda.Arn
  IngestionInvokeLambdaArn:
    Description: ARN of the ingestion-invoke Lambda function
    Value: !GetAtt IngestionInvokeLambda.Arn
  DocinsightIngestStateMachineArn:
    Description: ARN of the Step Function state machine
    Value: !Ref DocinsightIngestStateMachine
