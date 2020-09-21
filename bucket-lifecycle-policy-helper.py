#!/usr/bin/python
#####################################################################################################
# File to output a dictionary (JSON) of an updated bucket lifecycle configuration
#
# Input Args: 
# --existing-lifecycle-file: File with the existing lifecycle configuration from the bucket
# --prefix: Filter path Prefix for the new lifecycle. Note if this matches an existing prefix it will be replaced. Defauts to '' for whole bucket
# --current-version-expiration-days: Expiration number of days for current objects
# --noncurrent-version-expiration-days: Expiration number of days for non-current objects
# --abort-incomplete-multipart-upload: Number of days to abort an incomplete multipart upload. Default 7
# --current-transition-target: Target Storage Class (DEEP_ARCHIVE|GLACIER|INTELLIGENT_TIERING|ONEZONE_IA|STANDARD_IA) for current objects, leave blank for none.
# --current-transition-days: Number of days after which current objects should transition
# --noncurrent-transition-target: Target Storage Class (DEEP_ARCHIVE|GLACIER|INTELLIGENT_TIERING|ONEZONE_IA|STANDARD_IA) for non-current objects, leave blank for none.
# --noncurrent-transition-days: Number of days after which non-current objects should transition
#
######################################################################################################

import sys, getopt, json

def main(argv):
    existingLifecycleFile = ''
    prefix = ''
    currentVersionExpirationDays = 0
    nonCurrentVersionExpirationDays = 0
    abortIncompleteMultipartUpload = 7
    currentTransitionTarget = ''
    currentTransitionDays = 0
    nonCurrentTransitionTarget = ''
    nonCurrentTransitionDays = 0

    STORAGE_CLASSES = ['DEEP_ARCHIVE', 'GLACIER', 'INTELLIGENT_TIERING', 'ONEZONE_IA', 'STANDARD_IA', 'STANDARD_S3', '']

    HELP = "bucket-lifecycle-policy-helper.py -e <existing-lifecycle-file> -p <prefix>, -c <current-version-expiration-days> -n <non-current-version-expiration-days> " + \
        " -a <abort-incomplete-multipart-upload-days> -g <current-transition-target-storage-class> -y <non-current-transition-storage-class> " + \
        " -d <current-transition-days> -x <non-current-transition-days>"

    try:
        opts, args = getopt.getopt(argv, "he:p:c:n:a:g:y:d:x:",["existing-lifecycle-file=","prefix=","current-version-expiration-days=",\
            "noncurrent-version-expiration-days=","abort-incomplete-multipart-upload-days=","current-transition-target=","current-transition-days=",\
            "noncurrent-transition-target=", "noncurrent-transition-days="])

    except getopt.GetoptError:
        print(HELP)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print (HELP)
            sys.exit()
        elif opt in ("-e", "--existing-lifecycle-file"):
            existingLifecycleFile = arg
        elif opt in ("-p", "--prefix"):
            prefix = arg
        elif opt in ("-c", "--current-version-expiration-days"):
            if arg.isdigit():
                currentVersionExpirationDays = arg
            else:
                print("Invalid Value for option {}".format(opt))
                sys.exit(2)
        elif opt in ("-n", "--non-current-version-expiration-days"):
            if arg.isdigit():
                nonCurrentVersionExpirationDays = arg
            else:
                print("Invalid Value for option {}".format(opt))
                sys.exit(2)
        elif opt in ("-a", "--abort-incomplete-multipart-upload-days"):
            if arg.isdigit():
                abortIncompleteMultipartUpload= arg
            else:
                print("Invalid Value for option {}".format(opt))
                sys.exit(2)
        elif opt in ("-g", "--current-transition-target"):
            if arg in STORAGE_CLASSES:
                currentTransitionTarget = arg
            else:
                print("Invalid Storage Class {} for {}. Valid options are {}".format(arg, opt, STORAGE_CLASSES))
                sys.exit(2)
        elif opt in ("-y", "--non-current-transition-target"):
            if arg in STORAGE_CLASSES:
                nonCurrentTransitionTarget = arg
            else:
                print("Invalid Storage Class {} for {}. Valid options are {}".format(arg, opt, STORAGE_CLASSES))
                sys.exit(2)
        elif opt in ("-d", "--current-transition-days"):
            if arg.isdigit():
                currentTransitionDays = arg
            else:
                print("Invalid Value for option {}".format(opt))
                sys.exit(2)
        elif opt in ("-x", "--non-current-transition-days"):
            if arg.isdigit():
                nonCurrentTransitionDays = arg
            else:
                print("Invalid Value for option {}".format(opt))
                sys.exit(2)
        else:
            print("Unrecognised Option {}".format(opt))
            print(HELP)
            sys.exit(2)
        
    existingPolicy = {}
    if existingLifecycleFile:
        with open(existingLifecycleFile) as json_file:
            existingPolicy = json.load(json_file)
    
    if "Rules" not in existingPolicy:
        existingPolicy["Rules"] = []

    # remove previous prefixes from list
    rules = existingPolicy["Rules"]
    rules = [x for x in rules if not x["Filter"]["Prefix"] == prefix and not x["Filter"]["Prefix"] == prefix + '/']

    identity = "{}-{}{}-Exp{}".format(prefix, currentTransitionTarget, currentTransitionDays, currentVersionExpirationDays)

    rule = {
        "ID": identity, 
        "Filter": {"Prefix": prefix + "/"},
        "Status": "Enabled",
        "AbortIncompleteMultipartUpload": {
            "DaysAfterInitiation": int(abortIncompleteMultipartUpload)
        }
    }
    if currentVersionExpirationDays:
        rule["Expiration"] = {
            "Days": int(currentVersionExpirationDays)
        }
    
    if nonCurrentVersionExpirationDays:
        rule["NoncurrentVersionExpiration"] = {
            "NoncurrentDays": int(nonCurrentVersionExpirationDays)
        }
    
    if currentTransitionTarget and currentTransitionDays:
        rule["Transitions"] = [{
            "Days": int(currentTransitionDays),
            "StorageClass": currentTransitionTarget
        }]

    if nonCurrentTransitionTarget and nonCurrentTransitionDays:
        rule["NoncurrentVersionTransitions"] = [{
            "NoncurrentDays": int(nonCurrentTransitionDays),
            "StorageClass": nonCurrentTransitionTarget
        }]

    rules.append(rule)
    existingPolicy["Rules"] = rules

    print(json.dumps(existingPolicy))


if __name__ == "__main__":
   main(sys.argv[1:])