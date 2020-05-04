from glob import glob
import os
import yaml
import logging
from collections import defaultdict
from scripts.classification import 分类方法

logger = logging.getLogger(__name__)


def 在分类树中找到标签位置(标签, 分类树):
    if 标签 in 分类树:
        return [标签]
    for 类别, 子类别树 in 分类树.items():
        子类别结果 = 在分类树中找到标签位置(标签, 子类别树)
        if 子类别结果 is not None:
            return [类别] + 子类别结果
    return None


def 找到标签分类所属(标签):
    for 分类方法名, 分类树 in 分类方法.items():
        位置 = 在分类树中找到标签位置(标签, 分类树)
        if 位置 is not None:
            return 分类方法名, 位置
    return None, None


def 分析一条记录(一条记录的路径):
    日期 = 一条记录的路径[:8]
    图片地址列表 = glob(os.path.join(一条记录的路径, 'image.*'))
    if len(图片地址列表) != 1:
        logger.error('每条记录下面应该有且只有一张文件名为image.*的照片')
    图片地址 = '/' + 图片地址列表[0]
    详细信息 = yaml.load(open(os.path.join(一条记录的路径, 'desc.yaml')))
    所有分类位置 = []
    for 一个标签 in 详细信息['标签']:
        分类方法名, 位置 = 找到标签分类所属(一个标签)
        if 分类方法名 is not None:
            所有分类位置.append(位置)
    详细信息['所有分类位置'] = 所有分类位置
    详细信息['记录名'] = os.path.basename(一条记录的路径)
    详细信息['日期'] = 日期
    详细信息['md_图片'] = '![{}]({})'.format(详细信息['名字'], 图片地址)
    详细信息['md_完整'] = '### {}\n#### {}\n{}\n{}\n'.format(
        详细信息['名字'], 详细信息['日期'], 详细信息['故事'], 详细信息['md_图片'])
    return 详细信息


def 创建独立的记录展示(所有记录的详细信息):
    父路径 = 'build/所有记录'
    os.makedirs(父路径, exist_ok=True)
    for 详细信息 in 所有记录的详细信息:
        记录展示路径 = os.path.join(父路径, 详细信息['记录名'] + '.md')
        with open(记录展示路径, 'w') as 文件:
            文件.write(详细信息['md_完整'])


if __name__ == '__main__':
    所有记录的路径 = glob('resource/*')
    所有记录的详细信息 = []
    for 一条记录的路径 in 所有记录的路径:
        所有记录的详细信息.append(分析一条记录(一条记录的路径))
    创建独立的记录展示(所有记录的详细信息)