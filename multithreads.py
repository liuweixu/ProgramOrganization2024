import requests
from threading import Thread
from queue import Queue
import argparse
import time
from tqdm import tqdm


# 下载块的函数
def download_chunk(url, start, end, queue, progress_bar):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers)
    queue.put((start, response.content))
    progress_bar.update(end - start + 1)  # 更新进度条


# 主下载函数
def download_file(url, num_threads=4):
    response = requests.head(url)
    file_size = int(response.headers['Content-Length'])

    chunk_size = file_size // num_threads
    queue = Queue()

    threads = []
    start_time = time.time()  # 记录开始时间

    # 初始化进度条
    with tqdm(total=file_size, unit='B', unit_scale=True, desc='Downloading') as progress_bar:
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i != num_threads - 1 else file_size - 1
            thread = Thread(target=download_chunk, args=(url, start, end, queue, progress_bar))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    chunks = [queue.get() for _ in range(num_threads)]
    chunks.sort()  # 确保块的顺序正确

    file_name = url.split('/')[-1]
    with open(file_name, 'wb') as f:
        for _, chunk in chunks:
            f.write(chunk)

    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time  # 计算下载时间
    print(f"\nDownloaded {file_name} successfully in {elapsed_time:.2f} seconds!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-threaded file downloader")
    parser.add_argument("url", type=str, help="URL of the file to download")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use for downloading")

    args = parser.parse_args()
    download_file(args.url, num_threads=args.threads)
