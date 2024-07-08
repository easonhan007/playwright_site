+++
date = 2024-07-08
title = "如何playwright去检查按钮或者控件是否被禁用"
description = "利用 toHaveAttribute() 方法在 Playwright 中进行断言，以检查按钮是否启用或禁用"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

简单来说很多情况下，我们需要在用例里判断某个按钮是否处于被禁用(灰掉)的状态。

在 UI 层进行测试时，您可能希望根据用户的操作验证按钮或元素是否处于特定状态。我经常遇到的一个常见场景是登录、填写地址信息或输入信用卡详细信息。您不希望在必填字段中没有值时，用户就有机会点击提交按钮，通常这些按钮会被禁用。

在这些情况下，我发现构建测试以验证某些按钮是否正确处于禁用（不可点击状态）是很有帮助的。

下面是一个通过 CodePen 的基本示例，我们将针对其编写自动化测试。

展示禁用按钮直到输入文本的 CodePen 示例。

对于断言，我们将使用 toHaveAttribute() 方法。

`expect({locator}).toHaveAttribute("{name}", "{value}")`

在我们的示例中，定位器将是我们要检查是否禁用的按钮，属性名称将是 "disabled"，值将是 "true"。根据您正在测试的站点中禁用属性的实现方式，可能禁用只是一个没有值的属性，如果是这种情况，值实际上是一个空字符串。

```typescript
// 如果 DOM 看起来像这样
<button class="button" disabled>Click Me</button>

expect({locator}).toHaveAttribute("disabled", "")

// 如果 DOM 看起来像这样
<button class="button" disabled="true">Click Me</button>

expect({locator}).toHaveAttribute("disabled", "true")
```

现在让我们看看完整的脚本。请注意，由于我们使用 CodePen，为了与生成的 HTML 元素交互，我们需要查看名为 "CodePen" 的 iFrame，所有元素都在这里。你还会注意到，在我的示例中，我为我们要交互的元素创建了变量，如果我们想创建多种场景，这些变量可以很容易地添加到页面对象中。

```typescript
import { test, expect } from "@playwright/test";

test("test", async ({ page }) => {
  await page.goto("https://codepen.io/bmayhew/pen/eYLdwVg");

  // 创建我们将要交互的元素的变量
  const codePenFrame = page.frameLocator('iframe[name="CodePen"]');
  const textInput = codePenFrame.getByPlaceholder("fill me");
  const button = codePenFrame.getByRole("button", { name: "Click Me" });
  const result = codePenFrame.locator("id=result");

  // Disabled 属性是活动的
  expect(button).toHaveAttribute("disabled", "true");

  await textInput.fill("Testing 1234");
  await page.keyboard.press("Tab");

  // Disabled 属性不再活动
  expect(button).not.toHaveAttribute("disabled", "true");

  await button.click();
  expect(result).toHaveText("You clicked the button");
});
```

以下是关于定位器断言的文档链接，因为还有许多其他方法可以验证 DOM 中的元素。

[LocatorAssertions](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-have-attribute)

## 来源

**来源链接**: [Utilizing the toHaveAttribute() method when making assertions in Playwright to check if a button is enabled or disabled](https://playwrightsolutions.com/utilizing-the-tohaveattribute-method-when-making-assertions-in-playwright-to-check-if-a-button-is-enabled-or-disabled/)

**发布时间**: 2023-02-27
