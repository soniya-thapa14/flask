from flask import Flask, request
import pandas as pd
import os
import requests
from scr import *
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

AXISID_API_URL = 'https://axisid.e-billingnepal.com/mail/send_email'

SMS_AUTH_TOKEN = '0110e31d1b3c2e98e11705a1c22b49221e99f62e3cf95f09840850b4c379982c'


def send_sms(auth_token, phone_numbers, message):
    """Send SMS using Aakash SMS API"""
    return requests.post(
        "https://sms.aakashsms.com/sms/v3/send",
        data={'auth_token': auth_token, 'to': phone_numbers, 'text': message}
    )

def send_whatsapp_via_infobip(to, message_text):
    import http.client
    import json

    conn = http.client.HTTPSConnection("d9x6lr.api.infobip.com")
    payload = json.dumps({
        "messages": [
            {
                "from": "447860099299",
                "to": "9779841296586",
                "messageId": "43b6b596-8a2b-4e95-9864-0c799b2c9d0c",
                "content": {
                    "templateName": "test_whatsapp_template_en",
                    "templateData": {
                        "body": {
                            "placeholders": ["Axis"]
                        }
                    },
                    "language": "en"
                }
            }
        ]
    })
    headers = {
        'Authorization': 'App ca86ea5cfe06d52bba70b13fccf03ba7-d6dbcbde-531b-4adc-8cfb-f23015856092',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/whatsapp/1/message/template", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

def send_email_via_axisid(company_name, To, subject, body, regards):
    headers = {
    "Origin": "http://127.0.0.1:5000",  
    "Content-Type": "application/json"
    }

    email_data = {
        'company_name': company_name,
        'to': To,
        'subject': subject,
        'body': body,
        'regards':regards   
    }

    response = requests.post(AXISID_API_URL, headers=headers, json=email_data,)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    return response




@app.route('/send-notifications', methods=['POST'])
def send_notifications():
    try:
        file = request.files['file']
        if not file:
            return "❌ Missing file."

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_excel(filepath)
        pdf_path =generate_pdf()
        url = f"https://ersalugupta.com.np/sms/pdf/{pdf_path}"
        subject = "Welcome to Our Service!"
        body = (
            "We're excited to have you on board. This is just a warm welcome to let you know "
            "that you're now part of our growing community.\n\n"
            "If you ever have any questions or need support, feel free to reach out.\n\n"
            f"download pdf from this link: {url}\n\n"
            "Best regards,\nThe Team"
        )

        regards = 'Regards team'
        company_name = 'axis'
        message_template = (
            "Hi {name}, welcome to our service! We're excited to have you onboard. "
            "Let us know if you need any assistance. 😊\n"
            f"{url}"
        )

        for _, row in df.iterrows():            
            name = row.get('First name', 'Friend')

            # Send Email
            if 'Recipient' in row and pd.notnull(row['Recipient']):
                To = row['Recipient']
                response = send_email_via_axisid(company_name, To, subject, body, regards)
                try:
                    response_data = response.json()
                    print(f"📧 Email response for {To}: {response_data}")
                except ValueError as e:
                    print("⚠️ Email failed!")
                    print("🔍 Status code:", response.status_code)
                    print("🔍 Response text:", response.text)
                            


            # Send SMS and WhatsApp
            if 'phone' in row and pd.notnull(row['phone']):
                phone_number = str(row['phone']).strip()

                # SMS
                sms_response = send_sms(SMS_AUTH_TOKEN, phone_number, "Welcome to our service! We're excited to have you with us.\n\n"
                                        f"{url}")
                print(f"📱 SMS sent to {phone_number}: {sms_response.status_code}, {sms_response.text}")

                # WhatsApp
                try:
                    message_text = message_template.format(name=name)
                    send_whatsapp_via_infobip(phone_number, message_text)
                    print(f"💬 WhatsApp sent to {phone_number}")
                except Exception as e:
                    print(f"❌ WhatsApp failed for {phone_number}: {str(e)}")

        return "✅ Notifications processed successfully!"


    except Exception as e:
        return f"❌ Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)