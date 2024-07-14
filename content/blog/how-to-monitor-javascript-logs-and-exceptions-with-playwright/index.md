+++
date = 2024-06-21
title = "如何使用Playwright监控JavaScript控制台日志和异常"
description = "省流: 用page.on()进行监听"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## 目录

监控 JavaScript 日志消息是了解浏览器 上 JavaScript 运行情况的基本方法。Playwright 提供了一种高效的方式来监听页面中的控制台日志和未捕获的异常。这一功能对于开发人员和测试人员来说非常宝贵,可以帮助他们在开发周期的早期发现和解决问题。本文将指导您如何设置 Playwright 来监控 JavaScript 日志和异常,从而增强您的测试策略。

## 环境设置

测试需要一个基本的 Playwright 环境。设置过程很简单,您可以在[Playwright 官方文档](https://playwright.dev/docs/intro)中找到详细说明。您也可以[使用 Checkly 编写和运行首个 Playwright 测试](https://www.checklyhq.com/docs/cli/)。

之后,最好能在一个具有完全可预测日志消息和错误的页面上折腾。在我的例子中,我搭建了一个简单服务,其页面内代码如下:

consoleLogsAndErrors.js

```javascript
console.error("你好,这是一个错误");
console.log("这是一条日志消息");
//未捕获的异常会中断JS执行,不要在生产环境中这样做! :)
throw new Error("不要在try/catch块外这样做!");
```

一旦您的环境准备就绪,就可以开始折腾本文讨论的技术了。

## 监听控制台日志消息

JavaScript 应用程序可以生成各种类型的控制台消息,包括日志、警告和错误。这些消息通常表示应用程序的状态或需要注意的问题。Playwright 允许您通过为页面对象添加控制台事件监听器来捕获这些消息。

### 实现控制台监听器

要监听控制台消息,您需要为页面对象添加一个事件监听器,如下所示:

```javascript
page.on("console", (msg) => {});
```

这可以观察并响应控制台的日志输出。我们很容易会想到简单地在这个内部函数中使用 console.log 来记录每条日志消息。然而,以下代码是无效的:

```javascript
page.on("console", (msg) => {
  console.log(message);
});
```

这个内部的`console.log()`会在页面加载过程中被执行,而 Playwright 在执行测试时并不会显示出来。相反,你应该在页面加载前初始化一个数组,然后将消息推送到数组中。

```javascript
test("本地主机错误日志记录", async ({ page }) => {
  const logs = [];
  // 监听所有控制台日志
  page.on("console", (msg) => {
    logs.push({ msg, type: msg.type() });
  });
  // 监听所有控制台事件并处理错误
  await page.goto("localhost:3000");
  console.log(logs);
});
```

在这个例子中,我们将每条控制台消息推送到一个`logs`数组中,包括消息类型和消息文本。然后我们输出`logs`数组(注意,这段代码实际上并不包含断言,永远不会失败)。

## 理解 ConsoleMessage 类

Playwright 的`ConsoleMessage`类代表页面上的控制台消息事件,如日志、警告、错误、调试消息等。每个`ConsoleMessage`实例提供有关消息的详细信息,包括其类型、文本、位置(URL 和行号),以及[传递给控制台方法的任何参数](https://playwright.dev/docs/api/class-consolemessage)。

### 按类型过滤消息

在许多情况下,您可能对监控特定类型的消息感兴趣,如错误或警告。您可以使用`ConsoleMessage`类的`type()`方法按类型过滤消息:

```javascript
const errors = [];
page.on("console", (message) => {
  if (message.type() === "error") {
    errors.push(`错误消息: ${message.text()}`);
  }
});
```

这种技术特别有助于监控可能影响应用程序功能或用户体验的关键问题。

虽然有[日志有 18 种类型](https://playwright.dev/docs/api/class-consolemessage),但我们最可能遇到的是`log`、`debug`、`info`、`error`和`warning`。

### 访问消息位置

Playwright 允许您访问生成控制台消息的位置,包括 URL、行号和列号。这些信息对调试非常有价值,因为它们可以精确定位消息的确切来源:

```javascript
page.on("console", (message) => {
  const location = message.location();
  logs.push(
    `来自 ${location.url}:${location.lineNumber}:${location.columnNumber} 的消息`
  );
});
```

如果您使用上面"设置"部分中的演示 JS,结果将是:

```bash
[
  '来自 http://localhost:3000/index.js:0:8 的消息',
  '来自 http://localhost:3000/index.js:1:8 的消息'
]
```

### 在测试中断言控制台消息

高级监控还包括在测试中断言特定控制台消息的存在或不存在。通过将消息收集到数组中,您可以对测试执行期间应该或不应该出现的消息进行断言:

```javascript
test("本地主机错误日志记录", async ({ page }) => {
  const logs = [];
  page.on("console", (msg) => logs.push(msg.text()));
  await page.goto("localhost:3000");
  console.log(logs); // [ '你好,这是一个错误', '这是一条日志消息 苹果' ]
  expect(logs).toContain("你好,这是一个错误");
});
```

注意,`toContain`是一个简单的字符串匹配,不接受正则表达式模式。在上面的代码里,运行`expect(logs).toContain('苹果')`将会失败,因为它需要完全匹配数组中的字符串。

## 捕获未处理异常

未捕获的异常是可能让应用程序无法正常运行的关键错误。Playwright 提供了一种简单的方法来使用 pageerror 事件捕获这些异常。

### 实现异常监听器

与捕获控制台消息类似,您可以通过为 pageerror 事件添加事件监听器来监听未捕获的异常:

```javascript
const errors = [];
page.on("pageerror", (exception) => {
  errors.push(exception.message);
});
// 稍后在测试中
console.log(errors); //[ '不要在try/catch块外这样做!' ]
```

在这里,我们将异常消息收集到一个 errors 数组中。这种方法允许您收集和监控在 Playwright 测试用例执行期间发生的未捕获异常。

## 基于日志和异常进行断言

有了捕获的控制台消息和异常,您现在可以断言某些条件,以确保您的应用程序按预期运行。例如,您可能想验证是否没有错误或警告消息:

```javascript
await page.goto("http://localhost:8080");
// 额外的测试步骤...
expect(logs).toHaveLength(0);
expect(errors).toHaveLength(0);
```

这些断言确认在测试执行期间没有遇到控制台消息或未捕获的异常。如果捕获到任何消息或异常,测试将失败。请注意,对日志消息数量进行过多断言可能不是一个好主意,特别是当您期望的数量不是零时，想想自动化测试的目的是什么？是尽量模拟用户的操作，真实的用户对控制台的 js 日志是不感兴趣的。

## 使用软断言进行持续监控

** ❌ 乙醇的注释 👀: 这里的实现方式有问题，正确的实现应该是用[excpet.soft](https://playwright.dev/docs/test-assertions#soft-assertions)**

在某些情况下,您可能希望即使遇到日志消息或异常,也能继续运行测试。这可以通过实现软断言来实现,它允许测试继续进行,同时仍然报告遇到的问题，也就是测试用例不失败，但是错误却会被记录下来

```javascript
// 软断言实现示例
if (logs.length > 0) {
  console.warn("检测到控制台消息:", logs);
}
if (errors.length > 0) {
  console.error("检测到未捕获的异常:", errors);
}
```

软断言特别适用于当作日志来用。

## 更进一步

监控 JavaScript 的日志消息和异常是提高 Web 应用质量的强大技术。Playwright 在自动化测试中实现这种监控非常简单,为潜在问题提供了有价值的视角,并确保您的应用程序满足所需的可靠性和性能标准。通过将这些实践纳入您的测试策略,您可以主动解决问题,从而构建一个更加稳健和无错误的应用程序。

要查看 Playwright 中的日志消息实际效果,请观看 Checkly YouTube 页面上的这个视频:

如果您想加入 Playwright 用户社区,[请加入 Checkly Slack](https://www.checklyhq.com/slack/),其中有我们出色的#Playwright-Community 频道。

## 来源

来源 URL: https://www.checklyhq.com/blog/how-to-monitor-javascript-logs-and-exceptions-with-playwright/

发布时间: 2024-06-21
