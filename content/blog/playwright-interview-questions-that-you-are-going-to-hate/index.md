+++
date = 2024-05-05
title = "你会讨厌的 Playwright 面试题"
description = "全是细节"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

这些问题是设计来考你的，所以如果你答不对，不要太苛责自己。此外，一些答案有解释，甚至还有代码示例。滚动到页面底部查看详细内容。记住，这些都是可以运行的代码，使用了真实的 URL，所以你可以尝试复制粘贴这些代码看看效果。

## 1\. 本地环境

如果你要在本地机器上使用你设置好的本地环境运行测试，比如在 [http://localhost:3000/](http://localhost:3000/?ref=blog.martioli.com) ，你会如何处理测试运行期间的本地环境设置？

可能的答案：

- 在运行测试之前启动你的本地环境
- 在 package.json 中编写脚本来启动本地环境并运行测试
- 使用 webServer

#### 答案

所有可能的答案都是有效的，但推荐使用 [webServer](https://playwright.dev/docs/api/class-testconfig?ref=blog.martioli.com#test-config-web-server) 配置

[**查看解释**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#content-below-is-visible-to-members-only)

---

## 2\. 包含比较

除了一个接受 `locator` 而另一个接受 `value` 之外，以下两者之间的主要区别是什么：

`await expect(locator).toContainText()`

和

`await expect(value).toContain()`

#### 答案

第一个是一个 [自动重试](https://playwright.dev/docs/test-assertions?ref=blog.martioli.com#auto-retrying-assertions) 断言，意味着它会在 5 秒内重试，直到元素出现，而第二个只会尝试断言一次。

---

## 3\. 延迟加载

在以下 URL 中，文本“加载完成”将在 10 秒后出现。我们的测试在 `expect` 步骤中失败，错误为 `Expected: visible , Received: hidden`。你如何修复这个测试？

```javascript
test("The visible methods", async ({ page }) => {
  await page.goto("https://webdriveruniversity.com/Accordion/index.html");
  await expect(page.getByText("LOADING COMPLETE.")).toBeVisible();
});
```

#### 答案

默认的 `expect` 超时时间为 5 秒，如果元素在此时间内不可见，测试将失败。为修复此测试，我们将仅在此步骤中延长超时时间，超过已知的 10 秒延迟，如下所示：`await expect(page.getByText("LOADING COMPLETE.")).toBeVisible({ timeout: 12000 })`

---

## 4\. 自愈(self-healing)

知道 magento.softwaretestingboard.com 有一个名为“Sale”的菜单项，点击后会导航到新页面。完成以下测试，编写一个新的步骤来点击“Sale”菜单选项，但为该元素创建一个 **自愈定位器**

```javascript
test("The self-healing", async ({ page }) => {
  await page.goto("https://magento.softwaretestingboard.com/");
  await page.getByLabel("Consent", { exact: true }).click();
});
```

#### 答案

自愈定位器是当你将多个定位器指向同一个元素时，你使用帮助方法或 OR 操作符将它们链接在一起。使用 [or 操作符](https://playwright.dev/docs/api/class-locator?#locator-or) 可以提供多个定位器指向同一个元素，如果由于应用程序更改其中一个失效，它可以尝试使用另一个

[**查看代码**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#content-below-is-visible-to-members-only)

**来自乙醇的解释 👀：作者的示例代码是要会员才能访问的，不过没关系，我从官网找了个一样的例子，可以得到同样的效果，出于对原创的尊重，我把作者的原始链接也放在这里**

![Matching one of the two alternative locators](https://playwright.dev/docs/locators#matching-one-of-the-two-alternative-locators)

```javascript
const newEmail = page.getByRole("button", { name: "New" });
const dialog = page.getByText("Confirm security settings");

await expect(newEmail.or(dialog).first()).toBeVisible();

if (await dialog.isVisible())
  await page.getByRole("button", { name: "Dismiss" }).click();

await newEmail.click();
```

---

## 5\. 已关闭的浏览器

这段代码会做什么：

```javascript
test("The closed browser", async ({ page }) => {
  await page.goto("https://blog.martioli.com/");
  await page.getByRole("link", { name: "About" }).click();
  expect(page).toHaveURL(/about/);
});
```

可能的答案：

- 测试会失败，因为 About 是一个按钮，而不是链接
- 测试会报错，关于目标页面
- 测试会失败，因为传递给 .toHaveURL() 的参数

#### 答案

测试会报错，关于目标页面。错误：`expect.toHaveURL: 目标页面、上下文或浏览器已关闭`

[**查看解释**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#content-below-is-visible-to-members-only)

**乙醇的解释 👀：上面的示例也是要开会员的，我来给个省流的版本**

这是因为 `toHaveURL` 是一个异步操作，需要等待（`await`）其完成。因此，正确的代码应如下：

```javascript
test("The closed browser", async ({ page }) => {
  await page.goto("https://blog.martioli.com/");
  await page.getByRole("link", { name: "About" }).click();
  await expect(page).toHaveURL(/about/); // 这里添加了 await
});
```

---

## 6\. 引用

知道在第二步中点击的元素是页面上的一个反向链接，这段代码会做什么：

```javascript
test("The reference", async ({ page }) => {
  await page.goto("https://blog.martioli.com/playwright-tips-and-tricks-1/");
  await page
    .locator("section")
    .locator("p")
    .locator("a")
    .getByText("buy me a coffee")
    .click();
  await expect(page).toHaveURL(/blog.martioli.com/);
});
```

可能的答案：

- 测试会失败，因为“buy me a coffee”是一个链接，我们已经离开了 martioli.com
- 测试会通过
- 测试会失败，因为你不能混合使用 locator().locator().locator()

#### 答案

测试会通过，因为点击一个 [反向链接](https://backlinko.com/hub/seo/backlinks?ref=blog.martioli.com) 会生成一个包含我们初始来源（blog.martioli.com）reference 的 URL

[**查看解释**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#content-below-is-visible-to-members-only)

**乙醇的解释 👀：我不懂，反正我没在真实的项目中遇到过这种情况**

---

## 7\. 其他语言环境

修改以下测试并使其在不同的语言环境下运行，例如德语。

```javascript
test("The locale", async ({ page }) => {
  await page.goto("https://www.google.com/");
});
```

#### 答案

你可以在用例里直接修改。 [文档](https://playwright.dev/docs/emulation#locale--timezone)。只需在测试前添加 `test.use({locale: 'de-DE'})`

---

## 8\. CSS 属性

给定以下代码，如何提高其可读性和简洁性。

```javascript
test("The css properties", async ({ page }) => {
  await page.goto("https://magento.softwaretestingboard.com/");
  await page.getByLabel("Consent", { exact: true }).click();

  const element = page.getByText("Shop New Yoga");
  const backgroundColor = await element.evaluate((el) => {
    return window.getComputedStyle(el).getPropertyValue("background-color");
  });
  expect(backgroundColor).toBe("rgb(25, 121, 195)");
});
```

#### 答案

当你已经有内置方法 [toHaveCSS()](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-have-css) 时，不需要调用 evaluate。记住 `toHaveCSS()` 具有自动重试功能，这在你等待某些元素属性延迟出现时至关重要。

[**查看代码**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#content-below-is-visible-to-members-only)

**乙醇的解释 👀，参考[这篇文章](/blog/what-the-hex-or-how-i-check-colors-with-playwright/)**

```javascript
await page
  .getByText("Shop New Yoga")
  .toHaveCSS("background-color", "rgb(25, 121, 195)");
```

---

## 9\. 长按点击

给定以下代码，如何修改点击步骤来模拟按住左键 3 秒然后松开鼠标键。

```javascript
test("The long click", async ({ page }) => {
  await page.goto("https://www.clickspeedtester.com/mouse-test/");
  await page.getByRole("link", { name: "Second Clicker" }).click();
});
```

#### 答案

Click 可以选择性地接受一个带有 [delay](https://playwright.dev/docs/api/class-mouse?ref=blog.martioli.com#mouse-click) 属性的对象，值以毫秒为单位。像这样：`.click({delay: 3000})` 配合一个元素，它将在该元素上按住 3 秒钟，然后释放鼠标键

---

## 10\. 强制点击

页面上有一个数据同意弹出框，你必须同意才能继续。搜索按钮隐藏在这个弹出框后面。给定以下代码。会发生什么？

```javascript
test("The force", async ({ page }) => {
  await page.goto("https://www.google.com/");

  // 搜索输入字段
  await page.locator("textarea").first().fill("martioli");
  // 搜索按钮
  await page
    .locator('[type=submit][name="btnK"]')
    .last()
    .click({ force: true });
});
```

可能的答案：

- 测试会通过。我使用了 `{force:true}` ，它会点击按钮，结果会显示在弹出框后面
- 测试会通过，但没有结果显示在弹出框后面
- 测试会失败，超时，因为无法点击隐藏在弹出框后的按钮

#### 答案

测试会通过，但没有结果显示在弹出框后面。`force:true` 在元素被另一个元素覆盖时不会点击，但也不会报错（playwright 中的一个 bug？）。这与 `fill()` 不同。如果你检查输入字段，它在输入时没有问题。

---

## 11\. Base URL

我在配置文件中设置了 baseUrl。这段代码会做什么：

```javascript
test("The baseurl", async ({ page }) => {
  await page.goto("");
});
```

可能的答案：

- 测试会失败。我忘记了引号之间的 `/`
- 测试会失败，因为 `.goto()` 需要双引号
- 测试会通过

#### 答案

测试会通过，空字符串与 "/" 效果相同。它会导航到在 playwright.config.js 中配置的 baseUrl

---

## 12\. workders

给定以下关于 workers 的配置。如果我运行一个包含 100 个测试的套件，它们会如何运行：

```javascript
module.exports = defineConfig({
  testDir: "./tests",
  workers: "5%",

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
```

可能的答案：

- 测试会运行得非常慢，因为只有 5% 的 workers 工作量
- 测试会在你拥有的 CPU 核心数的 5% 上运行
- 测试不会开始，因为你不能以百分比设置 workers 数量

#### 答案

测试会在你拥有的 CPU 核心数的 5% 上运行。例如，如果你有 4 个核心，100% 就是 4 个，每个核心占 25%。在我们的例子中，5% 小于 25%，所以你只会得到一个 [worker](https://playwright.dev/docs/api/class-testconfig#test-config-workers)

---

如果你觉得这有用，请点击赞同按钮。或者如果你想进一步激励我，可以 [请我喝杯咖啡](https://ko-fi.com/adrianmaciuc?ref=blog.martioli.com)。

我的博客有一个 **会员** 部分。免费加入，没有垃圾邮件，你可以访问仅限会员的内容。 [现在成为会员](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/#/portal/signup/free) ，你还将是第一个在我发布新文章时收到电子邮件的人。

## 来源

URL 来源: https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/

发布时间: 2024-05-05
