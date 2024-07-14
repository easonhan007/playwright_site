+++
date = 2023-06-12
title = "如何在运行 Playwright 测试时获取底层网络请求的响应值？"
description = "playwright使用route直接用异步请求里返回的数据进行UI断言"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在页面上进行自动化操作时，我经常需要获取刚刚创建的某个对象的 `id` 或唯一标识符，用于断言或后续操作。通常，这些标识符可以在 UI 层操作的网络响应中找到。今天，我将展示如何抓取网络响应并在断言中使用它。

在这个测试中，我们将使用 [https://automationintesting.online/](https://automationintesting.online/)，这是一个预订网站。今天要抓取的具体值是登录后的消息通知数，该数值会根据系统中其他操作的不同而产生变化。步骤如下：访问上述网站，找到管理员登录链接，使用用户名: admin / 密码: password 并点击登录。你会在页面顶部看到通知框，如果查看 Chrome 开发工具的 Network tab 页，也会看到网络请求。

![Image 1](https://playwrightsolutions.com/content/images/2023/06/image.png)

👆 消息计数的 UI

![Image 2](https://playwrightsolutions.com/content/images/2023/06/image-1.png)

👆 Chrome 开发工具中的网络请求

在我的 Playwright 测试中，我计划使用 `page.route` 方法拦截流量。如果请求 URL 包含 `**/message/count`，则将响应设置为 `response` 变量，然后从 `response` 变量获取 json 并保存为名为 message 的变量。

需要注意的是，我在测试级别创建了 `message` 变量，这样可以在整个测试范围内访问它（而不仅仅是在 page.route 范围内）。如果遇到变量未定义的问题，请确保在正确的级别创建变量。

此外，我使用了 `let` 声明 `message` 变量，这样可以根据需要分配/重新分配值。

下面是一个具体例子，我在其中拦截了 message/count API 请求，并将 message 这个变量的值设置为请求的具体响应值。然后使用该 message 变量对屏幕上的内容进行断言。无论 API 返回什么值，我们将在 DOM 中检查该值。这确实帮助我们解决了测试数据问题，并且不需要用到 api mock。

```javascript
import { test, expect } from "@playwright/test";

test.describe("/admin Checks", async () => {
  test(`Validate Message Count is correct`, async ({ page }) => {
    let message;

    await page.route(
      "**/message/count",

      async (route) => {
        const response = await route.fetch();
        message = await response.json();
        route.continue();
      }
    );

    await page.goto("https://automationintesting.online/");
    await page.getByRole("button", { name: "Let me hack!" }).click();
    await page.getByRole("link", { name: "Admin panel" }).click();
    await page.locator('[data-testid="username"]').fill("admin");
    await page.locator('[data-testid="password"]').fill("password");
    await page.locator('[data-testid="submit"]').click();

    await expect(page.getByRole("link", { name: "Logout" })).toHaveText(
      "Logout"
    );

    const messageCountSpan = page
      .locator('[href*="#/admin/messages"]')
      .locator("span");

    // Wait for the message count to be updated before making an assertion
    await page.waitForResponse("**/message/count");
    await expect(messageCountSpan).toHaveText(`${message.count}`);
  });
});
```

这个代码可以在 Playwright-Demo 仓库中找到

[playwright-demo/messageCountIntercept.spec.ts](https://github.com/BMayhew/playwright-demo/blob/master/tests/ui/automationintesting.online/messageCountIntercept.spec.ts)

如果你想要一个模拟响应的示例，可以在这里找到

[如何在 Playwright 中通过特定响应模拟 HTTP 网络流量](https://playwrightsolutions.com/how-do-i-intercept-network-traffic-and-save-specific-values-from-http-requests/)

Tim Deschryver 撰写的精彩文章，包含更多示例，可以在这里找到

[使用 Playwright 拦截 HTTP 请求](https://timdeschryver.dev/blog/intercepting-http-requests-with-playwright)

![Image 9](https://playwrightsolutions.com/content/images/2023/06/image-2.png)

---

感谢阅读！如果你觉得这篇文章有帮助，请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上与我联系，或者考虑 [请我喝杯咖啡](https://ko-fi.com/butchmayhew)。如果你希望更多内容直接发送到你的收件箱，请在下方订阅，并确保留下 ❤️ 以示支持。

## 来源

来源网址: https://playwrightsolutions.com/get-a-response-value-of-an-underlying-network-request-when-running-a-playwright-test/

发布时间: 2023-06-12T12:30:52.000Z
