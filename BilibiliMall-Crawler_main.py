# ------------------------- Configuration Modification -------------------------
# 请填写 Bilibili Cookie 至下方引号内
BILIBILI_COOKIE = ""
# ------------------------------------------------------------------------------

import colorama
from colorama import Fore, Style
import time
import json
import requests
from tkinter import filedialog
from datetime import datetime
import os
import pandas as pd
import tkinter as tk

def crawler():
    global category_entry, output_dir, min_price, max_price, showPrice, start_time, item_count, pause_count, retry_count

    mall_url = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"

    min_price = min_price_entry.get() if min_price_entry.get() else "0"
    max_price = max_price_entry.get() if max_price_entry.get() else "5000"
    min_discount = min_discount_entry.get() if min_discount_entry.get() else "0"
    max_discount = max_discount_entry.get() if max_discount_entry.get() else "100"

    # 将最低价格和最高价格乘以 100 并格式化为字符串
    setprice = "{}-{}".format(int(float(min_price) * 100), int(float(max_price) * 100 + 1))
    # 将最低折扣和最高折扣格式化为字符串
    discount = "{}-{}".format(int(min_discount), int(max_discount) + 1)

    # 搜索类别: 手办-2312, 模型-2066, 周边-2331, 3C-2273, 福袋-fudai_cate_id
    id_mapping = {
        "手办": "2312",
        "模型": "2066",
        "周边": "2331",
        "3C": "2273",
        "福袋": "fudai_cate_id"
    }

    category_entry_value = category_entry.get()
    category_entry_real = category_entry_value.replace("c", "C")
    ID = id_mapping.get(category_entry_real, "")
    item_list = []
    item_count = pause_count = retry_count = 0
    showPrice = min_price
    nextId = None
    start_time = time.perf_counter()

    while True:
        payload = json.dumps({
            "sortType": "PRICE_ASC",
            "priceFilters": [
                str(setprice)
            ],
            "discountFilters": [
                str(discount)
            ],
            "categoryFilter": str(ID),
            "nextId": nextId
        })

        headers = {
            "authority": "mall.bilibili.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/json",
            "cookie": f'{BILIBILI_COOKIE}',
            "origin": "https://mall.bilibili.com",
            "referer": "https://mall.bilibili.com/neul-next/index.html?page=magic-market_index",
            "sec-ch-ua": "'Microsoft Edge';v='129', 'Not_A Brand';v='8', 'Chromium';v='129'",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "'Windows'",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }

        try:
            response = requests.request("POST", mall_url, headers = headers, data = payload)
            print(response.text)
            response = response.json()
            data = response["data"]["data"]  # 提取一页内的商品信息
            nextId = response["data"]["nextId"]  # 提取进入下一页所需的密钥

            for item in data:
                c2cItemsId = item["c2cItemsId"]
                c2cItemsName = item["c2cItemsName"]
                showPrice = item["showPrice"]
                showMarketPrice = item["showMarketPrice"]
                uname = item["uname"]
                uid = item["uid"]
                item_list.append({
                    "商品编号": c2cItemsId,
                    "商品名称": c2cItemsName,
                    "当前价格": showPrice,
                    "市场价格": showMarketPrice,
                    "卖家名称": uname,
                    "卖家UID": uid
                })
                item_count += 1
                retry_count = 0

            if nextId is None:
                break

        except (TypeError, KeyError) as e:
            try:
                if response["code"]:
                    if response["code"] == 429:
                        pause_count += 1
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.YELLOW}[Error {response["code"]}] 检测到爬取器触发操作频繁提示, 暂停 30 秒后重试...(¥{showPrice}){Style.RESET_ALL}')
                        information_values_output(0)
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        time_sleep_10ns(3)
                    elif response["code"] == -412:
                        try:
                            print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                            print(f'{Fore.RED}[Error {response["code"]}] 检测到账号已被风控! 请更换 IP 后重试...{Style.RESET_ALL}')
                            print(f'{Fore.YELLOW}[WARN] 从现在起, 爬取器每暂停 60 秒都将重试, 连续失败 5 次后认定爬取失败, 程序自动退出{Style.RESET_ALL}') if retry_count == 0 else ""
                            information_values_output(1)
                            print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                            if retry_count < 5:
                                retry_count += 1
                                pause_count += 1
                                time_sleep_10ns(6)
                            else:
                                print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')
                                break
                        except KeyboardInterrupt:
                            except_user_interrupt()
                            break
                    elif response["code"] == 83000004:
                        pause_count += 1
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.YELLOW}[Error {response["code"]}] 检测到在执行 POST 时读取超时, 暂停 5 秒后重试...{Style.RESET_ALL}')
                        information_values_output(0)
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        time_sleep_5s()
                    elif response["code"] == 83001002:
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        print(f'{Fore.RED}[Error {response["code"]}] 检测到 Bilibili Cookie 配置不正确! 请检查后重试...{Style.RESET_ALL}')
                        print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                        exit()
                    else:
                        except_error_null(response["code"])
                        break
                else:
                    except_error_null(e)
                    break
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except (requests.exceptions.ProxyError, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
            try:
                pause_count += 1
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                print(f'{Fore.YELLOW}[Error Network] 检测到网络环境不稳定, 暂停 5 秒后重试...{Style.RESET_ALL}')
                information_values_output(0)
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                time_sleep_5s()
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except requests.exceptions.JSONDecodeError:
            try:
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                print(f'{Fore.RED}[Error 412] 检测到账号已被风控! 请更换 IP 后重试...{Style.RESET_ALL}')
                print(f'{Fore.YELLOW}[WARN] 从现在起, 爬取器每暂停 60 秒都将重试, 连续失败 5 次后认定爬取失败, 程序自动退出{Style.RESET_ALL}') if retry_count == 0 else ""
                information_values_output(1)
                print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
                if retry_count < 5:
                    retry_count += 1
                    pause_count += 1
                    time_sleep_10ns(6)
                else:
                    print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')
                    break
            except KeyboardInterrupt:
                except_user_interrupt()
                break

        except KeyboardInterrupt:
            except_user_interrupt()
            break

        except Exception as e:
            except_error_null(e)
            break

    information_values_output(3)
    output_dir = filedialog.askdirectory()

    if not os.path.isdir(output_dir):
        print(f'{Fore.CYAN}[INFO] 商品信息的保存被取消!{Style.RESET_ALL}')
        return

    current_time = datetime.now().strftime("%Y-%m-%d_%H时%M分%S秒")
    file_name = f'{current_time}_{min_price}-{max_price}元_{int(min_discount) // 10}-{int(max_discount) // 10}折{category_entry_real}.xlsx'
    output_file = os.path.normpath(os.path.join(output_dir, file_name))

    df = pd.DataFrame(item_list, columns = ["商品编号", "商品名称", "当前价格", "市场价格", "卖家名称", "卖家UID"])
    writer = pd.ExcelWriter(output_file, engine = "xlsxwriter")
    df.to_excel(writer, index = False)
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    worksheet.freeze_panes(1, 0)

    # 标题行格式: 居中对齐, 仿宋, 加粗, 字号12
    header_format = workbook.add_format({"align": "center"})
    header_format.set_font_name("仿宋")
    header_format.set_bold()
    header_format.set_font_size(12)
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # 商品编号列格式: 居中对齐, 列宽15, Times New Roman
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("Times New Roman")
    worksheet.set_column("A:A", 15, col_format)

    # 商品名称列格式: 左对齐, 列宽80, 楷体
    col_format = workbook.add_format()
    col_format.set_align("left")
    col_format.set_font_name("楷体")
    worksheet.set_column("B:B", 80, col_format)

    # 卖家名称列格式: 居中对齐, 列宽10, 楷体
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("楷体")
    worksheet.set_column("E:E", 10, col_format)

    # 其余列格式: 居中对齐, 列宽10, Times New Roman
    col_format = workbook.add_format()
    col_format.set_align("center")
    col_format.set_font_name("Times New Roman")
    worksheet.set_column("C:D", 10, col_format)
    worksheet.set_column("F:F", 10, col_format)

    writer.close()
    print(f'{Fore.CYAN}[INFO] 商品信息已保存至 {output_file}{Style.RESET_ALL}')
    pass

def extract_minutes_seconds(interval_time):
    min = int(interval_time // 60)
    sec = int(interval_time % 60)
    return min, sec

def calculate_weighted_progress(showPrice):
    price_distribution = {
        (0, 50): 0.2,
        (50, 100): 0.4,
        (100, 500): 0.25,
        (500, 5000): 0.15
    }
    total_weight = 0

    for price_range, price_weight in price_distribution.items():
        min_price_range, max_price_range = price_range
        if float(showPrice) > max_price_range:
            total_weight += price_weight
        elif min_price_range < float(showPrice) <= max_price_range:
            progress = (float(showPrice) - min_price_range) / (max_price_range - min_price_range)
            return total_weight + progress * price_weight

    return 1.0  # 如果价格超过最高区间，则进度为100%

def information_values_output(tag):
    global max_price, showPrice

    max_price = str(float(max_price) + 1) if max_price == min_price else max_price
    showPrice = str(float(showPrice) + 1) if showPrice == min_price else showPrice

    if min_price == "0" and max_price == "5000":
        progress = calculate_weighted_progress(showPrice)
    else:
        progress = (float(showPrice) - float(min_price)) / (float(max_price) - float(min_price))

    interval_time = time.perf_counter() - start_time
    min, sec = extract_minutes_seconds(interval_time)
    remain_min, remain_sec = extract_minutes_seconds(interval_time / progress - interval_time)

    if tag == 0 and item_count != 0:  # Default 输出
        print(f'{Fore.CYAN}[INFO] 当前为第 {pause_count} 次暂停, 已爬取 {item_count} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
        print(f'{Fore.GREEN}[INFO] 程序已运行 {min} 分 {sec} 秒, 预计还将运行 {remain_min} 分 {remain_sec} 秒{Style.RESET_ALL}')
    elif tag == 1 and item_count != 0:  # Error 412 输出
        print(f'{Fore.CYAN}[INFO] 当前为第 {pause_count} 次暂停, 已爬取 {item_count} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}') if retry_count == 0 else print(f'{Fore.CYAN}[INFO] 当前为第 {retry_count} 次重试, 第 {pause_count} 次暂停, 已爬取 {item_count} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
        print(f'{Fore.GREEN}[INFO] 程序已运行 {min} 分 {sec} 秒, 预计还将运行 {remain_min} 分 {remain_sec} 秒{Style.RESET_ALL}')
    elif tag == 2 and item_count != 0:  # KeyboardInterrupt 输出
        print(f'{Fore.CYAN}[INFO] 当前已爬取 {item_count} 件商品, 爬取进度 {progress * 100:.2f} %{Style.RESET_ALL}')
    elif tag == 3:  # DONE 输出
        print(f'{Fore.GREEN}[DONE] 爬取进程结束, 本次在 {min_price}-{max_price} 元的区间内共爬取到 {item_count} 件商品, 耗时 {min} 分 {sec} 秒!{Style.RESET_ALL}')
        exit() if item_count == 0 else ""

def time_sleep_5s():
    for i in range(5, 0, -1):
        print(f'{Fore.RED}[INFO] 距离重试还剩 {i} 秒...{Style.RESET_ALL}')
        time.sleep(1)
    print(f'{Fore.MAGENTA}[INFO] 开始重新爬取!{Style.RESET_ALL}')

def time_sleep_10ns(n):
    for i in range(n, 0, -1):
        print(f'{Fore.YELLOW}[INFO] 距离重试还剩 {i * 10} 秒...{Style.RESET_ALL}')
        time.sleep(10) if i != 1 else time.sleep(5)
    time_sleep_5s()

def except_user_interrupt():
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.YELLOW}[WARN] 检测到程序运行被手动中断...{Style.RESET_ALL}')
    information_values_output(2)
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')

def except_error_null(e):
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.RED}[Error {e}] 检测到未知异常, 程序自动退出...{Style.RESET_ALL}')
    print(f'{Fore.MAGENTA}{"-" * 70}{Style.RESET_ALL}')
    print(f'{Fore.RED}[WARN] 程序退出时存在未解决的异常, 爬取的商品信息可能不完整!{Style.RESET_ALL}')

colorama.init(autoreset = True)
window = tk.Tk()
window.title("B站魔力赏市集商品信息爬取器")
window.geometry("600x400")

# 最低价格标签和输入框
min_price_label = tk.Label(window, text = "最低价格(默认 0 元)")
min_price_label.pack()
min_price_entry = tk.Entry(window)
min_price_entry.pack()

# 最高价格标签和输入框
max_price_label = tk.Label(window, text = "最高价格(默认 5000 元)")
max_price_label.pack()
max_price_entry = tk.Entry(window)
max_price_entry.pack()

# 搜索类别标签和输入框
category_label = tk.Label(window, text = "搜索类别(默认全选, 可选: 手办、模型、周边、3C、福袋)")
category_label.pack()
category_entry = tk.Entry(window)
category_entry.pack()

# 最低折扣标签和输入框
min_discount_label = tk.Label(window, text = "最低折扣(默认 0, 范围: 0-100)")
min_discount_label.pack()
min_discount_entry = tk.Entry(window)
min_discount_entry.pack()

# 最高折扣标签和输入框
max_discount_label = tk.Label(window, text = "最高折扣(默认 100, 范围: 0-100)")
max_discount_label.pack()
max_discount_entry = tk.Entry(window)
max_discount_entry.pack()

# 爬取按钮
crawl_button = tk.Button(window, text = "开始爬取", command = crawler)
crawl_button.pack()

window.mainloop()
colorama.deinit()