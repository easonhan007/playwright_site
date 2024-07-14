+++
date = 2024-04-04
title = "Playwright 技巧与诀窍 #3"
description = "用Promise.all()来实现并发"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

让我们深入了解 Playwright 的内部机制,掌握一些细节,从而提升我们的创造力。

## 1. 在测试运行期间获取更多测试详情

你可以实时访问与测试相关的特定值。假设你有一个复杂项目,其配置基于环境、测试数据或其他细节而动态变化,你想在测试运行时查看具体设置的值。可以通过在测试中访问 `testInfo` 对象来实现。以下是一个代码示例:

```javascript
import { test } from "@playwright/test";

test.describe("测试套件名称", () => {
  test("测试名称", async ({ page }, testInfo) => {
    console.log(`测试名称: ${testInfo.title}`);
    console.log(`并行索引:${testInfo.parallelIndex}`);
    console.log(`分片索引: ${JSON.stringify(testInfo.config.shard)}`);
  });
});
```

下面是通过 `testInfo` 可以访问的其他值的截图

![图片 1](https://blog.martioli.com/content/images/2024/03/image.png)

![图片 2](https://blog.martioli.com/content/images/2024/03/image-1.png)

我的[关于并发执行的文章](https://blog.martioli.com/full-parallelization-with-playwright/)展示了如何利用这个对象来显示特定值。

---

## 2. 如何使用 Playwright 测试多个浏览器窗口?

以下是测试多个窗口的方法。注意,这里指的是多个窗口,而不是同一窗口中的多个标签页。每个窗口都有自己的存储和 cookie。一个用例可能是测试网站的聊天功能,你想验证消息是否正确传递。你可以用两个浏览器分别登录两个用户,让他们互相聊天。如何在 Playwright 的单个测试中实现这一点呢?

我们可以使用 `browser` 和 `page` 对象。下面是一个代码示例:

```javascript
import { test, expect } from "@playwright/test";

test("两用户聊天功能", async ({ browser }) => {
  // 打开两个浏览器,每个都有自己的存储和 cookie
  const user1Context = await browser.newContext();
  const user1Page = await user1Context.newPage();
  const user2Context = await browser.newContext();
  const user2Page = await user2Context.newPage();

  // 打开聊天页面
  await user1Page.goto("https://www.yourweb.com/chat");
  await user2Page.goto("https://www.yourweb.com/chat");
  // 这里还需要添加登录凭证等详细信息

  // 按顺序进行对话

  await user1Page.getById("input").type("你好,用户2");
  await user1Page.getById("sendMsgBtn").click();

  await expect(user2Page.getByText("你好,用户2")).toBeVisible();
  await user2Page.getById("input").type("哦!你好,用户1");
  await user2Page.getById("sendMsgBtn").click();

  await expect(user1Page.getByText("哦!你好,用户1")).toBeVisible();
});
```

当然,聊天只是一个例子,你可以根据需要应用到其他场景。

## 3. Playwright 如何处理同一浏览器中的多个标签页?

对于某些元素具有 `target="_blank"` 属性,点击后会打开新标签页的情况,可以参考 [Playwright 文档中的这部分](https://playwright.dev/docs/pages?ref=blog.martioli.com#handling-new-pages)。如果你觉得 `const pagePromise = context.waitForEvent('page')` 难以理解,可以将其视为一个事件监听器,它不会阻塞测试,只是在监听。在执行打开新标签页的点击操作后,立即添加 `const newPage = await pagePromise`,之后就可以像使用上面例子中的 `user2Page` 一样使用 `newPage` 了。现在你可以在 `newPage` 对象或初始页面对象之间切换,无需额外操作。熟悉 Selenium 的人可能记得使用 `driver.switchTo().window(actual)` 来回切换,在 Playwright 中不再需要这样做。这里每个页面都有自己的对象。

如果你想完全理解这种"监听"事件(如新页面打开)的技巧,建议仔细阅读第 6 点。这不是一个简单的概念,但我相信你读完解释后就能掌握它。

请记住:

- browser.newContext() = 新窗口 (还不是完整的浏览器,还需要一个标签页)

- context.newPage() = 新标签页

下面是更多示例用来帮助理解。请仔细阅读注释。

```javascript
import { test } from "@playwright/test";

test("默认方式的多窗口和标签页", async ({ page }) => {
  // Playwright 的默认使用方式
  // page 包含了你在配置中设置的浏览器信息
  // 可以直接使用,无需额外操作
  // 这会打开一个窗口(context)和一个标签页(page)
  await page.goto("https://duckduckgo.com/");
});
```

```javascript
import { test } from "@playwright/test";

test("多窗口和标签页", async ({ browser }) => {
  // 这创建了一个新窗口,但你还不能对 page2Context 执行操作
  // 因为它还不完整,还需要一个标签页
  const page2Context = await browser.newContext();

  // 我们有了浏览器和窗口,只需要一个标签页。这样做:
  const page2 = page2Context.newPage();
});
```

尝试混合使用:

```javascript
import { test } from "@playwright/test";

test("混合使用多窗口和标签页", async ({ page, context, browser }) => {
  // 这会正常打开一个完整的浏览器,包含窗口和标签页(默认方式)
  await page.goto("https://duckduckgo.com/");

  // 这会在同一个窗口(context)中创建一个新标签页
  const page2 = await context.newPage();
  await page2.goto("https://martioli.com/");

  // 这会设置一个新的浏览器窗口和标签页
  // 独立于上面的操作
  const page3Context = await browser.newContext();
  const page3 = await page3Context.newPage();
  await page3.goto("https://github.com/adrianmaciuc");
});
```

---

## 4. 如何在一个测试中处理多种类型的浏览器?

下面我要展示的不是测试多个浏览器的方法。有更高效的方式来做这件事。我不确定是否会写关于这个的文章,因为它相当简单,网上也有很多这样的教程。但为了让我们深入了解浏览器实例是如何创建的,看看下面如何直接在测试范围内操作各种浏览器。

```javascript
import { test, webkit, firefox, chromium } from "@playwright/test";

test("多浏览器驱动", async () => {
  const browser = await webkit.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("https://martioli.com/");

  const browser2 = await firefox.launch();
  const context2 = await browser2.newContext();
  const page2 = await context2.newPage();
  await page2.goto("https://martioli.com/");
});
```

注意这里没有使用 { browser, page }。我们把 webkit 和 firefox 对象直接引入了测试范围。这样做有点牵强,但为了理解原理并可能在未来开发一些创新想法,了解它的工作方式是有好处的。

记住,在正常设置中,当你只使用 `test` 并解构 `{ page }` 时,这个对象会带有你在 Playwright 配置文件中设置的浏览器信息,或者可以通过终端命令或流水线动态设置的值。

对 JAVA 爱好者来说,还记得下面这些代码吗?

```javascript
import org.openqa.selenium.chrome.ChromeDriver;

WebDriver driver = new ChromeDriver()
driver.get("https://www.martioli.com")
```

如果你有 Java 和 Selenium 的背景,那么我上面所有关于如何实例化和处理驱动程序的解释对你来说都很有意义。你也会理解,我们不再需要编写任何其他代码来使 driver 对象准备就绪。我们不是必须这样做,但如果想要也没有问题。

---

## 5. 我可以在测试中覆盖 Playwright 的配置项吗?

我们都知道 **playwright.config** 文件[包含了配置](https://playwright.dev/docs/test-configuration?ref=blog.martioli.com),帮助我们进行项目的设置,所有测试都会使用这些配置运行。但如果**我想仅为一个测试或一组测试覆盖配置**呢?

如果我想让一组测试使用一套配置,另一组使用另一套配置,该怎么办?

你可以通过**两种方式**实现:

**简单方法: 创建一个[项目](https://playwright.dev/docs/test-projects?ref=blog.martioli.com),并为该项目编写所有[use 选项](https://playwright.dev/docs/test-use-options?ref=blog.martioli.com)**

第一种方法的示例如下:

```javascript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  projects: [
    (name: "项目名称"),
    (use: {
      ...devices["Desktop Chrome"],
      colorScheme: "dark",
      locale: "fr-FR",
      httpCredentials: {
        username: "你的用户名",
        password: "你的密码",
      },
      testIdAttribute: "data-testid",
    }),
    // 这里可以添加任何其他配置
  ],
});
```

默认情况下,运行测试时会对所有项目执行所有测试。所以请确保使用 `--project=项目名称` 指定要运行的项目。

**非正式方法: 在测试中覆盖配置值**

对于第二种方法,假设你希望特定的测试集或 spec 文件中的测试用例使用特殊的地理位置或 window 设置,或者某个测试需要绕过登录过程。换句话说,[这里列出的](https://playwright.dev/docs/test-use-options?ref=blog.martioli.com)任何值都可以在测试中进行操作。实现方法如下:

```javascript
import { test } from "@playwright/test";

test.use({
  geolocation: { longitude: 36.095388, latitude: 28.0855558 },
  userAgent: "我的超级秘密代理值",
});

test("覆盖配置", async ({ page }) => {
  await page.goto("https://martioli.com/");
});
```

这将保留其他设置,只覆盖你需要的部分。

**彩蛋 -> 告诉我这里地理位置对应的地点名称,你将赢得我的金牌读者称号**

如果你想在同一个 spec 文件中有多个测试集,每个测试集都有自己的额外配置,可以这样做:

```javascript
import { test, expect, webkit, firefox, chromium } from "@playwright/test";

test.describe("覆盖套件 1", () => {
  test.use({
    viewport: { width: 400, height: 810 },
    geolocation: { longitude: 36.095388, latitude: 28.0855558 },
    userAgent: "我的超级秘密代理值",
  });

  test("覆盖测试 1", async ({ page }) => {
    await page.goto("https://martioli.com/");
  });
});

test.describe("覆盖套件 2", () => {
  test.use({
    viewport: { width: 768, height: 1024 },
    geolocation: { longitude: 36.095388, latitude: 28.0855558 },
    userAgent: "我的第二个超级秘密代理值 2",
  });

  test("覆盖测试 2", async ({ page }) => {
    await page.goto("https://martioli.com/");
  });
});
```

如果你想在 spec 文件级别应用相同的覆盖配置,只需将 test.use() 移到文件顶部,它就会应用于文件中的所有套件。

配置也可以通过 [globalSetup](https://playwright.dev/docs/test-configuration?ref=blog.martioli.com#advanced-configuration) 完成。这是一种更优雅和高级的方法。我可能会在未来写一篇关于它的博文。

虽然不那么优雅,但还有另一种方法,你可以使用 context 传入配置覆盖。

```javascript
import { test, devices } from "@playwright/test";

test("覆盖测试 1", async ({ browser }) => {
  const context = await browser.newContext({
    ...devices["iPhone 13"],
    isMobile: true,
  });
  const page = await context.newPage();
  await page.goto("https://martioli.com/");
});
```

---

## 6. Playwright 中的 Promise.all

我想讨论这个问题,因为我经常看到人们在使用 Playwright 进行项目开发时,并不完全理解何时应该使用 Promise.all()。我会引用一个最佳解释(不是我的原话):

我将用 `waitForResponse()` 方法来举例说明

假设我们有一个搜索输入框和一个触发搜索的按钮,最终会向 API 发送请求([https://example.com/api/search](https://example.com/api/search?ref=blog.martioli.com),搜索词在请求体中)

你可能会这样写代码:

```javascript
await page.locator("button").click(); // 搜索按钮

await page.waitForResponse("https://example.com/api/search");
```

上面的代码存在一个(很高的)可能性:在我们执行到 `await page.waitForResponse("https://example.com/api/search")` 这一行之前,我们已经收到了来自 [`https://example.com/api/search`](https://example.com/api/search?ref=blog.martioli.com) 的响应。`.click()` 方法不会立即 resolve,而是在 resolve await promise 并继续到下一行之前执行一系列(耗时的)步骤。

**敲黑板，乙醇的评论 👀。上面是原文的翻译，我尽力了，不过大家可能还是看不懂。其实作者的意思是上面的代码里`waitForResponse()`只有等到`click()`运行结束之后才会执行，而我们的目标是让这两行代码同时执行**

Await 按顺序异步执行代码,一个接一个。

我们真正想要的是 `await page.locator("button").click()` 和 `await page.waitForResponse("https://example.com/api/search")` 同时执行 - 这样两者都能正确完成各自的工作。

这就是 Promise.all() 发挥作用的地方。

Promise.all() 并发执行 promises,这意味着,

```javascript
const [response] = await Promise.all([
  page.locator("button").click(),
  page.waitForResponse("https://example.com/api/search"),
]);
```

同时执行 `.click()` 和 `.waitForResponse()`。整个 await Promise.all() 只有在所有传入的 promise 参数都 resolve 后才会 resolve。我们在这里遇到的问题被称为竞态条件。

许多 Playwright 事件 `(.waitForRequest(), .waitForResponse(), .waitForEvent(), ...)` 必须使用 Promise.all 与它们的触发器并发执行。

这里是[完整解释的链接](https://github.com/microsoft/playwright/issues/5470?ref=blog.martioli.com#issuecomment-1285640689),感谢 [advename](https://github.com/advename?ref=blog.martioli.com)

如果你觉得这篇文章有用,请点击鼓掌按钮。或者如果你想给我更多动力,[给我买杯咖啡](https://ko-fi.com/adrianmaciuc?ref=blog.martioli.com)也行。

## 来源

[URL Source](https://blog.martioli.com/playwright-tips-and-tricks-3/)

Published Time: 2024-04-04
