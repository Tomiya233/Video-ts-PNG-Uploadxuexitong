import tkinter as tk
from tkinter import filedialog
import os
import requests
import subprocess
import shutil
from shutil import copyfile
import json
import tkinter.messagebox

main = tk.Tk()
main.title("视频切片并伪装png上传图床")
main.geometry("500x400")
main.resizable(False, False)


news= tk.Label(main, text="请先选择FFMPEG路径与mp4路径",font=(12),width=30,height=2).pack()

ffmpeg_path = tk.StringVar()

def ffmpeg_path_get():
    ffmpeg_path_path = filedialog.askopenfilename()
    ffmpeg_path.set(ffmpeg_path_path)

ffmpeg_path_input = tk.Entry(main,textvariable=ffmpeg_path, show=None, font=('Arial', 8))
ffmpeg_path_input.place(x=100, y=50,width=220,height=26)
tk.Label(main, text='FFmpeg路径', font=('Arial', 10)).place(x=10, y=50)
find_ffmpeg = tk.Button(main, text="选择ffmpeg.exe", command=ffmpeg_path_get).place(x=330,y=47)

mp4_path = tk.StringVar()
def mp4_path_get():
    mp4_path_path = filedialog.askopenfilename()
    mp4_path.set(mp4_path_path)

mp4_path_input = tk.Entry(main,textvariable=mp4_path, show=None, font=('Arial', 8))
mp4_path_input.place(x=100, y=85,width=220,height=26)
tk.Label(main, text='mp4路径', font=('Arial', 10)).place(x=10, y=85)
find_mp4 = tk.Button(main, text="选择mp4文件", command=mp4_path_get).place(x=330,y=82)


def gogogo():
    if ffmpeg_path_input.get() == "":
        tkinter.messagebox.showwarning(title='Hi', message='ffmpeg路径未输入')
        return
    if mp4_path_input.get() == "":
        tkinter.messagebox.showwarning(title='Hi', message='mp4路径未输入')
        return

    tstime = 10
    # 标准mp4转TS格式------------------------------------------------------------------------------
    cmd_str = f'"{ffmpeg_path_input.get()}" -y -i {mp4_path_input.get()} -vcodec copy -acodec copy -vbsf h264_mp4toannexb temp.ts'
    subprocess.run(cmd_str, encoding="utf-8", shell=True)
    print(f'标准 Mp4 转换到 TS 完成！')


    #TS切片------------------------------------------------------------------------------
    filePath = f'./temp'
    if os.path.exists(filePath) == False:
        os.makedirs(filePath)
    cmd_str = f'"{ffmpeg_path_input.get()}" -i temp.ts -c copy -map 0 -f segment -segment_list ./temp/index.m3u8 -segment_time {tstime} ./temp/output%03d.ts'
    subprocess.run(cmd_str, encoding="utf-8", shell=True)
    print(f'TS 切片 完成！')


    # TS重命名为PNG------------------------------------------------------------------------------
    file_list = os.listdir(filePath)
    for i in file_list:
        if i.endswith(".ts"):
            new_name = i.replace(".ts", ".png")
            os.rename(f'{filePath}/' + i, f'{filePath}/' + new_name)
    print("TS重命名为PNG 完成！")


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
    print("PNG元数据转PNG-TS 完成！")
    os.remove(f'temp.ts')
    shutil.rmtree(filePath)
    print("临时文件删除完成")
    tkinter.messagebox.showinfo(title='Hi', message='切片完成 开始上传') 
    url = "https://tools.doffchen.cn/chaoxingtc/new/ImageBed/update.php"
    m3u8_path = f'tempPng/index.m3u8'

    with open(m3u8_path, 'r') as m3u811:
        lines = m3u811.readlines()

    with open('out_viode.m3u8', 'w', encoding='utf-8') as m3u81:
        for line in lines:
            print(line.strip())
            if '.ts' in line.strip():
                # 获取.ts文件对应的.png文件名
                png_file = str(f'tempPng/') + str(line.strip().replace('.ts', '.png'))
                with open(png_file, 'rb') as file:
                    files = {'file': (png_file, file, 'image/png')}
                    post = requests.post(url, files=files).text
                png_url = (json.loads(post)["msg"])
                print(png_url)
                m3u81.write(png_url+ '\n')
            else:
                m3u81.write(line)
    tkinter.messagebox.showinfo(title='Hi', message='上传完毕 新的m3u8文件在本程序的目录下') 
gogogo = tk.Button(main, text="开始切片并上传学习通图床", command=gogogo).place(x=160,y=160)

if __name__ == "__main__":
    main.mainloop()