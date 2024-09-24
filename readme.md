<h1 align="center">
  <br>
  B站魔力赏市集商品信息爬取器
  <br>
</h1>

## ⚜ 功能简介

依据价格、类别、折扣等限制条件选择性爬取 Bilibili 魔力赏市集上的商品信息。

## ⚜ 更新日志

### 2024/09/25

- \[Fix\] 修复了由于市集风控回传信息发生改变而导致的未知异常误报问题
- \[Opt\] 由于商品数量不随价格均匀分布，全区间查询时将对爬取进度进行加权以减少误差

### 2024/03/04

- \[Fix\] 修复了输出文件内商品信息不包含爬取的最后一页数据的问题
- \[Fix\] 修复了取消保存商品信息后输出文件仍会被保存的问题

### 2024/02/28

- \[Add\] 新增了异常判定提示
- \[Add\] 新增了爬取进度提示
- \[Add\] 新增了运行时间提示
- \[Add\] 新增了 `卖家名称` 与 `卖家UID` 的爬取
- \[Add\] 新增了 `最低价格`、`最高价格`、`最低折扣`、`最高折扣` 的默认值
- \[Fix\] 修复了 `priceFilters` 与 `discountFilters` 筛选区间不包含上限的问题
- \[Opt\] 优化了输出文件内商品信息的格式使之更易于阅读
- \[Opt\] 删除了一些未实际使用的依赖库与函数

## ⚜ 前置条件

### 1. 搭建 Python 运行环境

- [前往 Python 官网下载](https://www.python.org/downloads/ "Python Source Releases")
  - 建议安装 Python 3.10 及以上版本，较老版本出现的问题我们将不再维护
  - 首次安装 Python 时请注意勾选 `Add Python x.x to PATH` 添加环境变量

### 2. 安装相关依赖库

- **Windows**：运行 `Installation of Dependency Libraries.bat` 安装相关依赖库

> [!TIP]
> 若您位于中国大陆且相关依赖库的下载速度较慢，可尝试通过 `pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/` 指令更换下载源

- **macOS & Linux**：运行 `Installation of Dependency Libraries.sh` 安装相关依赖库

> [!TIP]
> 若您位于中国大陆且相关依赖库的下载速度较慢，可尝试通过 `pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/` 指令更换下载源

### 3. 配置 Bilibili Cookie 信息

- 请在 `BilibiliMall-Crawler_main.py` 内找到以下代码，于引号内填写 Bilibili Cookie 信息即可

``` Python
BILIBILI_COOKIE = ""
```

> [!TIP]
> **教程**：[如何获取 Bilibili Cookie 信息](https://zmtblog.xdkd.ltd/2021/10/06/Get_bilibili_cookie/ "Get Bilibili Cookie")

## ⚜ 使用方法

### 1. 运行主程序

- **Windows**：前置条件满足后，运行 `BilibiliMall-Crawler.bat` 即可
- **macOS & Linux**：前置条件满足后，运行 `BilibiliMall-Crawler.sh` 即可

### 2. 退出主程序

- 本程序默认重复运行至商品信息爬取完毕，按下 `Ctrl+C` 以手动中断程序提前退出

## ⚜ 使用条款及注意事项

> [!IMPORTANT]
> - 本项目仅作学习交流之用，不得用于商业或非法用途
> - 本程序的使用方法和效果可能会因 Bilibili 网站的更新或变化而失效

> [!WARNING]
> - 本程序可能会触发 Bilibili 网站的安全风控策略并导致账号被限制访问甚至被封禁，用户应自行评估风险后谨慎使用
> - 本程序的使用需要用户提供自己的 Bilibili Cookie 信息，该信息的泄露可能会导致账号被盗，用户应保护好自身隐私安全，不要将该信息分享给他人
> - 项目贡献者不对用户使用本程序可能给 Bilibili 网站及其母公司上海宽娱数码科技有限公司造成的任何损害或侵权行为负责，用户应自行承担一切后果和法律责任

> [!CAUTION]
> **免责声明：使用本程序即视作用户已同意上述使用条款及注意事项，并充分认识到可能带来的包括但不限于账号封禁、法律纠纷等使用风险，用户同意自行承担一切后果和法律责任**