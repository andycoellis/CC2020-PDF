import boto3
from botocore.exceptions import ClientError
import os
import sys
import json
import uuid
from urllib.parse import unquote_plus
from jinja2 import Environment, FileSystemLoader
from fpdf import FPDF, HTMLMixin 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

s3_client = boto3.client('s3')

class MyFPDF(FPDF, HTMLMixin):
    pass

def convert_pdf(json_path, pdf_path, bucket, tmpkey, key):
	print('#### ENTERING CONVERSION')
	print(f"JSON PATH {json_path}")
	print(f"PDF PATH {pdf_path}")
	print(f"BUCKET {bucket}")
	print(f"TMP KEY {tmpkey}")
	print(f"KEY {key}")
	env = Environment(loader=FileSystemLoader('.'))
	template = env.get_template("myreport.html")

	json_file = open(json_path, "r")
	data = json.load(json_file)

	empID = ""
	empName = ""
	companyName = ""
	companyABN = ""
	payPeriod = ""
	pay = ""
	payYTD = ""
	tax = ""
	baseHours = ""
	satHours = ""
	sunHours = ""
	senderAddress = ""
	compAddress = ""


	for d in data['Details']:
		empID = d['EmpId']
		empName = d['EmployeeName']
		companyName = d['CompanyName']
		companyABN = d['CompanyABN']
		payPeriod = d['PayPeriod']
		pay = d['Pay']
		payYTD = d['PayYTD']
		tax = d['Tax']
		baseHours = d['BaseHours']
		satHours = d['SatHours']
		sunHours = d['SunHours']
		senderAddress = d['SenderAddress'];
		compAddress = d['ReceiverAddress']

	template_vars = {"company_name": companyName, "company_abn": companyABN, "employee_name": empName, "employee_id": empID,
					"base_hours": baseHours, "sat_hours": satHours, "sun_hours": sunHours, "pay_period": payPeriod, 
					"pay_ytd": payYTD, "pay": pay, "tax": tax}

	html_out = template.render(template_vars)

	pdf = MyFPDF()
	pdf.add_page()
	pdf.write_html(html_out)
	pdf.output(pdf_path, 'F')
	s3_client.upload_file(pdf_path, '{}-pdf'.format(bucket), tmpkey)
	bucket = 'cc2020-drop-box-pdf'
	temporaryKey = key.replace('.json', '.pdf') 
	tempkey = temporaryKey.replace('/', '')
	download_path = '/tmp/{}{}'.format(uuid.uuid4(), tempkey)  
	s3_client.download_file(bucket, temporaryKey, download_path)
	sendEmail(senderAddress, compAddress, empName, empID, companyName, download_path)


def sendEmail(sender, receiver, empName, empId, companyName, filePath):
	print('### ENTERING SEND MAIL')
	# SENDER = sender
	SENDER = "andycoellis@gmail.com"

	# RECIPIENT = receiver
	RECIPIENT = "andrew.co.ellis@gmail.com"

	AWS_REGION = "us-east-1"

	SUBJECT = "New Payslip for "+empName+", "+empId

	print(f"filePath: {filePath}")
	ATTACHMENT = filePath

	BODY_TEXT = ("Dear "+companyName+"\r\n\n"
	             "There is a newly created payslip for "+empName+", "+empId+"."
	            )       

	CHARSET = "utf-8"

	client = boto3.client('ses',region_name=AWS_REGION)

	msg = MIMEMultipart('mixed')
	msg['Subject'] = SUBJECT 
	msg['From'] = SENDER 
	msg['To'] = RECIPIENT

	msg_body = MIMEMultipart('alternative')

	textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)

	msg_body.attach(textpart)

	att = MIMEApplication(open(ATTACHMENT, 'rb').read())

	att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))

	msg.attach(msg_body)

	msg.attach(att)
	print(f"Message to {msg['Subject']}")
	try:
	    #Provide the contents of the email.
	    response = client.send_raw_email(
	        Source=SENDER,
	        Destinations=[
	            RECIPIENT
	        ],
	        RawMessage={
	            'Data':msg.as_string(),
	        }
	    )
	except ClientError as e:
	    print(e.response['Error']['Message'])
	else:
	    print("Email sent! Message ID:"),
	    print(response['MessageId'])


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        print('### BUCKET NAME')
        print(bucket)
        key = unquote_plus(record['s3']['object']['key'])
        print('#### BUCKET KEY')
        print(key)
        tmpkey = key.replace('/', '')
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)  
        tmpkey = key.replace('.json', '.pdf')
        upload_path = '/tmp/pdf-{} '.format(tmpkey)
        s3_client.download_file(bucket, key, download_path)
        convert_pdf(download_path, upload_path, bucket, tmpkey, key)
