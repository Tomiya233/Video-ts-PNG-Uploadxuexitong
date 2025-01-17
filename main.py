# utf-8
import subprocess
import os
import shutil
from shutil import copyfile
import requests
import json

# Mp4 文件名字
vName = 'yinyue'
tstime = 10
# 标准mp4转TS格式------------------------------------------------------------------------------
cmd_str = f'"D:/ffmpeg/bin/ffmpeg.exe" -y -i {vName}.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb {vName}.ts'
subprocess.run(cmd_str, encoding="utf-8", shell=True)
print(f'标准 Mp4 转换到 TS 成功！')


#TS切片------------------------------------------------------------------------------
filePath = f'./{vName}'
if os.path.exists(filePath) == False:
    os.makedirs(filePath)
cmd_str = f'"D:/ffmpeg/bin/ffmpeg.exe" -i {vName}.ts -c copy -map 0 -f segment -segment_list ./{vName}/index.m3u8 -segment_time {tstime} ./{vName}/output%03d.ts'
subprocess.run(cmd_str, encoding="utf-8", shell=True)
print(f'TS 切片 成功！')


# TS重命名为PNG------------------------------------------------------------------------------
file_list = os.listdir(filePath)
for i in file_list:
    if i.endswith(".ts"):
        new_name = i.replace(".ts", ".png")
        os.rename(f'{filePath}/' + i, f'{filePath}/' + new_name)
print("TS重命名为PNG 成功！")


# PNG文件添加PNG文件头------------------------------------------------------------------------------
file_list = os.listdir(filePath)
rewritePath = f'{filePath}Png/'
if os.path.exists(rewritePath) == False:
    os.makedirs(rewritePath)
for i in file_list:
    if i.endswith(".png"):
        copyfile("PNG", f'{rewritePath}/' + i)
    else:
        copyfile(f'{filePath}/' + i, f'{rewritePath}/' + i)
file_list = os.listdir(rewritePath)
for i in file_list:
    if i.endswith(".png"):
        bin_file = open(f'{filePath}/' + i, 'rb')  # 打开二进制文件
        # 合并文件
        with open(f'{rewritePath}/' + i, 'ab') as f:
            f.write(bin_file.read())
            bin_file.close()
print("PNG元数据转PNG-TS 成功！")
os.remove(f'{vName}.ts')
shutil.rmtree(filePath)
print("临时文件删除成功")

url = "https://tools.doffchen.cn/chaoxingtc/new/ImageBed/update.php"
m3u8_path = f'{vName}Png/index.m3u8'

with open(m3u8_path, 'r') as m3u811:
    lines = m3u811.readlines()

with open('1.m3u8', 'w', encoding='utf-8') as m3u81:
    for line in lines:
        print(line.strip())
        if '.ts' in line.strip():
            # 获取.ts文件对应的.png文件名
            png_file = str(f'{vName}Png/') + str(line.strip().replace('.ts', '.png'))
            with open(png_file, 'rb') as file:
                files = {'file': (png_file, file, 'image/png')}
                post = requests.post(url, files=files).text
            png_url = (json.loads(post)["msg"])
            print(png_url)
            m3u81.write(png_url+ '\n')
        else:
            m3u81.write(line)