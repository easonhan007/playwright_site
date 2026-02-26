+++
date = 2026-02-15
title = "Playwright 测试最佳实践：Fixtures + Page Object Model 完美结合"
description = "python版本"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "原创", "Fixture", "Page Object"]
[extra]
math = false
image = "cover.jpg"
+++

之前有分享过[typescript的版本](/blog/building-scalable-playwright-tests-with-fixtures-and-page-object-model/)，现在分享一下如何 python用 Fixtures 优雅实现 Page Object Model设计模式。

## 被测项目

还是用[memo](https://usememos.com/)这个笔记工具，这次我们写2个用例，分别是

- 登录
- 创建笔记

## 项目结构

```
根目录/
├── conftest.py          ← 定义fixtures的地方
├── pages/
│   └── login_page.py    ← 定义page的地方
│   └── home_page.py
├── tests/
│   └── test_xxx.py      ← 用例写在这里
└── ...
```

## pages

### login page(注册和登录页)

```python
# login_page.py
class LoginPage():
    def __init__(self, page):
        self.page = page
        self.username = self.page.get_by_role("textbox", name="Username")
        self.password = self.page.get_by_role("textbox", name="Password")
        self.sign_up_btn = self.page.get_by_role("button", name="Sign up")
        self.sign_in_btn = self.page.get_by_role("button", name="Sign in")

    def navigate(self, sign_up: bool = False):
        url = "http://localhost:5230/auth"
        if sign_up:
            url = "http://localhost:5230/auth/signup"

        self.page.goto(url, wait_until="domcontentloaded")
        self.username.wait_for(state="visible", timeout=2000)

    def sign_up(self, username: str, password: str):
        self.navigate(sign_up=True)
        self.username.fill(username)
        self.password.fill(password)
        self.sign_up_btn.click()

    def sign_in(self, username: str, password: str):
        self.navigate()
        self.username.fill(username)
        self.password.fill(password)
        self.sign_in_btn.click()

```

### home page(创建和查看memo的页面)

```python
# home_page.py

class HomePage():
    def __init__(self, page):
        self.page = page
        self.textarea = self.page.get_by_role("textbox", name="Any thoughts...")
        self.save_btn = self.page.get_by_role("button", name="Save")
        self.more_btn = self.page.locator(".lucide-ellipsis-vertical").first

        self.pin_option = self.page.get_by_role("menuitem", name="Pin")
        self.edit_option = self.page.get_by_role("menuitem", name="Edit")
        self.delete_option = self.page.get_by_role("menuitem", name="Delete")

        self.unpin_btn = self.page.locator(".lucide-bookmark")
        self.published_at = self.page.locator("relative-time")
        self.smile_btn = self.page.locator(".lucide.lucide-smile-plus").first

        self.delete_btn = self.page.get_by_role("dialog").page.get_by_role("button", name="Delete")

        self.upload = self.page.locator('input[type="file"]').first

    def navigate(self):
        self.page.goto("http://localhost:5230", wait_until="domcontentloaded")
        self.textarea.wait_for(state="visible", timeout=2000)

    def create_post(self, content):
        self.navigate()
        self.textarea.fill(content)
        self.save_btn.click()

    def pin_post(self):
        self.more_btn.click()
        self.pin_option.wait_for(state="visible", timeout=2000)
        self.pin_option.click()

    def unpin_post(self):
        if self.unpin_btn.count() > 0:
            self.unpin_btn.first.click()

    def reaction_btn(self, reaction):
        btn = self.page.get_by_role("dialog").get_by_text(reaction)
        btn.wait_for(state="visible", timeout=2000)
        return btn


    def add_reaction(self, reaction: str):
        self.published_at.hover()
        self.smile_btn.wait_for(state="visible", timeout=2000)
        self.smile_btn.click()
        time.sleep(0.5)
        self.reaction_btn(reaction).click()

    def edit_post(self, content: str):
        self.more_btn.click()
        self.edit_option.wait_for(state="visible", timeout=2000)
        self.edit_option.click()
        self.page.get_by_role("textbox", name="Any thoughts...").nth(1).fill(content)
        self.page.get_by_role("button", name="Save").nth(1).click()

    def delete_post(self):
        self.more_btn.click()
        self.edit_option.wait_for(state="visible", timeout=2000)
        self.delete_option.click()
        self.delete_btn.wait_for(state="visible", timeout=2000)
        self.delete_btn.click()

    def upload_file(self, file_path):
        self.upload.set_input_files(file_path)
        self.save_btn.click()

```

## conftest.py

conftest.py 是 pytest 用来存放“共享 fixture、钩子函数、插件配置”的特殊文件，它能让很多测试相关的设置和准备工作在多个测试文件之间共享，而不需要重复写代码。

它是 pytest 中最重要、最常用的“全局/局部配置与共享机制”之一。

### conftest.py 的位置决定了它的作用范围（非常重要！）

位置不同，影响的测试范围完全不一样：

| 文件位置                         | 作用范围                               | 典型场景                             |
| -------------------------------- | -------------------------------------- | ------------------------------------ |
| 项目根目录下的 conftest.py       | **全局**：影响项目下所有测试           | 浏览器 fixture、日志、数据库连接     |
| tests/ 目录下的 conftest.py      | 只影响 tests/ 目录及其子目录的所有测试 | 整个测试套件的通用 fixture           |
| tests/api/ 下的 conftest.py      | 只影响 tests/api/ 及其子目录           | 只给 API 测试用的 token、mock server |
| tests/ui/login/ 下的 conftest.py | 只影响 tests/ui/login/ 目录            | 登录相关的页面对象、已登录 fixture   |

### 小结：一句话记住 conftest.py 的本质

**conftest.py = pytest 的“共享配置 + 公共的数据准备 + 全局钩子”文件**

## 测试用例

```python
# test_memo.py
from playwright.sync_api import expect
def test_login(login_page):
    login_page.navigate()
    login_page.sign_in("demo", "demo")

    # 判断登录成功之后，页面应该跳转到http://localhost:5230/
    expect(login_page.page).to_have_url("http://localhost:5230/")


def test_create_memo(authenticated_page, home_page):
    before_count = home_page.published_at.count()
    home_page.create_post("hi, there")


    expect(home_page.published_at).to_have_count(before_count + 1)
```

`test_create_memo`的断言有点难理解。

这里的思路是先拿到创建post之前页面上的post数量，创建成功之后，页面上的post数量应该是+1的。

这里其实有个问题，如果页面上存量的post比较多的话，那么哪怕是再创建几个，页面上展示出来的post数量也是不会变化的，大家可以想想这是为什么。

解决思路其实有2个

- 每次跑用例之前清理一下数据库，保证数据库里post小于1页，这样就没有问题了
- 用api去拿post的数量，但是有可能存在数据写进去了，但是页面上的显示不发生变化的风险

## 快速上手 checklist

- [ ] 创建 `pages/` 目录，放所有 Page 类
- [ ] 创建 `conftest.py` 文件，定义 fixture
- [ ] 把常用前置操作（登录、导航）尽量封装成 fixture
- [ ] Page 类里多放组合方法（login、addToCart、checkout 等）

祝你写出优雅、可维护的 Playwright 测试！🚀
