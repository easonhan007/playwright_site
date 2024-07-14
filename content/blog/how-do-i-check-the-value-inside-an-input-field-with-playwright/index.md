+++
date = 2023-05-22
title = "如何使用playwright检查输入框中的内容"
description = "用自带的toHaveValue()断言就可以了，但是hack的方式也是需要掌握的"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在使用 Playwright 进行页面测试时，有时我需要验证输入框中是否已经预先填充了文本，以确保我的系统正常运行。

在这种情况下，断言并不那么简单。典型的方法是找到页面上的元素，并查看.text 或.innerText 属性，_但问题是输入框通常不属于 DOM 的一部分_。

![图片1](https://playwrightsolutions.com/content/images/2023/05/image-5.png)

输入框文本不在 DOM 中

但幸运的是，Playwright 有办法处理这个问题！

在这个例子中，我将使用测试网站[https://ecommerce-playground.lambdatest.io/](https://ecommerce-playground.lambdatest.io/)。这个网站是一个虚拟商店，我们可以针对它编写自动化测试。我的测试场景如下：

- 使用搜索框搜索产品并点击搜索
- 验证我搜索的产品名称是否仍在搜索框中
- 点击进入产品详情页，验证产品名称是否仍在搜索框中
- 点击“加入购物车”，验证产品名称是否仍在搜索框中
- 点击结账，验证产品名称是否不再在搜索框中

最后一点是否应该如此功能目前我不质疑，但可以作为一个问题提出，这是系统当前的操作方式，因此有必要为其添加自动化检查。如果它发生变化，我们的自动化测试会通知我们。

## 使用.toHaveValue()断言方法

使用这个方法非常方便。这个方法可以在任何定位器上使用，被称为 LocatorAssertion。这些是一级公民，需要使用`await`与 expect 一起使用。下面的例子展示了如何使用这个功能。

```typescript
test("验证产品搜索输入框", async ({ page }) => {
  await page.goto("https://ecommerce-playground.lambdatest.io/");

  const productName = "Palm Treo Pro";
  const productSearch = page.getByRole("textbox", {
    name: "Search For Products",
  });
  const searchButton = page.getByRole("button", { name: "Search" });

  await productSearch.fill(productName);

  await test.step("搜索后验证输入框", async () => {
    await searchButton.click();
    await expect(productSearch).toHaveValue(productName);
  });
});
```

官方 Playwright 文档链接如下：

[toHaveValue()](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-have-value)

## 使用剪贴板进行断言

第二种方法是不使用 toHaveValue()，这在某些棘手的情况下会很有用。可以点击输入框，选择输入内容并将其复制到剪贴板。然后使用 JavaScript 获取剪贴板的内容，并进行断言。示例代码如下。

```typescript
import { test, expect } from "@playwright/test";

test("验证产品搜索输入框", async ({ page }) => {
  await page.goto("https://ecommerce-playground.lambdatest.io/");

  const productName = "Palm Treo Pro";
  const productSearch = page.getByRole("textbox", {
    name: "Search For Products",
  });
  const searchButton = page.getByRole("button", { name: "Search" });

  await productSearch.fill(productName);

  await test.step("搜索后验证输入框（替代方法）", async () => {
    await productSearch.click();
    let userAgentInfo = await page.evaluate(() => navigator.userAgent);
    if (userAgentInfo.includes("Mac OS")) {
      await page.keyboard.press("Meta+A");
      await page.keyboard.press("Meta+C");
    } else {
      await page.keyboard.press("Control+A");
      await page.keyboard.press("Control+C");
    }

    let clipboardText = await page.evaluate("navigator.clipboard.readText()");
    expect(clipboardText).toBe(productName);
  });
});
```

在这个例子中，我们首先评估浏览器的 userAgent，以确定需要按下的键盘修饰符，如果是 Mac OS 我们使用 Meta/Command 键，如果是 Windows 或 Linux 我们使用 Control 修饰键。我们首先点击 productSearch 定位器，使光标位于输入框中，然后按下选择和复制的快捷键。代码的下一步是获取 clipboardText。

⚠️ 你需要确保在你的 playwright.config.ts 中设置了以下内容：

```typescript
use: {
  permissions: ["clipboard-read"];
}
```

然后代码将 clipboardText 设置为剪贴板的文本，并进行断言以确保剪贴板中的文本与原始的 productName 变量匹配。

理想情况下你不需要这样做，但这是可行的 :) 完整的规范如下所示，注意我使用 test.steps 添加了不同的场景，这使得调试更加方便。

```typescript
import { test, expect } from "@playwright/test";

test("验证产品搜索输入框", async ({ page }) => {
  await page.goto("https://ecommerce-playground.lambdatest.io/");

  const productName = "Palm Treo Pro";
  const productSearch = page.getByRole("textbox", {
    name: "Search For Products",
  });
  const searchButton = page.getByRole("button", { name: "Search" });

  await productSearch.fill(productName);

  await test.step("搜索后验证输入框", async () => {
    await searchButton.click();
    await expect(productSearch).toHaveValue(productName);
  });

  await test.step("搜索后验证输入框（替代方法）", async () => {
    await productSearch.click();
    let userAgentInfo = await page.evaluate(() => navigator.userAgent);
    if (userAgentInfo.includes("Mac OS")) {
      await page.keyboard.press("Meta+A");
      await page.keyboard.press("Meta+C");
    } else {
      await page.keyboard.press("Control+A");
      await page.keyboard.press("Control+C");
    }

    let clipboardText = await page.evaluate("navigator.clipboard.readText()");
    expect(clipboardText).toBe(productName);
  });

  await test.step("导航到产品页面后验证输入框", async () => {
    await page.getByRole("link", { name: productName }).nth(1).click();
    await expect(productSearch).toHaveValue(productName);
  });

  await test.step("加入购物车后验证输入框", async () => {
    await page.getByRole("button", { name: "Add to Cart" }).click();
    await expect(productSearch).toHaveValue(productName);
  });

  await test.step("访问结账页面后验证输入框", async () => {
    await page.getByRole("link", { name: "Checkout " }).click();
    await expect(productSearch).not.toHaveValue(productName);
  });
});
```

完整的代码添加可以在[这里](https://github.com/BMayhew/playwright-demo/pull/21)找到。

## 引用

[来源网址](https://playwrightsolutions.com/how-do-i-check-the-value-inside-an-input-field-with-playwright/)

发布时间：2023-05-22
