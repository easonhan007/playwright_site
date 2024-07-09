+++
date = 2024-07-09
title = "Playwright中如何使用fixture来监控前端的javascript错误"
description = "简单来说就是用fixture先监听pageerror事件，然后在用例中断言没有错误出现"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在今天充满 JavaScript 的世界中，ui 自动化测试和实时监控是非常具有挑战性的。现代应用程序中有大量的异步 JavaScript 代码运行，怎么样让测试稳定运行不挂掉一个真正的难题。

这就是为什么许多团队依赖于测试关键功能，并将“测试其余部分”视为一种可有可无的做法。这是一种典型的成本-效益决策。这种方法的缺点是，如果我们不对所有功能进行 ui 自动化测试，很容易忽略生产环境的问题和回归。

除了编写更多的测试之外，我们还能做些什么来解决测试覆盖率不足的问题呢？

一种有价值的方法是实施一个安全策略，让 ui 自动化测试监听显而易见的应用程序问题。让我们以 JavaScript 异常为例。

我们的关键功能用例全部测试通过并不意味着一切都如预期般工作。通过在 ui 自动化测试应用程序时监控 JavaScript 异常，增加捕获问题的机会，这样就不需要直接测试所有可用功能了。

在本文中，我将向我们展示如何设置 Playwright，并利用其 fixture 功能，以便在 JavaScript 控制台显示红色警报时使测试失败。

准备好了吗？

_如果我们更喜欢观看视频而不是阅读博文，请访问[YouTube 上的视频链接](https://www.youtube.com/watch?v=LKMwS_u_x8Y)。_

## 问题：前端的 js 代码会报错

让我们看一个例子：我一段时间前把 Checkly 博客上的延迟加载功能玩坏了。为了防止再次发生这种情况，我编写了一个在 Checkly 中运行的 Playwright ui 自动化测试。GitHub 操作使用 [npx checkly test](https://www.checklyhq.com/docs/cli/command-line-reference/#npx-checkly-test) 测试每个预览部署，并且如果一切顺利，我的测试用例将转化为生产监控，使用 [npx checkly deploy](https://www.checklyhq.com/docs/cli/command-line-reference/#npx-checkly-deploy)来运行并监控。

以下是完整的 Playwright 测试代码。

```typescript
import { expect, test } from "@playwright/test";

test("Checkly 博客延迟加载", async ({ page }) => {
  await page.goto("http://localhost:3000/blog/");
  // 定位所有博客文章
  const articles = page.locator('a[title="Visit this post"]');
  // 计算最初包含的文章数量
  const articleCount = await articles.count();

  // 将最后一篇文章滚动到视图中，以触发延迟加载
  await articles.last().scrollIntoViewIfNeeded();

  // 等待更多文章加载和渲染
  await expect(async () => {
    const newCount = await articles.count();
    expect(newCount).toBeGreaterThan(articleCount);
  }).toPass();
});
```

我原以为这种方法会安全，但事实并非如此（剧透：我错了）。

该测试导航到博客并测试了实现的延迟加载功能，但没有监控网站的其他问题。功能性的延迟加载是否意味着页面上的所有内容都正确工作？并非如此。

即使在向下滚动页面后页面上有更多的博客文章，也会忽略高度关键的用户问题，包括各种的 JavaScript 异常。该测试仅覆盖一个功能，忽略了其余部分。这并不理想！

![图片 1: 旁边的成功 Playwright 测试显示出现应用程序的情况。](https://images.prismic.io/checklyhq/4c0c430b-0b69-4ebb-9721-082baff0a8e8_javascript-exception-monitoring.jpg?auto=compress,format)

监听抛出的 JavaScript 异常是防止 UI 奔溃的一种保护措施。

如前所述，我们可能没有时间或能力对每个功能进行 ui 自动化，但是**我们的 ui 自动化测试应该至少关注显而易见的问题**。

那么，如何监听抛出的 JS 异常呢？

## 监听 Playwright 测试中的 JavaScript 异常

在 Playwright 中监听页面事件非常简单。page 对象带有一个方便的 `on` 函数，允许我们监听多种页面事件类型（`"load"`、`"pageerror"`、`"crash"` 等）。对于 JavaScript 异常跟踪，我们需要的是 `"pageerror"` 事件。

我们要考虑测试中抛出的异常，搞一个事件侦听器并将所有抛出的异常收集到一个数组中。一旦 ui 自动化测试功能通过，断言我们的错误数组不包含任何条目。如果有，我们的测试将失败。

```typescript
test("Checkly 博客延迟加载", async ({ page }) => {
  // 设置一个新的数组以收集抛出的错误
  const errors: Array<Error> = [];

  // 在测试会话期间监听异常
  page.on("pageerror", (error) => {
    errors.push(error);
  });

  // 所有我们的测试代码...
  // ...

  // 断言没有发生任何错误
  expect(errors).toHaveLength(0);
});
```

_请注意，在测试用例与页面交互之前必须初始化事件侦听器。理想情况下，我们的 `page.on` 代码应该首先出现在测试用例中。_

虽然上面的代码片段非常适合在单个测试用例中实现 js 的异常跟踪，但在大型测试项目中就不太好维护了。我们不希望在每个测试用例中重复相同的事件处理逻辑。

## 如果 JavaScript 抛出异常，让 ui 自动化测试自动失败

我们可以用 `beforeEach` 或 `beforeAll` 钩子在测试之前和之后运行代码，但是一个被低估的 Playwright 特性，这个特性值得更多关注！

[Playwright fixtures](https://playwright.dev/docs/test-fixtures) 允许我们以结构化方式组织代码。它们还允许我们在测试之前和之后运行代码，并且甚至可以提供配置修改和测试数据生成。对于许多其他用例，fixtures 非常有用。

### fixture 代码

在 Playwright 中创建 fixture 以捕获 JavaScript 异常并自动使测试失败。

```typescript
import { Page, test, expect } from "@playwright/test";

// 将其放在通用 fixture 部分
// https://playwright.dev/docs/test-fixtures#fixtures
const errors: Array<Error> = [];

// 在启动 Playwright 测试用例之前，注册事件侦听器
const errorListener = (page: Page) => {
  page.on("pageerror", (error) => {
    errors.push(error);
  });
};

// 使用 fixture 注册事件侦听器
// 使用 'errorListener' 定制的 'launchContext'
const customFixture = test.extend<{ page: Page }>({
  page: async ({}, use, testInfo) => {
    // 创建一个新页面实例
    const page = await browser.newPage();

    // 注册错误侦听器
    errorListener(page);

    // 使用该页面进行测试
    await use(page);

    // 关闭页面并终止浏览器实例
    await page.close();
  },
});

// 添加异常捕获到我们的 Playwright 测试
customFixture("Checkly 博客延迟加载", async ({ page }) => {
  await page.goto("http://localhost:3000/blog/");

  // 所有我们的测试代码...
  // ...

  // 断言没有发生任何错误
  expect(errors).toHaveLength(0);
});
```

### 项目级的 fixture 设置

接下来，我们应该为将来的扩展性和可维护性做好准备。将上述 fixture 提取到一个独立的文件中，并将其与其他 fixture 和自定义逻辑一起集成。

为了保持代码的整洁和有序，我们应该考虑把一个大型 fixture 放在自己的文件夹中，并在单独的模块中引用。这种方法允许我们添加额外的测试代码和检查脚本，而无需让代码库炸裂。

```typescript
// fixtures.ts
import { errors } from "./report";
import { Page } from "@playwright/test";

export const errorListener = (page: Page) => {
  page.on("pageerror", (error) => {
    errors.push(error);
  });
};

// custom-fixture.ts
import { customFixture } from "./fixtures";
import { errors } from "./report";

customFixture("Checkly 博客延迟加载", async ({ page }) => {
  await page.goto("http://localhost:3000/blog/");

  // 所有我们的测试代码...
  // ...

  // 断言没有发生任何错误
  expect(errors).toHaveLength(0);
});

// report.ts
export const errors: Array<Error> = [];
```

**结论 — 使用扩展的 Playwright 设置进行更多测试**

即使是简单的 Playwright ui 自动化测试，也可以通过添加一些基本的 JS 错误跟踪来提高其功能。通过了解如何设置和组织代码，我们可以确保未来的更改不会影响基础测试集的稳定性。

虽然这种方法不会取代更全面的测试战略，但它确实提供了一个低成本的方法来提高测试用例的可靠性。通过识别在测试中自动捕获的常见问题，我们可以通过捕获简单的 JS 错误和异常来提升 ui 自动化测试的价值。

所以，让我们回顾一下我们可以做些什么：在 Playwright 中使用 fixture 跟踪 JavaScript 异常，让我们的 ui 自动化测试更智能，更具鲁棒性。

```typescript
import { customFixture } from "./fixtures";
import { errors } from "./report";

customFixture("Checkly 博客延迟加载", async ({ page }) => {
  await page.goto("http://localhost:3000/blog/");

  // 所有我们的测试代码...
  // ...

  // 断言没有发生任何错误
  expect(errors).toHaveLength(0);
});
```

## 来源

**[阅读原文](https://www.checklyhq.com/blog/track-frontend-javascript-exceptions-with-playwright/)**
**发布时间：** 2023-11-20
