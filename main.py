  IngestionStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Ref IngestionNestedTemplateURL
      TimeoutInMinutes: 60
      Parameters:
        Env: !Ref Env
        DefaultEnv: !Ref DefaultEnv
        Name: !Ref Name
        CfnBucketName: !Ref CfnBucketName
        StepFunctionDefinitionS3ObjKey: !Ref StepFunctionDefinitionS3ObjKey
        IngestionProcessTabularDataLambdaImageUri: !Ref IngestionProcessTabularDataLambdaImageUri
        IngestionProcessNonTabularDataLambdaImageUri: !Ref IngestionProcessNonTabularDataLambdaImageUri
        IngestionEmbeddingLambdaImageUri: !Ref IngestionEmbeddingLambdaImageUri
        IngestionStoreLambdaImageUri: !Ref IngestionStoreLambdaImageUri
        IngestionInvokeLambdaImageUri: !Ref IngestionInvokeLambdaImageUri
        CostCenterID: !Ref CostCenterID
        PrimaryOwner: !Ref PrimaryOwner
        SecondaryOwner: !Ref SecondaryOwner
