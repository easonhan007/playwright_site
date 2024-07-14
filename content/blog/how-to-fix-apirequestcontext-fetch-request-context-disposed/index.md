+++
date = 2023-10-23
title = "playwright如何修复 apiRequestContext.fetch报错:context disposed"
description = "测试用例运行完了但是请求却没有结束的时候就可能发生这样的错误，可以用waitForResponse来解决"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在工作中进行自动化测试时,我发现在使用 `await page.route()` ([文档](https://playwright.dev/docs/api/class-route))功能时,测试中经常出现以下两个错误:

```
错误: apiRequestContext.fetch: Request context disposed
错误: apiRequestContext.fetch: Browser has been closed

还送了个错误
1 error was not a part of any test, see above for details
```

这种情况通常发生在页面中有一个或一组网络请求,而测试在 API 请求完成前就结束了。

## 复现问题

我有一个例子,大约每 10 次运行就能复现一次。如果你想看到失败情况,可以下载代码库并运行以下命令:

`npx playwright test tests/checkout/checkoutWithRoute.spec.ts --repeat-each 20`

[代码在这里](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com)

这个测试的代码如下。请注意,我没有添加任何断言,因为我用这个例子来验证一个可以解决上述错误的方案。

```javascript
// checkoutWithRoute.spec.ts

import { expect } from "@playwright/test";
import { test, HomePage } from "@pages";

test.describe("UI与API路由", () => {
  test("检查已释放的api上下文", async ({ page }) => {
    await page.route(
      "https://api.practicesoftwaretesting.com/products?**",
      async (route) => {
        const response = await page.request.fetch(route.request());
        const responseBody = await response.json();
        route.continue();
      }
    );

    const homePage = new HomePage(page);
    await homePage.goto();
  });
});
```

测试报告中错误的示例 👇

![Image 3](https://playwrightsolutions.com/content/images/2023/10/image-2.png)

这种情况发生的原因是,即使测试已经运行完毕,网络请求仍未完成。一般情况下这种错误并不会发生,但如果你正在路由多个请求,或者应用程序正在获取大量数据,这种情况就非常有可能发生。

## 防止或修复这些错误的技巧

### 检查测试文件中的 await 语句

首先,确保你已正确地"await"了所有浏览器或网络交互,例如:`await homePage.goto()`。如果你没有正确地等待这些操作,可能会在测试结束时出现这些错误,或者在不同的地方出现错误,这取决于哪些操作仍在进行。

### 使用 waitForResponse()

接下来,在测试结束前使用`await page.waitForResponse()`([文档](https://playwright.dev/docs/api/class-page#page-wait-for-response))函数,以确保所有网络流量都已响应。看下面的例子,现在这个测试永远不会因为网络连接仍然打开而失败。

```javascript
// checkoutWithRoute.spec.ts

import { expect } from "@playwright/test";
import { test, HomePage } from "@pages";

test.describe("UI与API路由", () => {
  test("检查已释放的api上下文", async ({ page }) => {
    await page.route(
      "https://api.practicesoftwaretesting.com/products?**",
      async (route) => {
        const response = await page.request.fetch(route.request());
        const responseBody = await response.json();
        route.continue();
      }
    );

    const homePage = new HomePage(page);
    await homePage.goto();

    await page.waitForResponse(
      "https://api.practicesoftwaretesting.com/products?**"
    );
  });
});
```

### 使路由更加具体

在我工作的代码库中,我们有一个报告页面,它获取所有支付信息,最终会路由超过 10 个匹配以下模式的 API 调用:

`await page.route("**/payment-intents?**", ...`

一个解决方案是使我的路由更加详细,不使用正则表达式匹配,比如这样。对于我测试中的断言,我实际上只需要加载前 25 个请求。限制通过 page.route()路由的请求数量应该可以帮助解决这类问题。

`await page.route("**/payment-intents?offset=0&limit=25", ...`

## 总结

总的来说,这些错误可能很难排查和解决,主要是因为我们测试的系统的网络时序问题。如果你有其他处理这些问题的技巧或窍门,请在 LinkedIn 上联系我,告诉我!

---

感谢阅读!如果你觉得这篇文章有帮助,请在[LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew)上联系我,或者考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱里收到更多内容,请在下方订阅,别忘了留下 ❤️ 表示支持。

## 来源

URL 来源: https://playwrightsolutions.com/how-to-fix-apirequestcontext-fetch-request-context-disposed/

发布时间: 2023-10-23T12:30:01.000Z
