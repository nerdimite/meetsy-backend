# Lambda Layer Setup

This is a guide to setup the lambda layer for the insights API.

1. Run the following commands in your terminal to install the required packages in the `python` folder:
   ```bash
   mkdir python
   sudo service docker start
   sudo docker run --rm --volume=$(pwd):/lambda-build -w=/lambda-build lambci/lambda:build-python3.8 pip install -r requirements.txt --target python
   ```
2. Compress the `python` folder into a zip file.
3. Upload the zip file to AWS Lambda as a layer with compatible runtimes as `python3.8`.
