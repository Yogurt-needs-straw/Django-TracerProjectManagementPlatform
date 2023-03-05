# -*- coding=utf-8
from django.http import JsonResponse
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

def delete_file(bucket, region, key):

    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    # 删除桶操作
    client.delete_object(
        Bucket=bucket,
        Key=key,
    )

def delete_file_list(bucket, region, key_list):

    config = CosConfig(Region=region, SecretId=settings.TENCENT_COS_ID, SecretKey=settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }

    # 删除桶操作
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )

def credential(bucket, region,):
    ''' 获取cos上传的临时凭证 '''
    # 生成一个临时凭证，并给前端返回
    # 1.安装一个生成临时凭证python模块 pip install -U qcloud-python-sts
    # 2.写代码
    from sts.sts import Sts
    config = {
        # 临时秘钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 1800,
        # 固定秘钥 id
        'secret_id': settings.TENCENT_COS_ID,
        # 固定秘钥 key
        'secret_key': settings.TENCENT_COS_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成bucket所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录判断允许上传的具体路径
        # 例子：a.jpg 或者 a/* 或者 *（使用通配符*存在重大安全风险，请谨慎评估使用）
        'allow_prefix': '*',
        # 秘钥的权限列表，简单上传和分片需要以下的权限，其他权限列表请看
        # https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            'name/cos:PostObject',
            # "*",
        ],

    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return JsonResponse(result_dict)

