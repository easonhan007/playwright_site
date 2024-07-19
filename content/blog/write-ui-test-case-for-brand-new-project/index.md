+++
date = 2024-07-19
title = "我的playwright项目实战初体验"
description = "应该是2023年年初写的，当时正好有合适的项目可以用playwright去进行ui自动化测试"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "python"]
[extra]
math = false
image = "banner.jpg"
+++

2023 年初接了一个新项目，配套有个 web 管理后台页面，尽管需求一直在迭代以及测试时间相对不宽裕，我还是决定写点自动化用例作为功能测试的补充和回归测试的输入，顺便玩一下 playwright，不在真是项目中使用一种技术其实是很难对这种技术产生深刻理解的。

## 项目介绍

管理后台是前后端分离的，前端用的 react 加上蚂蚁的前端组件库，后端是基于 golang 构建的微服务。其实这种项目更适合做接口测试，ui 自动化作为补充就好了。

## 技术选型

这点很清楚，之前 benchmark 过，playwright 比 cypress 性能要好，所以直接选 playwright，另外 playwright 的 python 版本完全安装之后自带了 pytest 和一系列断言，基本上开箱即用，非常方便。另外为什么不用 js 而用 python，主要是因为我用 python 写了一点接口用例，有些数据库操作的代码可以稍微复用一下，所以统一起见用 python+playwright

## 第一个难点：登录

管理后台接的是 google auth，由于我的账号开启了二次验证，需要收验证码，所以从 ui 上输入用户名和密码登录就走不通了。不过登录的原理基本相同，就是往 cookie 里写一些东西，后面所有的请求都自动带 cookie 到后端，后端通过之前写的那些东西就可以判断用户是谁，什么时候登录失效等。知道了原理后面就是随便试试了，我的代码大概是这样写的

```python
def login(page):
    page.goto("url")
    page.evaluate(f'()=> document.cookie="{COOKIE}"')
```

其实就是先访问被测页面，然后自动跳到登录页面，这时候去用 js 设置 cookie，之后再访问一次被测页面就可以自动登录了。

cookie 的话可以从浏览器的开发者工具里直接拷贝出来，因为是测试环境，所以 cookie 的有效期很长，基本可以放心使用。

至于如何定期刷新 cookie 其实也不难搞，写个浏览器插件，每次打开被测页面的时候就把 cookie 发到一个自建后台服务，这个服务就是把 cookie 存到 redis 里，在测试用例里直接访问 redis 拿最新的 cookie 就好了。

## 定位有点麻烦

作为熟练工，定位对我来说应该不会是大问题，然而现在的前端组件层级嵌套厉害，html 的表意性不强，而且 id，name 等比较有标志性的属性也不是很多，踌躇良久之后我决定请前端同学在一些关键的组件上面加上 id 或者 name，尽管他们不是很愿意，但是我倚老卖老，还是让他们从了。

playwright 的元素定位策略非常灵活，从这几天的使用情况来看，建议还是 css 加 xpath，如果你 css 不熟那就直接用 xpath，优点是从浏览器上就可以直接复制 xpath，缺点是复制的 xpath 稳定性很差，页面结构稍微发生一些变化就不可用了。

最后就是 playwright 有录制的功能，我一般是在调试暂停的时候顺便打开录制，看看 playwright 自己录制的定位器是怎么样的，感觉大多数时候 playwright 的录制结果很靠谱，不比自己写要差。playwright 生成的代码里 text 属性用的相对比较多点，对于多语言的系统来说需要慎用。

## 日期选择器

大人，大清早就亡了。

很多年前我们在处理日期选择器的时候基本上是用 js 来 set 相应的 input 的 value 值，可以做到不管 ui 怎么样，我想设置成什么值都可以的效果。

然而，这次时代变了。ant 框架的日期选择器直接设置 value 值并没有什么用。我尝试过打开日期选择器选择今天的日期，因为今天的日期会高亮，所以选起来比较容易，但这样就做不到选择任意一天的效果，对于写用例来说相当不友好。

最后经过一番尝试，还是使用黑科技，模拟键盘在日期框上输入相应的日期，模拟键盘按下回车键，代码如下。

```python
def select_time_range(self, start, end):
    start_str = start.strftime('%Y-%m-%d 00:00:00')
    end_str = end.strftime('%Y-%m-%d 23:59:59')
    self.page.locator('#validTime').type(start_str)
    self.page.locator('.ant-picker-input input >> nth=1').type(end_str)
    self.page.locator('#validTime').press('Enter')
```

## 数据清理

我的用例基本建立在数据的基础上，比如我会先创建一系列的数据，然后通过确定的条件去搜索数据，再度创建数据，编辑数据等，等于是写了剧本的，每个用例按照安排运行，这就要求在所有用例执行之后做数据清理的工作，这就要求我去数据库里更新每条记录的软删除字段。另外搜索页面的数据放在 es 里，这就要求清理的过程中除了数据库之外还要顺便把 es 清掉，稍微有一点点麻烦，不过还好，几行代码的事情。

```python
import pymysql.cursors
import requests, logging, sys
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)

mysql_conf = {
    'host': 'xxxxx',
    'user': 'test',
    'port': 3306,
    'db': 'xxx_db',
    'password': 'secert',
}

class DBCleaner:
    def __init__(self) -> None:
        self.c = pymysql.connect(host=mysql_conf['host'],
        user=mysql_conf['user'],
        port=mysql_conf['port'],
        password=mysql_conf['password'],
        database=mysql_conf['db'],
        cursorclass=pymysql.cursors.DictCursor)

    def delete_by_mid(self, mid):
        with self.c.cursor() as cursor:
            select_sql = f"Select id from biz_tab where m_id = %s;"
            cursor.execute(select_sql, (mid))
            for row in cursor:
                self.delete_es_index_by_biz_id(row['id'])

            logging.info(f"Delete by mid = {mid}")
            sql = f"Delete from biz_tab where m_id = %s;"
            cursor.execute(sql, (mid))
        self.c.commit()

    def delete_es_index_by_biz_id(self, biz_id):
        url = f"test_index/_doc/{biz_id}"
        response = requests.request("DELETE", url).json()
        logging.info(f"Deleting es index for {biz_id}, result is {response['result']}")

if __name__ == __main__':
    if len(sys.argv) == 1:
        print("USAGE: db_cleaner m_id")
    else:
        m_id = sys.argv[-1]
        cleaner = DBCleaner()
        cleaner.delete_by_mid(m_id)
```

上面的脚本有 2 个作用

当 module 引入时可以调用删除的方法，传入 mid 就可以删除对应的记录
直接命令行执行时给出 mid 也能删除
确保清除成功
pytest 在断言失败之后，后面的代码是不会被执行的，为了确保每次都会调用清理的代码，我们需要使用 pytest 的 fixture 机制，代码如下

```python
@pytest.fixture
def data_set():
    m_id = '12'
    yield {'m_id': m_id}
    DBCleaner().delete_by_mid(m_id)
```

## 总结

经过几天的把玩和用例编写，发现

- 迭代过程中的项目确实不太适合写 ui 自动化测试，不过千金难买我喜欢，我就要写
- playwright 很好用
- page object 还是得用
- pytest 很好用
- headless 很好用
- 直接写 js 很好用
- 简单来说，熟练工是第一生产力。

## 回顾

最后在 2024 年的今天来回顾一下这个项目。

项目最后没有维护了，主要是因为:

- playwright 的 python 版本一直更新失败，官方也没给出明确的说法
- playwright 的 api 在当时变化十分频繁，过几个月之后再来看当时的代码，发现很多 api 都过时了
- 因为 web 端的用户很少，所以主要精力也没放在那里，渐渐的就不维护了

现在看来直接连数据库做数据清理不是很好。

- 要了解数据库的分库分表策略，了解是小事，但是策略代码要自己写，这个没必要
- 直接在数据库删数据的时候没办法触发业务逻辑的数据处理脚本
- 数据库的变化对代码的影响很大

后面我在做 api 的自动化时用的是调接口清理的方法，代码可维护了很多。

总之在当时使用 playwright 做 ui 自动化应该是没问题的，问题是不应该用 python 版本，如果是 ts 版本的话估计稳定性会强很多。
