#!/usr/bin/env python3
import subprocess
import time
import os
import sys

# 配置参数
OUTPUT_DIR = "../download/bilidown"
COOKIES_FILE = "../cookies.txt"
DOWNLOAD_QUALITY = "0"  # 下载质量
SLEEP_TIME = 20  # 每次下载之间的间隔时间(秒)
BV_LIST_FILE = "bv_list.txt"  # 存储BV号的文件
LOG_FILE = "download_log.txt"  # 日志文件

def log_message(message):
    """记录日志到文件和控制台"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def read_bv_list(file_path):
    """从文件中读取BV号列表"""
    if not os.path.exists(file_path):
        log_message(f"错误: BV号列表文件 '{file_path}' 不存在!")
        return []
    
    bv_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # 清理每行，移除空白字符并跳过空行和注释
            bv = line.strip()
            if bv and not bv.startswith("#"):
                bv_list.append(bv)
    
    return bv_list

def download_video(bv_id):
    """使用bilidown.py下载指定BV号的视频"""
    cmd = [
        "python3", "bilidown.py", 
        bv_id, 
        "-o", OUTPUT_DIR, 
        "-c", COOKIES_FILE, 
        "-d", DOWNLOAD_QUALITY
    ]
    
    log_message(f"开始下载: {bv_id}")
    try:
        # 执行下载命令
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 实时输出下载进度
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # 获取命令执行结果
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            log_message(f"成功下载: {bv_id}")
            return True
        else:
            log_message(f"下载失败: {bv_id}, 错误: {stderr}")
            return False
            
    except Exception as e:
        log_message(f"下载过程中发生错误: {bv_id}, 异常: {str(e)}")
        return False

def mark_as_downloaded(bv_id):
    """将已下载的BV号标记为已完成"""
    with open("downloaded.txt", "a", encoding="utf-8") as f:
        f.write(f"{bv_id}\n")

def get_downloaded_list():
    """获取已下载的BV号列表"""
    if not os.path.exists("downloaded.txt"):
        return set()
    
    downloaded = set()
    with open("downloaded.txt", "r", encoding="utf-8") as f:
        for line in f:
            downloaded.add(line.strip())
    
    return downloaded

def main():
    # 确保日志文件存在
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    
    log_message("=== 批量下载程序启动 ===")
    
    # 读取BV号列表
    bv_list = read_bv_list(BV_LIST_FILE)
    if not bv_list:
        log_message("没有找到要下载的BV号，程序退出")
        return
    
    log_message(f"共找到 {len(bv_list)} 个BV号待下载")
    
    # 获取已下载的BV号列表
    downloaded = get_downloaded_list()
    log_message(f"已有 {len(downloaded)} 个BV号下载完成")
    
    # 过滤掉已下载的BV号
    to_download = [bv for bv in bv_list if bv not in downloaded]
    log_message(f"本次需要下载 {len(to_download)} 个BV号")
    
    # 开始下载
    for i, bv_id in enumerate(to_download, 1):
        log_message(f"处理第 {i}/{len(to_download)} 个: {bv_id}")
        
        success = download_video(bv_id)
        if success:
            mark_as_downloaded(bv_id)
        
        # 如果不是最后一个视频，则等待一段时间再下载下一个
        if i < len(to_download):
            log_message(f"等待 {SLEEP_TIME} 秒后继续下一个下载...")
            time.sleep(SLEEP_TIME)
    
    log_message("=== 所有下载任务完成 ===")

if __name__ == "__main__":
    main()
