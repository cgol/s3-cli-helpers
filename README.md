# s3-cli-helpers
Helpers to create notification and lifecycle policies in JSON for S3 via the command line interface

The issue with the S3API is that the lifecycle and notification policies only allow complete replacement of the whole policy. Where there are a number of polices with different prefixes one needs to obtain the current policy, and then replace or add the relevant part for the prefix whilst retaining other parts of the policy relating to other prefixes.


## bash script example of using a helper:

oldNotificationFile=$(mktemp)
aws s3api get-bucket-notification-configuration --bucket ${Bucket} --profile ${Profile} >$oldNotificationFile 
 
if [[ -s $oldNotificationFile ]]; then
    oldpolicy="-e $oldNotificationFile"
fi
    
newNotificationFile=$(mktemp)

$(python3 ./bucket-notification-policy-helper.py -p ${Prefix} ${oldpolicy} -t ${TopicArn} >$newNotificationFile)

aws s3api put-bucket-notification-configuration --bucket ${Bucket} --profile ${Profile} --notification-configuration "file://${newNotificationFile}"
