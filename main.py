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
