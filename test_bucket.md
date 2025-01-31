The bucket is called etllambdatest. 
https://us-east-1.console.aws.amazon.com/s3/buckets/etllambdatest

It is currently not open to public access, but this can be changed if it 
is required.

This was a separate s3 bucket created for the ETL lambda trigger testing, 
in order to not interfere with the s3 bucket redesign/testing. This bucket 
will be watched by our lambda function and be triggered on file add
(hopefully). 
