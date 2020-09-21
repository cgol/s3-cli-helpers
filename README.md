# s3-cli-helpers
Helpers to create notification and lifecycle policies in JSON for S3 via the command line interface

The issue with the S3API is that the lifecycle and notification policies only allow complete replacement of the whole policy. Where there are a number of polices with different prefixes one needs to obtain the current policy, and then replace or add the relevant part for the prefix whilst retaining other parts of the policy relating to other prefixes.

Check the python code for the required command line switches


### bash script extract example of using the notification helper:

~~~
...
# Update bucket notification policy with the new prefix - the CLI requires one json object containing all prefixes.
# We need to get any existing policy and add/update the notification config with the new prefix and then put back the total policy

oldNotificationFile=$(mktemp)
aws s3api get-bucket-notification-configuration --bucket ${Bucket} --profile ${Profile} >$oldNotificationFile 
 
if [[ -s $oldNotificationFile ]]; then
    oldpolicy="-e $oldNotificationFile"
fi
    
newNotificationFile=$(mktemp)

$(python3 ./bucket-notification-policy-helper.py -p ${Prefix} ${oldpolicy} -t ${TopicArn} >$newNotificationFile)

aws s3api put-bucket-notification-configuration --bucket ${Bucket} --profile ${Profile} --notification-configuration "file://${newNotificationFile}"
...
~~~

