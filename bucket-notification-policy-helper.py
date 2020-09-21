#!/usr/bin/python
#####################################################################################################
# File to output a dictionary (JSON) of an updated bucket lifecycle configuration
#
# Input Args: 
# --existing-notification-file: File with the existing notification configuration from the bucket
# --prefix: Filter path Prefix for the new notification. Note if this matches an existing prefix it will be replaced. Defauts to '' for whole bucket
# --topic-arn: SNS Topic to receive notifications
#
######################################################################################################

import sys, getopt, json

def main(argv):
    existingNotificationFile = ''
    prefix = ''
    topicArn = ''    

    HELP = "bucket-notification-policy-helper.py -e <existing-notification-file> -p <prefix>, -t <topicArn>"

    try:
        opts, args = getopt.getopt(argv, "he:p:t:",["existing-notification-file=","prefix=","topic-arn="])

    except getopt.GetoptError:
        print(HELP)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print (HELP)
            sys.exit()
        elif opt in ("-e", "--existing-notification-file"):
            existingNotificationFile = arg
        elif opt in ("-p", "--prefix"):
            prefix = arg
        elif opt in ("-t", "--topic-arn"):
            topicArn = arg
        else:
            print("Unrecognised Option {}".format(opt))
            print(HELP)
            sys.exit(2)
        
    existingPolicy = {}
    if existingNotificationFile:
        with open(existingNotificationFile) as json_file:
            existingPolicy = json.load(json_file)
    
    if "TopicConfigurations" not in existingPolicy:
        existingPolicy["TopicConfigurations"] = []

    # remove previous prefixes from list
    topicConfigs = existingPolicy["TopicConfigurations"]
    topicConfigs = [x for x in topicConfigs if not x["Events"] == ['s3:ObjectRestore:Completed'] or not x["Filter"]["Key"]["FilterRules"][0]["Value"] == prefix + '/' ]

    event = {
        "Id": prefix + "-RestoreComplete", 
        "Filter": {"Prefix": prefix},
        "TopicArn": topicArn,
        "Events": ["s3:ObjectRestore:Completed"],
        "Filter": {
            "Key": {
                "FilterRules": [
                    {
                        "Name": "prefix",
                        "Value": prefix + "/"
                    }
                ]
            }
        }
    }

    topicConfigs.append(event)
    existingPolicy["TopicConfigurations"] = topicConfigs

    print(json.dumps(existingPolicy))


if __name__ == "__main__":
   main(sys.argv[1:])