1. Create a lambda in AWS web interface (or AWS CLI).
    - on the Lambda site, click the orange create function button
    - Enter a name for your lambda
    - Click the dropdown for change default execution role, select use existing role, select 334s25_lambda_execution_s3
    - Click create function
2. Create a trigger for the lambda to update on s3 bucket.
    - In the lambda interface, click the add trigger box
    - On trigger configuration dropdown, search s3 and select
    - Under bucket, select the bucket you wish to update on
    - By default, event type is on all files added. This can be changed in the dropdown
    - Prefixes and Suffixes can help update only in a certain "folder" or for certain file types
    - click the checkbox for acknowledging potential recursive invocation
    - click the add button at the bottom