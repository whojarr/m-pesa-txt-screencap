import os
import boto3
import json
from flask import Flask, request, render_template
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

S3_BUCKET = os.environ['S3_BUCKET'];
SERVERLESS_STAGE = os.environ['SERVERLESS_STAGE'];
TEAMS_URL = os.environ['TEAMS_URL'];
APIKEY = os.environ['APIKEY'];

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

s3_client = boto3.client("s3")


def detect_text(photo, bucket):

#     print("detect_text({},{})".format(photo, bucket))

    client=boto3.client('rekognition')

    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})
                        
    textDetections=response['TextDetections']
    result_string = ""
#     print ('Detected text\n----------')
    for text in textDetections:
#             print ('Detected text:' + text['DetectedText'])
#             print ('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
#             print ('Id: {}'.format(text['Id']))
#             if 'ParentId' in text:
# #                 print ('Parent Id: {}'.format(text['ParentId']))
#             print ('Type:' + text['Type'])
#             print()
            if 'ParentId' in text:
                result_string += text['DetectedText']
                result_string += " "
    return result_string


def send_teams_message(title, summary, text):

    ''' Create the mapping to convert to json containing the teams message '''
    tdata = {}
    tdata['@context'] = "http://schema.org/extensions"
    tdata['@type'] = "MessageCard"
    tdata['themeColor'] = "00FF00"
    tdata['title'] = title
    tdata['summary'] = summary
    tdata['text'] = text

    ''' Send a teams formated dict to a teams channel '''
    response = requests.post(
        TEAMS_URL, data=json.dumps(tdata),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to Teams returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )

 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def s3_upload(inp_file_name, s3_bucket_name, inp_file_key, content_type):

    upload_file_response = s3_client.put_object(
        Body=inp_file_name,
        Bucket=s3_bucket_name,
        Key=inp_file_key,
        ContentType=content_type
    )
    return upload_file_response


@app.route("/", methods=["GET", "POST"])
def event():

    if request.method == "GET":

        return render_template("upload.html", **locals())

    if request.method == "POST":

        apikey = request.headers.get('X-API-Key');
        if not apikey == APIKEY:
            resp = app.response_class(
                response=json.dumps("unauthorised"),
                status=403,
                mimetype='application/json'
                )
            return resp

        posted = request.json
        print("Recieved:{}",format(posted))

        image_name = posted['image_name']
        result=detect_text(image_name,S3_BUCKET)
        print("Text detected: " + str(result))

        send_teams_message("p-mesa txt screen capture to text", "p-mesa txt screen capture to text", result)

        resp = app.response_class(
            response=json.dumps({"result": result}),
            status=200,
            mimetype='application/json'
        )
        return resp


@app.route("/upload/", methods=["POST"])
def upload_handler():

    if request.method == "POST" and 'file' in request.files:
        file_to_upload = request.files['file']
        content_type = request.mimetype
        if file_to_upload.filename == '':
            print("no uploade filename specified")
        if file_to_upload and allowed_file(file_to_upload.filename):
            file_name = secure_filename(file_to_upload.filename)
            upload_result = s3_upload(file_to_upload, S3_BUCKET, file_name,content_type )
            print(upload_result)

            result=detect_text(file_name,S3_BUCKET)
            print(result)

    resp = app.response_class(
        response=json.dumps({"result": result}),
        status=200,
        mimetype='application/json'
    )
    return resp


def main():

    bucket=S3_BUCKET
    photo='sample_1.jpeg'
    res=detect_text(photo,bucket)
    print("Text detected: " + str(res))


if __name__ == "__main__":
    main()

