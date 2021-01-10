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
    日期 = os.path.basename(一条记录的路径)[:8]
    图片地址列表 = glob(os.path.join(一条记录的路径, 'image.*'))
    if len(图片地址列表) != 1:
        logger.error('每条记录下面应该有且只有一张文件名为image.*的照片')
    if len(图片地址列表) == 0:
        图片地址列表 = glob(os.path.join(一条记录的路径, '*.JPG'))[:1]
    图片地址 = '/' + 图片地址列表[0]
    详细信息 = yaml.load(open(os.path.join(一条记录的路径, 'desc.yaml')))
    所有分类位置 = []
    for 一个标签 in 详细信息['标签']:
        分类方法名, 位置 = 找到标签分类所属(一个标签)
        if 分类方法名 is not None:
            所有分类位置.append((分类方法名, 位置))
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
        详细信息['独立记录链接'] = '/' + 记录展示路径
        详细信息['md_独立记录链接'] = '[{}]({})'.format(详细信息['名字'], 详细信息['独立记录链接'])
        with open(记录展示路径, 'w') as 文件:
            文件.write(详细信息['md_完整'])


def 获取子目录内容(分类树, 层级=2):
    结果 = ''
    for 一条记录 in 分类树.get('记录', []):
        结果 += '- {}\n'.format(一条记录['md_独立记录链接'])
    for 子类别名, 子类别树 in 分类树.items():
        if 子类别名 == '记录':
            continue
        结果 += '#' * 层级 + ' ' + 子类别名 + '\n'
        结果 += 获取子目录内容(子类别树, 层级+1)
    return 结果


def 创建分类导引页面(所有记录的详细信息):
    内容导引 = {}
    for 详细信息 in 所有记录的详细信息:
        for 分类方法名, 位置 in 详细信息['所有分类位置']:
            if 分类方法名 not in 内容导引:
                内容导引[分类方法名] = {}
            当前目录 = 内容导引[分类方法名]
            for 标签 in 位置:
                if 标签 not in 当前目录:
                    当前目录[标签] = {'记录': []}
                当前目录 = 当前目录[标签]
            当前目录['记录'].append(详细信息)
    for 分类方法名, 分类树 in 内容导引.items():
        页面路径 = 'build/按{}.md'.format(分类方法名)
        with open(页面路径, 'w') as 文件:
            文件.write(获取子目录内容(分类树))


def 创建时间线(所有记录的详细信息):
    内容 = ''
    for 一条记录 in 所有记录的详细信息[::-1]:
        内容 += 一条记录['md_完整']
    with open('build/时间线.md', 'w') as 文件:
        for 一条记录 in 所有记录的详细信息:
            文件.write('- ' + 一条记录['md_独立记录链接'] + '\n')
    return 内容


if __name__ == '__main__':
    所有记录的路径 = glob('resource/*')
    所有记录的详细信息 = []
    for 一条记录的路径 in 所有记录的路径:
        所有记录的详细信息.append(分析一条记录(一条记录的路径))
    所有记录的详细信息.sort(key=lambda x: x['记录名'])
    创建独立的记录展示(所有记录的详细信息)
    创建分类导引页面(所有记录的详细信息)
    时间线内容 = 创建时间线(所有记录的详细信息)
    with open('README.md', 'w') as 文件:
        文件.write('对自制美食的一些记录与整理\n')
        文件.write('## 目录\n')
        文件.write('- [按照食材分类整理的目录](/build/按食材.md)\n')
        文件.write('- [按照烹饪方法整理的目录](/build/按烹饪方法.md)\n')
        文件.write('- [按照时间线整理的目录](/build/按烹饪方法.md)\n')

        文件.write('## 最新动态\n')
        文件.write(时间线内容)

