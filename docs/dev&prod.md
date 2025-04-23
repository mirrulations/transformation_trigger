lambda functions:
the development environment can be run through sam and unit tests. See running_locally.

- To build the application: `sam build`
- To run locally: `sam local start-api`
- To run unit tests: `pytest tests/`

the production environment can be deployed using sam deploy. AWS lambda cli is also a possiblitity, but for
simplicity sake, we will just use sam deploy for the time being. The github actions can do CD by using this.

Commands for production:

- To package the application: `sam package --template-file template.yaml --s3-bucket <your-bucket-name> --output-template-file packaged.yaml`
- To deploy the application: `sam deploy --template-file packaged.yaml --stack-name <your-stack-name> --capabilities CAPABILITY_IAM`
