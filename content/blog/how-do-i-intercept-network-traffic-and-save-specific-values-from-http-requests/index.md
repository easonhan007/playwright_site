+++
date = 2024-07-09
title = "如何通过 Playwright 模拟特定响应的 HTTP 网络请求"
description = "playwright的常见套路就是拦截网络请求，然后mock返回值"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我最近遇到一个场景，我想检查一个 UI 元素，但 UI 元素中的数据是一个计数器，而我套件中的其他测试会影响这个计数。我看到有两种方法可以解决这个问题。一种是拦截网络流量并抓取这个值，然后对这个值进行断言，另一种方法是拦截并 mock(自己设置 1 个假的值) 一个我传入的值作为响应。

在本文中，我将演示一个简单的拦截和模拟网络请求的场景。

首先，我们创建一个名为`count`的变量，并将其设置为 100。这个值可以是任何数字，因为它将被传入测试名称、mockMessageCount 函数，并在断言中使用。

在这个测试中，我在 beforeEach 方法中有很多操作，理想情况下，我会将很多这些操作抽象到一个页面对象中，使测试更加简洁。这个测试假设在`test`部分开始时你已经登录。在 beforeEach 中，我还调用了`mockMessageCount(page, count)`方法。此代码调用了测试规范底部列出的异步函数。这个函数可以很容易地存在于不同的文件中，通过从它自己的文件中导出函数并在其他测试用例中导入。下面的代码使用 route 类，对于以"/message/count"结尾的任何 URL，我们将直接 mock 这个接口的返回值。我通过这个接口[https://automationintesting.online/message/count](https://automationintesting.online/message/count) mock 返回值。这是不需要身份验证的，所以你可以点击并查看当前的计数。

```typescript
export async function mockMessageCount(page, messageCount) {
  await page.route("**/message/count", (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ count: messageCount }),
    })
  );
}
```

由于我们在 mockMessageCount 中传入了 100 作为计数，因此在 Playwright 测试用例中 mock 了`100` 这个返回。完整的测试如下所示。

```typescript
import { test, expect, selectors } from "@playwright/test";

test.describe("/admin 检查", async () => {
  let count = "100";

  test.beforeEach(async ({ page }) => {
    selectors.setTestIdAttribute("data-testid");

    // 这调用了一个在此页面底部存在的异步函数，它接受页面实例和一个数字
    await mockMessageCount(page, count);
    await page.goto("https://automationintesting.online/");
    await page.getByRole("button", { name: "Let me hack!" }).click();
    await page.getByRole("link", { name: "Admin panel" }).click();
    await page.getByTestId("username").click();
    await page.getByTestId("username").fill("admin");
    await page.getByTestId("password").click();
    await page.getByTestId("password").fill("password");
    await page.getByTestId("submit").click();
  });

  test(`验证消息计数为${count}`, async ({ page }) => {
    await expect(page.getByRole("link", { name: "Logout" })).toHaveText(
      "Logout"
    );

    const messageCountSpan = page
      .locator('[href*="#/admin/messages"]')
      .locator("span");

    await expect(messageCountSpan).toHaveText(`${count}`);
  });
});

// 这个函数使用route类，拦截服务器发送的内容，并用我们提供的响应进行满足（模拟！）
export async function mockMessageCount(page, messageCount) {
  await page.route("**/message/count", (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ count: messageCount }),
    })
  );
}
```

### Playwright 文档链接

查看文档将帮助你更深入地了解 page.route 类的所有可能性。下面是一个简要总结。

- [页面类 - page.route()](https://playwright.dev/docs/api/class-page#page-route)
- [Route 类](https://playwright.dev/docs/api/class-route)

`abort()` 终止 route 的请求。

`continue()` 继续 route 的请求，并可选择性地进行覆盖。

`fallback()` 当多个路由匹配给定模式时，它们按照注册顺序的相反顺序运行。这样，最后注册的路由总是可以覆盖所有先前的路由。在下面的示例中，请求将首先由最底层的处理程序处理，然后它会回退到上一个，最后由第一个注册的路由终止。

`fetch()` 执行请求并获取结果，而不进行满足，以便可以修改响应然后进行满足。

`fulfill()` 使用给定的响应满足 route 的请求。

---

示例中的代码可以在这个仓库中找到。[代码示例](https://github.com/BMayhew/playwright-demo/blob/master/tests/ui/automationintesting.online/messageCount.spec.ts)

## 来源

[URL Source](https://playwrightsolutions.com/how-do-i-intercept-network-traffic-and-save-specific-values-from-http-requests/)

发布时间: 2023-04-24
