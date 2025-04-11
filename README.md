# transformation_trigger

A repo for the mirrulations trigger to transform data

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- lambda_functions - Code for the application's Lambda functions.
- common_layer - a submodule that contains functions to get secrets and connect to databases for the lambdas.
- events - Invocation events that you can use to invoke the functions.
- tests - Unit tests for the application code.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions, SNS trigger, S3, and secrets manager. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Additional Documentation

[Lambda Trigger Creation Guide](docs/lambda_trigger_documentation.md)\
[Moto Lambda Mocking Guide](docs/lambdamocking.md)\
[Moto S3 Mocking Guide](docs/s3mocking.md)\
[Flake8 Installation & Setup Guide](docs/static_analysis.md)\
[Local Dev / Execution Guide](docs/running_locally.md)\
[Adding New Lambda Functions Guide](docs/adding_new_lambdas.md)

## Get Started

- To start, download the AWS SAM CLI [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html#install-sam-cli-instructions).
- We utilized Docker for the containerized deployment of the infrastructure, download Docker Desktop [here](https://www.docker.com/products/docker-desktop/)

- Clone this repository
- `cd` into dev-env
- Clone the common layer ingest functions by running `git submodule update --init`
  - Make sure to occasionally rerun `git submodule update` whenever there are changes to the ingest repository!

Refer to the [running locally](docs/running_locally.md) documentation to build and run the stack in your local environment

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.
