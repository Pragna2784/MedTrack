import boto3

# Create SNS client
sns = boto3.client('sns', region_name='us-east-1')

# Replace this with your actual SNS Topic ARN
TOPIC_ARN = "YOUR_SNS_TOPIC_ARN"


# --------------------------------
# SEND NOTIFICATION FUNCTION
# --------------------------------
def send_notification(message):

    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=message,
        Subject="MedTrack Update"
    )