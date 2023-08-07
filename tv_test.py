import re
import requests
import pandas as pd


def read_txt(file_path):  # 读取tv.txt
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


def parse_tv_file(raw_data):  # 提取原始数据的有效频道信息
    channels = []
    for line in raw_data:
        if line.startswith('#EXTINF:'):  # 开头字符判断，频道信息
            channel_info = re.findall(r'tvg-id="([^"]*)".*tvg-name="([^"]*)".*group-title="([^"]+)",(.+)', line)
            if channel_info:
                tvg_id, tvg_name, group_title, channel_name = channel_info[0]
                channel_info_dict = {
                    "tvg-id": tvg_id,
                    "tvg-name": tvg_name,
                    "group-title": group_title,
                    "channel-name": channel_name,
                }
                channels.append(channel_info_dict)
        elif line.startswith("http"):  # 开头字符判断，频道网址
            if channels:
                channels[-1]["url"] = line.rstrip("\n")
    return channels


def test_channel(channel_list):  # 测试网址, 并返回分辨率和 available
    test_result = []
    for index, channel in enumerate(channel_list):
        response = requests.get(channel['url'], timeout=3)
        if response.status_code == 200:
            available = True
            pattern = r'RESOLUTION=(\d+x\d+)'
            resolution_ratio = re.findall(pattern, response.text)[0]
        else:
            available = False
            resolution_ratio = ''
        channel_test_dict = {
            "id": channel['tvg-id'],
            "name": channel['channel-name'],
            "available": available,
            'resolution_ratio': resolution_ratio,
        }
        test_result.append(channel_test_dict)
    return test_result


def save_test_result_to_file(filename, test_result):  # 保存为 txt
    with open(filename, 'w', encoding='utf-8') as file:
        for channel in test_result:
            file.write(str(channel) + '\n')


def save_test_result_to_csv(filename, test_result):  # 保存为 csv
    df = pd.DataFrame(test_result)  # 使用Pandas的DataFrame将测试结果转换为表格形式
    df.to_csv(filename, index=False)  # 将DataFrame保存为CSV文件


if __name__ == '__main__':
    txt_path = 'tv.txt'  # tv.txt 文件有效路径
    txt_data = read_txt(txt_path)  # 读取 tv.txt
    channel_data = parse_tv_file(txt_data)  # 从M3U中提取有效内容
    test_res = test_channel(channel_data)  # 测试channel并记录结果
    # save_test_result_to_file('tv_test.txt', test_res)  # 保存结果到 tv_test.txt
    save_test_result_to_csv('tv_test_result.csv', test_res)  # 结果保存为 tv_test_result.csv
