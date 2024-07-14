+++
date = 2023-02-06
title = "如何使用 Playwright 测试含页面重定向网页的网站?"
description = "省流: 最好用waitForURL"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在测试各种 Web 应用时,你不可避免的会遇到链接点击或页面操作导致重定向的情况。这种重定向可能通过 JavaScript 或 HTTP 请求实现。如果你想了解更多关于重定向实现方式的详细信息,可以参考[这篇指南](https://www.semrush.com/blog/redirects/)。

## 带重定向功能的示例网站

在这个演示中,我创建了一个简单的 HTML 页面,其中包含一个"重定向"按钮。

![图片 1](https://playwrightsolutions.com/content/images/2023/02/image.png)

👆 简单的带重定向按钮的网页

点击该按钮后,页面会添加一段文本,开始重定向过程,并添加一个点击后会弹出提示框的"订阅"按钮。以下是实现这个功能的代码。你可以在这个 GitHub 仓库的 public 文件夹中找到完整代码:[https://github.com/BMayhew/new-playwright-init/tree/master/public](https://github.com/BMayhew/new-playwright-init/tree/master/public)

```javascript
function redirect() {
  // 重定向前显示消息
  document.write("4秒后将重定向到新的URL...");

  // 4秒后重定向到新页面
  setTimeout(function () {
    window.location = "https://playwrightsolutions.com/";
  }, 4000);

  const button = document.createElement("button");

  button.innerText = "订阅";
  button.addEventListener("click", () => {
    alert("你点击了订阅按钮!");
  });
  document.body.appendChild(button);
}
```

## 一个失败的 Playwright 测试用例

为了使这个练习更有趣,我在重定向页面上也添加了一个"订阅"按钮。现在,我们编写一个测试用例:访问主页,点击重定向按钮,等待 4 秒,然后页面重定向到 PlaywrightSolutions.com 主页。之后,我们要点击"订阅"按钮,并开始填写订阅信息。

```javascript
import { test, expect } from "@playwright/test";

test("访问主页并完成订阅", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000");
  await page.locator("text=重定向").click();

  await page.locator("text=订阅").click();

  const popup = page.frameLocator('iframe[title="portal-popup"]');
  await popup.locator("id=input-name").fill("test");
  await popup.locator("text=注册").click();

  expect(popup.locator("text=输入你的邮箱地址")).toBeVisible;
});
```

然而,当我运行这段代码时,测试并没有按预期进行。它点击了重定向之前的页面上的"订阅"按钮,而不是 PlaywrightSolutions.com 页面上也就是重定向之后的页面上的"订阅"按钮。因此,脚本在执行 `await popup.locator("id=input-name").fill("test");` 这一步时失败了。
![图片 2](https://playwrightsolutions.com/content/images/2023/02/image-1.png)

## 测试超时错误详情

出现这个问题的原因是,一旦点击"重定向"按钮,重定向页面上就出现了一个匹配"订阅"文本的元素。测试脚本立即点击了这个元素,触发了一个警告框。当重定向最终完成时,已经没有可以输入名字的弹出窗口了。

## page.waitForURL 解决方案(推荐做法)

解决这个问题有几种方法,但最简单有效的是使用 page 对象的 [waitForURL 方法](https://playwright.dev/docs/api/class-page#page-wait-for-url)。我们只需在点击重定向按钮之后,点击订阅按钮之前添加这个等待。waitForURL 命令可以使用完整 URL、glob 模式或正则表达式。更多细节可以查阅上面链接的文档。这个解决方案在使用 [`--repeat-each=10`](https://playwrightsolutions.com/in-playwright-test-is-there-an-easy-way-to-loop-the-test-multiple-times-to-check-for-flakiness/) [参数](https://playwrightsolutions.com/in-playwright-test-is-there-an-easy-way-to-loop-the-test-multiple-times-to-check-for-flakiness/)多次运行时表现稳定。

```javascript
test("访问主页并完成订阅 - 使用 waitForURL", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000");
  await page.locator("text=重定向").click();

  await page.waitForURL("https://playwrightsolutions.com/");

  await page.locator("text=订阅").click();

  const popup = page.frameLocator('iframe[title="portal-popup"]');
  await popup.locator("id=input-name").fill("test");
  await popup.locator("text=注册").click();

  expect(popup.locator("text=输入你的邮箱地址")).toBeVisible;
});
```

## 使用 page.waitForURL 和 JavaScript Promise

虽然代码稍长,但在遇到复杂情况时,你可以使用下面这种基于 Promise 的方法,这也是[官方文档](https://playwright.dev/docs/navigations#multiple-navigations)中提到的。需要注意的是,曾经有一个名为 `waitForNavigation()` 的方法,但由于存在竞态条件问题,现已被弃用。使用下面的 Promise 方法时,我发现还需要在点击"订阅"按钮前添加 `page.waitForLoadState()`。相比之下,单独使用 `await page.waitForURL()` 的优势在于它内置了导航等待,默认会等到 `load` 事件触发才认为操作完成。

```javascript
test("访问主页并完成订阅 - 使用 Promise", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000");

  // 在点击之前开始等待导航,注意这里没有 await
  const navigationPromise = page.waitForURL("https://playwrightsolutions.com/");

  // 触发导航的操作
  await page.locator("text=重定向").click();
  await navigationPromise;

  await page.waitForLoadState("networkidle");
  await page.locator("text=订阅").click();

  const popup = page.frameLocator('iframe[title="portal-popup"]');
  await popup.locator("id=input-name").fill("test");
  await popup.locator("text=注册").click();

  expect(popup.locator("text=输入你的邮箱地址")).toBeVisible;
});
```

另一种使用 `Promise.all([])` 的方法,它会等待数组中所有的 Promise 都 resolve 后才继续:

```javascript
test("访问主页并完成订阅 - 使用 Promise.all", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000");

  await Promise.all([
    // 重要:在点击之前设置等待导航
    page.waitForURL("https://playwrightsolutions.com/"),
    // 触发导航的操作
    page.locator("text=重定向").click(),
  ]);

  await page.waitForLoadState("networkidle");
  await page.locator("text=订阅").click();

  const popup = page.frameLocator('iframe[title="portal-popup"]');
  await popup.locator("id=input-name").fill("test");
  await popup.locator("text=注册").click();

  expect(popup.locator("text=输入你的邮箱地址")).toBeVisible;
});
```

![图片 3](https://playwrightsolutions.com/content/images/2023/02/image-2.png)

👆 梗图，开个玩笑

## 使用 expect().toPass() 的反模式做法

首先要强调,请不要在实际项目中这样做。我展示这种方法只是为了说明它的可能性。在最近的一个版本中,Playwright 引入了 .toPass() 方法,允许在特定的断言块内进行重试。你可以利用这个特性来等待 page.url() 变为期望的值。为了减少这种方法的不稳定性,我不得不添加 `await page.waitForLoadState("networkidle");` 这一行,它会等待网络活动至少停止 500ms 才继续。但这种方法无法保证在继续之前 DOM 和所有网络请求都已完成。再次强调,这种方法不推荐使用,仅作为技术探讨!

```javascript
test("访问主页并完成订阅 - 反模式", async ({ page }) => {
  await page.goto("http://127.0.0.1:3000");

  await page.locator("text=重定向").click();

  await expect(async () => {
    expect(page.url()).toBe("https://playwrightsolutions.com/");
  }).toPass();

  await page.waitForLoadState("networkidle");
  await page.locator("text=订阅").click();

  const popup = page.frameLocator('iframe[title="portal-popup"]');
  await popup.locator("id=input-name").fill("test");
  await popup.locator("text=注册").click();

  expect(popup.locator("text=输入你的邮箱地址")).toBeVisible;
});
```

我希望这些方法能帮助你更轻松地处理网页重定向测试。如果你已经读到这里,那真是太棒了! 🙌 不过,我还是建议你重点关注 `page.waitForURL 解决方案` 部分的第一种方法,这才是最佳实践。

---

感谢你的阅读!如果你觉得这篇文章有帮助,欢迎在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上与我联系,或者考虑[请我喝杯咖啡](https://ko-fi.com/butchmayhew)。如果你想接收更多类似的内容,可以在下方订阅我们的通讯。

## 来源

[URL 来源](https://playwrightsolutions.com/how-do-i-test-a-website-that-has-a-page-redirect-with-playwright/)

发布时间:2023 年 2 月 6 日 13:30:22
