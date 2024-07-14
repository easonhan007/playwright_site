+++
date = 2023-11-20
title = "如何在 Playwright Test 中为 page.goto() 添加查询参数?"
description = "这里用到了拦截器的思想，不过代码里用了bind()，初学者理解起来会有点难度"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

虽然我们不常需要在特定请求中添加和验证查询参数,但本文的方法在测试使用 URL 参数的 [UTM](https://blog.hubspot.com/marketing/what-are-utm-tracking-codes-ht) 或其他类型的跟踪链接时会非常有用。

在本文中,我将测试 [https://practicesoftwaretesting.com](https://practicesoftwaretesting.com/) 这个站点。非常感谢 [Roy de Kleijn](https://www.linkedin.com/in/roydekleijn/) 提供这个优秀的测试资源!

[GitHub - playwrightsolutions/playwright-practicesoftwaretesting.com](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com)

我们先来编写一个简单的测试用例,访问页面并填写提交表单。最终目标可能是通过 UTM 代码跟踪某些操作,比如结账过程或支付行为。

```javascript
// tests/contact/contact.nofixtured.spec.ts

import { test, expect } from "@playwright/test";

test("首页测试", async ({ page }) => {
  await page.goto("");

  await page.getByTestId("nav-contact").click();
  await page.getByTestId("first-name").fill("Test");
  await page.getByTestId("last-name").fill("Mctester");
  await page.getByTestId("email").fill("asf@asdf.com");
  await page.getByTestId("subject").selectOption("payments");
  await page.getByTestId("message").fill("test".repeat(40));
  await page.getByTestId("contact-submit").click();
  await expect(page.locator(".alert-success")).toHaveText(
    "感谢您的留言!我们将尽快与您联系。"
  );
});
```

注意:上面的测试没有包含任何 URL 参数,也没有检查它们。有趣的是,当我访问[https://practicesoftwaretesting.com](https://practicesoftwaretesting.com/#/)

时,会被重定向到[https://practicesoftwaretesting.com/#/](https://practicesoftwaretesting.com/#/)

在添加 URL 参数时需要考虑这一点,因为参数会被添加到我们访问的网站上,但如果发生重定向,URL 参数就不会被保留。

如果你只有一个测试用例,可以直接将 URL 参数传入 `page.goto("/#/?UTM_SOURCE=playwright")`。但在我们的示例中,我们想让多个测试用例里的 url 都带上这个参数,比较好的方式是将实现一个扩展基本页面的[固定装置(fixture)](https://playwright.dev/docs/test-fixtures#creating-a-fixture)。

**乙醇的注释 👀: 学过前端的同学一看就懂了，这其实就跟拦截器很像**

```javascript
// lib/fixtures/modifiedGoto.ts

import { test as base } from "@playwright/test";

export const test = base.extend({
  page: async ({ page }, use) => {
    const goto = page.goto.bind(page);
    function modifiedGoto(url, options) {
      url += "?UTM_SOURCE=playwright";
      return goto(url, options);
    }
    page.goto = modifiedGoto;
    await use(page);
    page.goto = goto;
  },
});
```

我不会详细解释[如何创建 fixture](https://playwright.dev/docs/test-fixtures#creating-a-fixture),但会讲解 fixture 的逻辑。

首先,我们创建一个新变量 `goto`,它被设置为 `page.goto.bind(page)`。这里使用了 [bind() 函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_objects/Function/bind),用于创建一个新函数,其 `this` 值设置为 `page` 对象。

**乙醇的注释 👀: bind()是经典的 javascript 中比较容易迷糊的问题，大家可以让 ai 多举几个例子来理解**

接下来的代码添加了一个名为 `modifiedGoto()` 的新函数,它将替代 `goto()`。在这个函数中,我们将 `?UTM_SOURCE=playwright` 加到提供的 URL 字符串上并返回。

```javascript
function modifiedGoto(url, options) {
  url += "?UTM_SOURCE=playwright";
  return goto(url, options);
}
```

下一行 `page.goto = modifiedGoto;` 用 `modifiedGoto` 方法替换了原始的 `page.goto` 方法。

然后我们调用 `await use(page);`,这是一个回调函数,用于"在运行的测试中使用固定装置值"。

最后,我们调用 `page.goto = goto;`,在 `use` 函数调用后恢复原始的 `page.goto` 方法。

总的来说,我们现在有了一个功能性的 fixture,可以导入到任何测试用例中,并自动添加我们在 fixture 中指定的 URL 参数。让我们通过创建一个新的 `contact.spec.ts` 来测试它,该用例将使用 `@fixtures/modifiedGoto`。注意,我们在访问页面后添加了一个断言,以验证 UTM_SOURCE 是否存在于 URL 中!

```javascript
// tests/contact/contact.spec.ts

import { test } from "@fixtures/modifiedGoto";
import { expect } from "@playwright/test";

test("首页测试", async ({ page }) => {
  await page.goto("/#/");
  expect(page.url()).toContain("?UTM_SOURCE=playwright");

  await page.getByTestId("nav-contact").click();
  await page.getByTestId("first-name").fill("Test");
  await page.getByTestId("last-name").fill("Mctester");
  await page.getByTestId("email").fill("asf@asdf.com");
  await page.getByTestId("subject").selectOption("payments");
  await page.getByTestId("message").fill("test".repeat(40));
  await page.getByTestId("contact-submit").click();
  await expect(page.locator(".alert-success")).toHaveText(
    "感谢您的留言!我们将尽快与您联系。"
  );
});
```

这篇文章的灵感来自 [Playwright Discord](https://aka.ms/playwright/discord) 上 [Tomaj](https://discord.com/channels/807756831384403968/1160874346483564644) 的帖子。

![Image 3](https://playwrightsolutions.com/content/images/2023/11/image.png)

他提供了他的解决方案,让我了解到 `bind` 方法的"全新世界"!

---

感谢阅读!如果您觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑[为我买杯咖啡](https://ko-fi.com/butchmayhew)。如果您想在收件箱中收到更多内容,请在下方订阅,别忘了留下一个 ❤️ 来表示您的喜爱。

## 来源

URL 来源: https://playwrightsolutions.com/how-do-you-append-query-parameters-to-page-goto-using-playwright-test/

发布时间: 2023-11-20
