# This file is used only when code is deployed to aws lambda function using sam cli
#sam does not take empty file in dependencies directory.

def CheckKey(dict, key):
    return key in dict.keys()