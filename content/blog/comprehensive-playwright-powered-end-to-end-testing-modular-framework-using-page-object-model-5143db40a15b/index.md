+++
date = 2024-03-12
title = "全面的基于 Playwright 的ui自动化测试，使用页面对象模型的模块化框架"
description = "本文描述的框架不仅工程化做的很好，而且没有用到第三方库，强烈推荐 👍"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## 关键特性

- **模块化设计**：通过为“操作”和“断言”创建单独的类，促进代码的重用性和可维护性。
- **数据生成**：支持使用工具函数和 API 调用生成测试数据。
- **页面对象模型**：用于维护页面元素定位器的通用类。
- **Fixture**：提供一致且高效的统一配置和钩子函数。

## 核心组件介绍

### 页面对象模型（POM）

页面对象模型是一种设计模式，鼓励更好的测试维护并减少代码重复。它将页面细节抽象为对象，使测试人员能够编写更具可读性和更强健的测试用例，尤其适用于 Web 应用程序测试。

### 页面对象（pages/）

页面对象代表被测试的 Web 应用程序的页面元素定位符。

### 操作（actions/）

我们为操作创建了单独的类，这些操作使用页面对象与 UI 进行交互。

### 断言（assertions/）

我们为断言创建了单独的类，这些断言在执行操作后验证应用程序的状态，确保应用程序表现如预期。

### 工具（utils/）

工具函数提供可在测试中重复使用的通用功能，例如生成随机图书数据。

![Image 3](https://miro.medium.com/v2/resize:fit:700/1*5qFbO9ZPFhouSWgPwAeE-Q.png)

### 测试用例（tests/e2e/）

测试用例定义 ui 自动化的测试场景，聚焦于应用程序的特定功能或特性。

**用例 1**：在此测试中，我们调用“generateRandomBookData”函数生成测试数据，并将其作为参数传递到测试中。

```javascript
import { test } from "../../fixtures/addBooks_fixture.js";
import generateRandomBookData from "../../utils/generateRandomBookData.js";

test.describe.serial("添加图书功能", () => {
  let title, isbn, genre, summary;

  test.beforeAll(() => {
    // 在所有测试之前生成一次图书数据
    const bookData = generateRandomBookData();
    ({ title, isbn, genre, summary } = bookData); // 解构并分配给局部变量
  });

  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000/books");
  });

  test("验证-> 新书添加", async ({ addBookActions, addBookAssertions }) => {
    // 在我们的测试中使用生成的图书数据
    await addBookAssertions.nodataValidationisPresent();
    await addBookActions.clickaddBook(title, genre, isbn, summary);
    await addBookAssertions.verifyBookInTable(title);
    await addBookAssertions.nodataValidationisNotPresent();
  });
});
```

**用例 2**：在此测试中，当我们无法在 UI 中生成数据，并且需要通过 API 调用获取测试数据时，可以在 before hooks 中调用 API。

```javascript
import { test } from "../../fixtures/updateBooks_fixture.js";
import generateRandomBookData from "../../utils/generateRandomBookData.js";
import { addBookViaAPI } from "../../requests/addBooks.js";

test.describe.serial("查看更多，编辑，删除功能", () => {
  test.beforeAll(() => {
    // 使用requests/addBooks.js文件生成图书数据
    addBookViaAPI(generateRandomBookData());
  });

  test.beforeEach(async ({ page }) => {
    await page.goto("http://localhost:3000/books");
  });

  test("验证-> 查看更多功能", async ({ page, updateBookActions }) => {
    await updateBookActions.clickviewMore();
  });

  test("验证-> 编辑功能", async ({
    page,
    updateBookActions,
    updateBookAssertions,
  }) => {
    await updateBookActions.clickeditBook();
    await updateBookAssertions.verifyUpdatedBookInTable("_editText");
  });

  test("验证-> 删除功能", async ({
    page,
    updateBookActions,
    updateBookAssertions,
  }) => {
    await updateBookActions.clickdeleteBook(); // 删除在此测试中添加的书籍
    await updateBookAssertions.verifyBookNotIntable("_editText");
    await updateBookActions.clickdeleteBook(); // 删除剩余的另一书籍
    await updateBookAssertions.nodataValidationisPresent();
  });
});
```

### 通过 Fixture 增强测试

Fixture 管理测试的配置和解变量的过程，初始化数据、配置测试环境或分配测试可能需要的资源。

### 使用 Fixture 的好处

- **一致性**：确保每个测试在相同条件下运行。
- **效率**：智能管理资源，加快测试过程。

### 实现 Fixture

我们的框架利用 Playwright 的 Fixture 来增强测试工作流，管理 BrowserContext、页面对象、操作和断言的自定义 Fixture。

```javascript
import { test as baseTest } from "@playwright/test";
import { AddBookActions } from "../pages/addBooks/addBooks_actions";
import { AddBooksAssertions } from "../pages/addBooks/addBooks_assertions";
import { AddBookPageObjects } from "../pages/addBooks/addBooks_pageObjects";

export const test = baseTest.extend({
  context: async ({ browser }, use) => {
    const context = await browser.newContext();
    await use(context);
  },

  page: async ({ context }, use) => {
    const page = await context.newPage();
    await use(page);
  },

  addBookActions: async ({ page }, use) => {
    await use(new AddBookActions(new AddBookPageObjects(page)));
  },

  addBookAssertions: async ({ page }, use) => {
    await use(new AddBooksAssertions(new AddBookPageObjects(page)));
  },
});

export default test;
```

```javascript
import { test as baseTest } from "@playwright/test";
import { UpdateBookActions } from "../pages/UpdateBooks/UpdateBooks_actions";
import { UpdateBooksAssertions } from "../pages/UpdateBooks/UpdateBooks_assertions";
import { UpdateBookPageObjects } from "../pages/UpdateBooks/UpdateBooks_pageObjects";

// 使用附加属性扩展基础测试Fixture以支持UpdateBookActions和UpdateBooksAssertions
export const test = baseTest.extend({
  context: async ({ browser }, use) => {
    const context = await browser.newContext();
    await use(context);
  },

  page: async ({ context }, use) => {
    const page = await context.newPage();
    await use(page);
  },

  updateBookActions: async ({ page }, use) => {
    await use(new UpdateBookActions(new UpdateBookPageObjects(page)));
  },

  updateBookAssertions: async ({ page }, use) => {
    await use(new UpdateBooksAssertions(new UpdateBookPageObjects(page)));
  },
});

export default test;
```

### 测试数据生成

项目使用定义在 utils/generateRandomBookData.js 中的工具函数生成随机图书数据。此函数利用 randomatic 包生成随机字符串和数字，然后将它们组合形成图书数据，包括“标题、类型、ISBN 和摘要”。以下是数据生成的简要概述：

- **标题**：一个以“Book ”为前缀，后跟 5 个字母和数字组成的字符串。
- **类型**：从预定义的类型列表中随机选择。
- **ISBN**：一个表示为字符串的随机 13 位数字。
- **摘要**：一个包含生成标题的简单字符串。

这些生成的数据用于测试中，以添加、更新或验证应用程序中的书籍，确保测试具有多样性的数据点。

## 来源

https://medium.com/@kbalaji.kks/comprehensive-playwright-powered-end-to-end-testing-modular-framework-using-page-object-model-5143db40a15b

发布时间: 2024-03-12
