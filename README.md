## COSC2626 Cloud Computing Assignment 02

## AWS Lambda Function

*RMIT University Melbourne*
<br>**group members:**
> Andrew Ellis - s3747746
<br>Shrey Parekh - s3710669

### Lambda Features
**Python Scipt with HTML template:** 
>+ *Function Handler*
>+ *Publish and Retrieve Data from AWS S3 Bucket*
>+ *Convert JSON to PDF*
>+ *Send Email with AWS SES (simple email service)*

#### Notes
>This Python script utilises **AWS Lambda** function handlers to retrieve a JSON object form a designated **S3 Bucket** convert to a PDF, store the PDF in another S3 bucket then forward the PDF to **AWS SES.** 

#### Packages
- boto3
- json
- uuid
- fpdf
- email.mime
- jinja2
