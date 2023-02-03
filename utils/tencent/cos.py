# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from django.conf import settings

def creat_bucket(bucket, region = "ap-nanjing"):
    '''
    :param bucket: 桶名称
    :param region: 区域
    :return:
    '''

    # 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # region = 'ap-nanjing'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                               # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
    # token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
    # scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填


    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL="public-read",  # private / public-read / public-read-write
    )

def upload_file(bucket, region, file_object, key):

    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    # 上传配置
    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key,  # 上传到桶之后的文件名
        # PartSize=1,
        # MAXThread=10,
        # EnableMD5=False
    )

    # 返回图片路径
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)




