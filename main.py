[2:04 PM] Deep, Akash (External)
"""
    Initializes the customer credentials needed to make calls to Textract using boto3 package internally.
 
    :param profile_name: Customer's profile name as set in the ~/.aws/config file. This profile typically contains this format.
                                :code:`[default]
                                region = us-west-2
                                output=json`
    :type profile_name: str
    :param region_name: If AWSCLI isn't setup, the user can pass region to let boto3 pick up credentials from the system.
    :param region_name: str
    :type profile_name: str, optional
    :param kms_key_id: Customer's AWS KMS key (cryptographic key)
    :type kms_key_id: str, optional
[2:05 PM] Deep, Akash (External)
Textractor(profile_name="default")
