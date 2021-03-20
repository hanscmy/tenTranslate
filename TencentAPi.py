import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

try: 
    cred = credential.Credential("AKIDjDTO9fS3oeJkumNQnw5CySiklW5VLLNj", "HSNJIGyQcY8Tm2XnoZtZ1E9tOtCZcZXH") 
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tmt_client.TmtClient(cred, "", clientProfile) 

    req = models.TextTranslateRequest()
    params = {
        "SourceText": "love",
        "Source": "en",
        "Target": "zh"
    }
    req.from_json_string(json.dumps(params))

    resp = client.TextTranslate(req) 
    print(resp.to_json_string()) 

except TencentCloudSDKException as err: 
    print(err) 