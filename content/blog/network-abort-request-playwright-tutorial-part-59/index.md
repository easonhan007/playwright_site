+++
date = 2022-04-16
title = "playwright如何屏蔽页面上的各种弹出广告"
description = "用route就可以了"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

最近，我的一个被测网站添加了谷歌广告，这导致我之前编写的所有测试都失败了。一个从底部弹出的广告窗口覆盖在了自动化程序要点击的输入框上。

为了解决这个问题，我转向使用[route 方法](https://playwright.dev/docs/api/class-route)。这个方法允许拦截网络请求。`route`对象允许以下操作：

- abort - 中止路由的请求
- continue - 继续路由的请求，可选择重写部分内容（如重写头部）
- fulfill - 改写响应内容（如发送不同的状态码、内容类型或正文）
- request - 允许你以多种方式与[request 对象](https://playwright.dev/docs/api/class-request)交互。

对于这个特定的例子，我想编写代码来查找所有 URL 以`https://googleads.*`开头的请求并拦截它们，同时继续处理其余的请求。

以下代码块使用当前会话/测试的上下文，创建一个路由拦截器来监视所有请求。代码的第 2 行获取请求 URL 作为字符串，并使用`startsWith()`函数返回一个布尔值。如果为 true，则执行第 3 行（中止），否则执行第 4 行（继续）。然后返回响应。

```javascript
await context.route("**/*", (request) => {
  request.request().url().startsWith("https://googleads.")
    ? request.abort()
    : request.continue();
  return;
});
```

如果你想获取页面上发出的所有的异步请求列表，这段代码也很有用，把结果打印到控制台就可以了。这里的一个重要部分是要对请求做些处理，在下面的例子中我选择继续执行。如果你不使用`abort`、`continue`或`fulfill`，请求很可能会超时。

```javascript
await context.route("**/*", (request) => {
  console.log(request.request().url());
  request.continue();
  return;
});
```

尽情使用吧！

## 来源

URL 来源: https://playwrightsolutions.com/network-abort-request-playwright-tutorial-part-59/

发布时间: 2022 年 4 月 16 日 05:04:36
