+++
date = 2024-05-17
title = "你会喜欢的 Playwright 面试问题"
description = "还是细节"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

适用于中高级 QA 自动化工程师的 Playwright 面试问题

继我之前关于 Playwright 面试问题的[文章](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-hate/)之后，这里有 9 个**Playwright 棘手问题**。

## 1\. 显式等待

从测试搜索功能的角度来看，你会如何改进下面的代码：

```javascript
test("The explicit waits", async ({ page }) => {
  await page.goto("https://blog.martioli.com/playwright-tips-and-tricks-2/");
  await page
    .getByText("Playwright tips and tricks #2")
    .scrollIntoViewIfNeeded();
  await expect(page.getByText("Playwright tips and tricks #2")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Search this site" })
  ).toBeVisible();
  await page.getByRole("button", { name: "Search this site" }).click();
  await expect(
    page
      .frameLocator('iframe[title="portal-popup"]')
      .getByPlaceholder("Search posts, tags and authors")
  ).toBeVisible();
  await page
    .frameLocator('iframe[title="portal-popup"]')
    .getByPlaceholder("Search posts, tags and authors")
    .fill("Cypress");
  await expect(
    page
      .frameLocator('iframe[title="portal-popup"]')
      .getByRole("heading", { name: "Cypress" })
      .first()
  ).toContainText("Cypress");
});
```

#### 回答

- 移除所有 `toBeVisible()` 断言
- 移除 `scrollIntoViewIfNeeded()`
- 将 iframe 存储在常量中以便重用和提高可读性
- 在定位器中使用正则表达式，以便使用部分文本，例如 `/Search posts/` 而不是 `Search posts, tags and authors`

**查看代码和解释请见页面末尾** [**链接...**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-love/#content-below-is-visible-to-members-only)

**乙醇的解释 👀: 还是给个省流版本吧，我没看作者的解释，我按照自己的理解来编的 😳**

- 移除所有 `toBeVisible()` 断言: 因为这些断言没必要，如果你要操作 1 个元素的话，没必要断言这个元素`toBeVisible`，因为 playwright 会自动帮你做这件事情

- 移除 `scrollIntoViewIfNeeded()`: 理由同上

- 将 iframe 存储在常量中以便重用和提高可读性: 个人喜好问题，但是有道理

- 在定位器中使用正则表达式，以便使用部分文本，例如 `/Search posts/` 而不是 `Search posts, tags and authors`: 完全同意，尽量避免精准匹配的断言和定位器，当然了，playwright 默认情况下`getByXXX`中如果出现文本，都是模糊匹配的。

---

## 2\. 可见的方法

这段代码将会做什么：

```javascript
test("The visible methods", async ({ page }) => {
  await page.goto("https://blog.martioli.com/");
  await expect(page.getByRole("link", { name: "About" }).isVisible());
});
```

可能的答案：

- 测试将失败，因为 isVisible() 不是一个有效的方法
- 测试将失败，并显示关于属性 'then' 的错误
- 测试将通过

#### 回答

测试将失败，并显示错误：Error: expect: Property 'then' not found

**查看解释请见页面末尾** [**链接...**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-love/#content-below-is-visible-to-members-only)

**省流版本**

错误原因是 `isVisible()` 方法返回的是一个 `Promise` 对象，但 `expect` 断言方法不能直接处理 `Promise` 对象。需要使用 `await` 关键字来等待 `Promise` 对象的解析。

正确的代码应该是：

```javascript
test("The visible methods", async ({ page }) => {
  await page.goto("https://blog.martioli.com/");
  const isVisible = await page.getByRole("link", { name: "About" }).isVisible();
  await expect(isVisible).toBe(true);
});
```

这样修改后，`isVisible()` 方法的返回结果会在被 `expect` 断言方法处理之前被正确解析。

**乙醇的注释 👀：最好用 playwright 的 web 断言 await expect(locator).toBeVisible()**

## 3\. 忍者点击

以下代码将会发生什么：

```javascript
test("The ninja", async ({ page }) => {
  await page.goto("https://www.clickspeedtester.com/mouse-test/");
  await page
    .getByRole("link", { name: "Second Clicker" })
    .click({ trial: true });
  await page.waitForURL("**/clicks-per-second-test/");
});
```

可能的答案：

- 测试将失败，错误为 page.waitForURL: Test ended，因为点击操作未执行
- 测试将失败，因为 `waitForURL()` 参数格式无效
- 测试将在点击步骤失败，没有 `trial:true` 这样的选项

#### 回答

测试将失败，错误为 page.waitForURL: Test ended。使用 [trial:true](https://playwright.dev/docs/api/class-page?ref=blog.martioli.com#page-click-option-trial) Playwright 只执行[是否可以被点击的](https://playwright.dev/docs/actionability?ref=blog.martioli.com)检查，但跳过点击操作。

---

## 4\. 你还好吗？

以下代码将会发生什么：

```javascript
test("The you OK", async ({ page }) => {
  const response = await page.request.get("https://blog.martioli.com/");
  await expect(response).toBeOK();
});
```

可能的答案：

- 测试将失败，因为没有 `toBeOK()` 这个方法
- 测试将失败，因为 `page` 没有 `request`
- 测试将通过

#### 回答

测试将通过（前提是网站没挂的话）。[toBeOK()](https://playwright.dev/docs/api/class-apiresponseassertions?ref=blog.martioli.com#api-response-assertions-to-be-ok) 是一个确保响应状态码在 `200..299` 范围内的方法。

---

## 5\. 特殊词

假设元素包含文本"Be the first to discover new tips and tricks about automation in software development"，以下代码将会发生什么：

```javascript
test("The innerText?", async ({ page }) => {
  await page.goto("https://blog.martioli.com");
  const innertText = page.locator(".gh-subscribe-description").innerText();
  await expect(innertText).toContain("Be the first to discover new tips");
});
```

可能的答案：

- 测试将通过
- 测试将失败，错误为 Error: expect Received object: {}
- 测试将失败，因为我们不能在 `innerText()` 上使用 `toContain()`

#### 回答

测试将失败，错误为 Error: expect Received object: {}。因为我们忘记在 `innerText()` 方法前加上 `await` 关键字，以解析 Promise 并提取文本。

---

## 6\. 神奇的过滤器

过滤测试用例的最佳推荐方法是什么？

#### 回答

[tags](https://playwright.dev/docs/test-annotations?ref=blog.martioli.com#tag-tests)是过滤测试最简单和最有效的方法。

---

## 7\. 失败的一次

以下代码将会发生什么：

```javascript
test("The fail", async ({ page }) => {
  test.fail();
  await page.goto("https://www.martioli.com/");
  await expect(page.getByText("Astronaut")).toBeVisible();
});
```

可能的答案：

- 测试将通过，因为应用了 `test.fail()` 方法
- 测试将失败，因为应用了 `test.fail()` 方法
- 测试将执行所有步骤，但结果仍然失败

#### 回答

测试将通过，因为应用了 `test.fail()` 方法

为什么？因为它在我的[网站](https://martioli.com/?ref=blog.martioli.com)上找不到 "Astronaut" 这个词，因为找不到它，我们期望的测试整体失败，用例确实会失败，所以整体而言用例[将通过](https://playwright.dev/docs/api/class-test?ref=blog.martioli.com#test-fail)。

---

## 8\. 健康检查

以下代码将会发生什么？你如何改进代码：

```javascript
const locales = ["de", "com", "es"];

for (const location of locales) {
  test(`check health: ${location}`, async ({ page }) => {
    const response = await page.request.get(`https://www.google.${location}/`);
    expect(response).toBeOK();
  });
}
```

可能的答案：

- 测试将通过
- 测试将失败，因为不能进行这样的 `for` 循环
- 测试将失败，因为 `expect` 没有 `await` 关键字

#### 回答

测试将通过。你可以在 Playwright 中进行这样的检查，只需注意在测试中加入一些延迟。

**如果你想知道为什么 `expect` 不需要 `await` 关键字，请见页面末尾的解释** [**链接...**](https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-love/#content-below-is-visible-to-members-only)

**省流版本: 在 Playwright 中，expect 断言方法不需要 await 关键字的原因是 Playwright 的 expect 方法是同步的，不返回 Promise 对象。它会立即检查传入的值或对象的状态，并且如果检查失败，它会立即抛出一个错误**

---

## 9\. 页面一

以下代码将会发生什么：

```javascript
test("The page one", async ({ page }) => {
  await page.goto("https://blog.martioli.com/");
  await expect(getByText("Recommended Resources")).toBeVisible();
});
```

可能的答案：

- 测试将通过，因为我们有 `Recommended Resources`
- 测试将失败，因为引用错误
- 测试将失败，因为我的博客中没有 `Recommended Resources` 文本

#### 回答

测试将失败，错误为 ReferenceError: getByRole is not defined。注意我们用了 `expect(getByText` 而不是 `expect(page.getByText.`

---

如果你觉得这篇文章有用，请点击点赞按钮。或者[请我喝杯咖啡](https://ko-fi.com/adrianmaciuc?ref=blog.martioli.com)，以

更好地激励我。

## 来源

来源网址：https://blog.martioli.com/playwright-interview-questions-that-you-are-going-to-love/

发布时间：2024-05-17T07:08:35.000Z
