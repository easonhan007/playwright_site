+++
date = 2024-03-13
title = "如何让playwright的测试用例运行的更加稳定"
description = "八字箴言：独立重试等待超时"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

**写在前面 by 乙醇 💡: 英文里有个专用名词叫做 flaky test，也就是易碎的测试用例的意思，中文直接翻译过来不太好听，我一般喜欢翻译成不稳定的测试用例，大家以后看到这个词大概知道是什么意思就好了**

Flaky test 是指在不同运行时产生不同结果的测试。有时它会通过，有时又会失败，原因不明。可以想象，导致这种行为背后一定有一些原因。这个问题在 UI 和 E2E 工具如 Playwright 上尤为明显。

Playwright 中的 flaky tests 是 CI 流水线的最大敌人之一，因为它们会导致看似随机的流水线任务失败。因此，一定要想办法避免不稳定的测试用例出现！

在本指南中，你将了解什么是 flaky test 及其主要原因。然后，你将探索一些避免在 Playwright 中出现 flaky tests 的最佳实践。

让我们开始吧！

## 什么是 Playwright 中的 Flaky Test(不稳定的测试用例)？

Flaky test 是指在同一个 [commit SHA](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits#about-commits) 上，测试结果不一致的测试。识别这种测试的另一个规则是“如果它在分支上通过，但在合并后失败，它可能是 flaky test。”在 Playwright 中，当一个测试第一次失败但重试之后通过时，这个测试就耀被标记为“flaky”。

Playwright 中的 flaky tests 在 CI 流水线中的影响尤为显著，因为它们的不一致性导致了同一次代码提交在不同尝试中出现不可预测的失败。为了确保成功部署，流水线需要在失败时多次运行。这会让 ci 的效率变低，并打击开发人员的信心，因为每次部署似乎都受到看似随机的测试不通过的影响。

## 测试为何会变得 Flaky 的原因

以下是导致测试变得 flaky 的一些重要原因：

- **竞争条件**：并发操作导致动态页面产生变化，然后就造成了意外的行为。
- **被测应用太慢**：如果被测应用程序运行在性能不好的机器上，测试中使用的超时可能会导致测试间歇性失败。
- **测试中的 bug**：测试脚本中的特定选择器，如不可靠的节点定位器，可能是测试不稳定的原因。

这些因素可以单独或共同导致测试变得 flaky。现在，让我们看看如何通过一些最佳实践来防止这些问题！

## 在 Playwright 中避免编写 Flaky Tests 的策略

在开始之前，请记住，你可以在 [Playwright 的 GitHub 仓库](https://github.com/microsoft/playwright.git) 中找到一些 Playwright 示例测试来练习。Clone 仓库，安装 Playwright，并使用以下命令启动测试：

```bash
git clone https://github.com/microsoft/playwright.git
cd playwright/examples/todomvc/
npm install && npx playwright install
npx playwright test
```

现在，我们去官方文档里看一下官方推荐的避免 flaky tests 的最佳策略。

### 在提交之前运行和调试测试

避免 Playwright flaky tests 的最简单和直观的方法是尝试预防它们。这个想法是在本地彻底检查所有测试，然后再提交。这样，你可以确保它们在不同情况下都是健壮的并且按预期工作。

由于 flaky test 比较鬼魅，不是每次都会报错，你应该尝试多次运行每个测试，并在与生产服务器类似资源的机器上进行测试。在本地测试中更改环境会产生与 CI/CD 流水线结果不一致的结果。

在正确设置环境和配置 Playwright 后，你可以使用以下命令在本地运行所有测试：

```bash
npx playwright test
```

一旦测试运行完毕，如果有些测试失败，[Plawright HTML 报告](https://playwright.dev/docs/test-reporters#html-reporter) 将自动打开，你也可以使用以下命令手动打开报告：

```bash
npx playwright show-report
```

生成的 HTML 文件将显示所测试执行的完整报告。详细来说，它允许你通过 flaky tests 过滤结果：

![Image 1](blob:https://semaphoreci.com/f5cac92d0c758d8aba7147f0dca557df)

请记住，当一个测试第一次失败但在另一尝试中通过时，它会被标记为“faulty”。换句话说，如果你想在本地检测 flaky tests，你需要配置 Playwright 在失败时自动重试（retry）测试。

在识别出 flaky test 后，你可以使用 [Playwright 提供的许多调试工具](https://playwright.dev/docs/debug) 中的任意工具进行调试。例如，假设检测到的 flaky test 定义在 `landing-page.spec.ts` 文件第 15 行的 [`test()`](https://playwright.dev/docs/api/class-test) 函数中。用下面的命令进行调试：

```
npx playwright test landing-page.spec.ts:15 --debug
```

另外强烈推荐使用 [UI 模式](https://playwright.dev/docs/test-ui-mode) 进行调试，因为它提供了一种时间旅行体验，使你能够直观地检查和浏览测试执行的所有操作：

![Image 2: Debugging tools for Playwright](blob:https://semaphoreci.com/f76b32e76d6f5786a90be088d7c98470)

### 使用 Locators 而非 Selectors

编写健壮的 E2E(ui 自动化) 测试用例的关键点之一是为 HTML 节点编写稳定的定位策略。虽然你可能熟悉 XPath 和 CSS 选择器，但在测试中它们并不是最佳解决方案。问题在于使用 JavaScript 的现代页面里，很多 DOM 是动态的，这种静态选择器可能导致测试不稳定。

这就是为什么 Playwright 推荐使用 [locators](https://playwright.dev/docs/locators)，它们更接近用户对页面的感知。你应该 [定位自定义的 testID](https://playwright.dev/docs/locators#locate-by-test-id) 或使用 [Role Locator](https://playwright.dev/docs/locators#locate-by-role)，而不是编写 CSS 选择器。Locators 代表一种在任何时刻进行查找页面元素的方法，它们是 Playwright 自动等待和重试能力的核心。

以下是你应该使用的推荐内置定位器函数：

- [`page.getByRole()`](https://playwright.dev/docs/locators#locate-by-role)：按显式和隐式可访问性属性定位元素。
- [`page.getByText()`](https://playwright.dev/docs/locators#locate-by-text)：按文本内容定位节点。
- [`page.getByLabel()`](https://playwright.dev/docs/locators#locate-by-label)：通过关联标签的文本定位表单控件。
- [`page.getByPlaceholder()`](https://playwright.dev/docs/locators#locate-by-placeholder)：按占位符定位输入。
- [`page.getByAltText()`](https://playwright.dev/docs/locators#locate-by-alt-text)：通过其 `alt` 文本替代项定位元素，通常是图像。
- [`page.getByTitle()`](https://playwright.dev/docs/locators#locate-by-title)：通过其 `title` 属性定位元素。
- [`page.getByTestId()`](https://playwright.dev/docs/locators#locate-by-test-id)：基于其 `data-testid` 属性定位元素。

现在，考虑以下 CSS 选择器：

```javascript
.btn-primary.submit
```

这很容易理解，但它显然没有以下表达式健壮和具有表现力：

```javascript
page.getByRole("button", { name: "Submit" });
```

虽然 HTML 元素在 DOM 中的 `class` 属性可以动态更改，但其在页面上的文本和 role 不太可能轻易更改。

如果你绝对必须使用 CSS 或 XPath，请尽量编写一致且通用的选择器。XPath 和 CSS 选择器很容易与页面的 dom 结构绑在一起，这就非常恶心了，因为当页面结构发生一点点改变时测试就会不通过。记住，一长串的 CSS 或 XPath 选择器是不好的，这会导致测试变得 flaky 且难以维护。

### 永远不要依赖硬等待

在测试中，硬等待是指在测试逻辑中添加固定时间延迟。其想法是暂停测试执行一段时间，以等待特定操作完成。虽然这是一种直接的等待方法，但它是导致 flaky tests 的主要原因之一。

例如这个例子:

```javascript
const { test, expect } = require('@playwright/test');

test('"Load More" button loads new products', async ({ page }) => {
  // 导航到要测试的页面
  await page.goto('https://localhost:3000/products');

  // 选择“Load More”按钮
  const loadMoreButton = await page.getByRole('button', { name: 'Load More' });

  // 点击“Load More”按钮
  await loadMoreButton.click();

  // 暂停测试执行 10 秒等待
  // 新产品加载到页面上
  await page.waitForTimeout(10000);

  // 计算页面上的产品元素数量
  const productNodes = await page.locator('.product').count();

  // 验证页面上有

10 个新产品
  expect(productNodes).toBe(10);
});
```

用例假设页面上的产品将会在 10 秒内加载完毕。如果页面的性能低于预期，这种硬等待时间将导致测试失败。同样，如果应用程序在预期时间之前就加载完成了，10 秒的延迟将使测试变得更慢且效率低下。

Playwright 通过其 [`page.waitFor()`](https://playwright.dev/docs/api/class-page#page-wait-for) 方法提供了更好的替代方案。这个方法允许你明确的等待元素满足特定条件：

```javascript
const { test, expect } = require("@playwright/test");

test('"Load More" button loads new products', async ({ page }) => {
  // 导航到要测试的页面
  await page.goto("https://localhost:3000/products");

  // 选择“Load More”按钮
  const loadMoreButton = await page.getByRole("button", { name: "Load More" });

  // 点击“Load More”按钮
  await loadMoreButton.click();

  // 等待 10 个产品元素出现在页面上
  // 来自乙醇的注释⚡️ waitForSelector方法已经不推荐使用了，请使用locator.waitFor()来替代
  await page.waitForSelector(".product:nth-of-type(10)");

  // 计算页面上的产品元素数量
  const productNodes = await page.locator(".product").count();

  // 验证页面上有 10 个新产品
  expect(productNodes).toBe(10);
});
```

`page.waitForSelector()` 方法会自动轮询 DOM，直到满足指定条件。这使得测试更具确定性并减少了硬等待带来的风险。

来自乙醇的注释：👆 上面的方法已经不推荐使用了，现在应该使用[locator.waitFor()](https://playwright.dev/docs/api/class-locator#locator-wait-for) 方法来替代。

### 利用 Playwright 内置重试

正如你在前一节中看到的，当测试失败时，Playwright 会标记它为 flaky。这会在生成报告中用黄色条目高亮显示 flaky tests。为了减少 CI/CD 流水线中的 flaky tests 干扰，你可以使用 Playwright 的 [`retries`](https://playwright.dev/docs/test-configuration#retries) 选项来设置测试的重试测试：

```javascript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  retries: 2, // 当测试失败时自动重试
  use: {
    baseURL: "https://localhost:3000",
  },
});
```

配置后，当一个测试失败时它将自动重试两次。在本地，你可以设置更高的重试次数来检测 flaky tests。

Playwright 的重试功能通过确保测试用例在因为

- 短暂的网络问题
- 或其他外部因素

运行失败后，最终还可以获得正确的结果，是一种建议掌握和设置的保底方式。

### 调整超时设置

为了更好地控制 Playwright 的行为，你可以配置各种超时设置。调整这些超时值可以帮助你避免由于应用程序响应时间慢或网络延迟而导致的 flaky tests。

- **测试超时**：通过 [testTimeout](https://playwright.dev/docs/test-configuration#test-timeout) 配置单个测试的超时时间。例如：

```javascript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  timeout: 60000, // 单个测试的超时时间为 60 秒
});
```

- **浏览器上下文**：配置 [`launch`](https://playwright.dev/docs/api/class-browser#browser-launch) 方法的 `timeout` 参数以控制启动浏览器的超时时间：

```javascript
const { chromium } = require("@playwright/test");

(async () => {
  const browser = await chromium.launch({
    headless: true,
    timeout: 30000, // 启动浏览器的超时时间为 30 秒
  });
})();
```

- **等待页面加载**：通过 [`page.goto()`](https://playwright.dev/docs/api/class-page#page-goto) 的 `timeout` 参数控制页面加载的超时时间：

```javascript
await page.goto("https://localhost:3000/products", {
  timeout: 45000, // 页面加载的超时时间为 45 秒
});
```

调整这些超时配置确保了 Playwright 在不同情景中能够满足你测试的实际情况，从而减少了由于超时问题导致的 flaky tests。

### 保持测试数据独立性

在 E2E 测试中，数据隔离是一个关键问题。共享状态会导致意外行为，尤其是在测试用例之间共享同一数据集时。为避免此问题，你应该确保每个测试都在干净和独立的状态下执行。

Playwright 提供了内置的 [Fixtures](https://playwright.dev/docs/test-fixtures) 支持，可以用于确保每个测试都有独立的测试数据。例如，你可以使用 Fixtures 来创建测试用户并在每个测试之后清除它们。

假设你有一个包含用户登录的测试集。你可以通过以下方式设置 Fixtures， 这样每个测试都会独立运行：

```javascript
import { test as base, expect } from "@playwright/test";

// 创建一个新的用户对象
const test = base.extend({
  user: async ({ page }, use) => {
    // 注册新的测试用户
    await page.goto("https://localhost:3000/register");
    await page.fill('input[name="username"]', "testuser");
    await page.fill('input[name="password"]', "password123");
    await page.click('button[type="submit"]');

    // 在测试中使用新用户
    await use({ username: "testuser", password: "password123" });

    // 清除测试用户
    await page.goto("https://localhost:3000/admin");
    await page.click(`button[aria-label="Delete testuser"]`);
  },
});

test("User can login", async ({ page, user }) => {
  await page.goto("https://localhost:3000/login");
  await page.fill('input[name="username"]', user.username);
  await page.fill('input[name="password"]', user.password);
  await page.click('button[type="submit"]');
  expect(page.url()).toBe("https://localhost:3000/dashboard");
});
```

通过确保测试数据的独立性，你可以避免由于共享状态导致的 flaky tests。

### 合理使用 BrowserContext

[`BrowserContext`](https://playwright.dev/docs/api/class-browsercontext) 是 Playwright 中的一个强大概念。它允许在单个浏览器实例中创建独立的浏览器会话。这意味着你可以并行运行多个测试而不会相互干扰。

通过为每个测试创建新的 `BrowserContext`，你可以确保测试的独立性。例如：

```javascript
const { test, chromium } = require("@playwright/test");

test("Run tests in isolated context", async () => {
  const browser = await chromium.launch();

  // 为第一个测试创建新的 BrowserContext
  const context1 = await browser.newContext();
  const page1 = await context1.newPage();
  await page1.goto("https://localhost:3000/products");
  // 执行第一个测试的操作...

  // 为第二个测试创建新的 BrowserContext
  const context2 = await browser.newContext();
  const page2 = await context2.newPage();
  await page2.goto("https://localhost:3000/login");
  // 执行第二个测试的操作...

  await browser.close();
});
```

通过使用 `BrowserContext`，你可以在单个浏览器实例中创建多个隔离的会话，从而减少 flaky tests 的发生。

## 小结

编写稳定的 E2E 测试是确保持续交付流水线高效和可靠的关键。虽然 Playwright 是一个强大的测试工具，但它也容易受到 flaky tests 的影响。然而，通过遵循本文中讨论的最佳实践，你可以显著减少 flaky tests 并得到更一致和可靠的测试结果。

总而言之，避免 flaky tests 的关键在于：

- 通过本地反复的检查和调试，多次运行测试用例来进行预防。
- 使用 Playwright 的内置重试策略和调整超时配置。
- 避免硬等待，使用 Playwright 的 `waitFor` 方法。
- 利用 Playwright 的定位器(locator)，而非静态选择器(css/xpath selector)。
- 保持测试数据的独立性。
- 合理使用 BrowserContext 创建独立的浏览器会话。

这些策略将帮助你编写更健壮和可靠的 E2E 测试，从而提高 CI/CD 流水线的效率和稳定性。

## 作者：Alexandra Zlate

Alexandra 是 Test Automation 的成员。她热衷于帮助团队提高测试自动化的成熟度并使用最佳实践。

## 来源

[URL Source](https://semaphoreci.com/blog/flaky-tests-playwright)

发布日期: 2024-03-13
