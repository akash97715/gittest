PS D:\summarize-lambda\lambda-env\Lib\site-packages> Compress-Archive -Path * -DestinationPath D:\summarize-lambda\function.zip -ForceCompress-Archive -Path * -DestinationPath D:\summarize-lambda\function.zip -Force
Compress-Archive : Cannot bind parameter because parameter 'Path' is specified more than once. To provide multiple
values to parameters that can accept multiple values, use the array syntax. For example, "-parameter
value1,value2,value3".
At line:1 char:99
+ ... D:\summarize-lambda\function.zip -ForceCompress-Archive -Path * -Dest ...
+                                                             ~~~~~
    + CategoryInfo          : InvalidArgument: (:) [Compress-Archive], ParameterBindingException
    + FullyQualifiedErrorId : ParameterAlreadyBound,Compress-Archive
 
PS D:\summarize-lambda\lambda-env\Lib\site-packages>
