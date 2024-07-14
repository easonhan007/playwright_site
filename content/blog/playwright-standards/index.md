+++
date = 2023-10-20
title = "playwright的各种规范"
description = "Houseful 的 Playwright 测试规范，值得学习"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Houseful 业务中的多个团队使用 Playwright 进行前端测试自动化。在构建我们的 Playwright 框架时,我们的目标是让代码易于阅读、维护和调试。为了帮助我们实现这一目标,我们作为一个团队共同努力,在使用 Playwright 的各个代码库中创建了统一的测试规范。

在各个代码库中统一测试标准为我们在可读性、可用性和准入门槛方面提供了好处。例如:

- 提高可重用性 - 函数 / 定位器 / 共享步骤 / 其他测试代码可以轻松重用。对于在测试中工作的人来说,找到他们需要的函数和元素很简单。这减少了重复,并降低了代码审查开始后需要重新修改的可能性。

- 简化 review - 代码可以更快地被 review。它减少了审查代码的心理负担,因为你可以轻松弄清楚测试代码在做什么。

- 加快入职 - 命名约定帮助新人快速入职并感到舒适地为代码库做贡献。

以下是我们在 Houseful 创建 Playwright 测试时遵循的测试规范和指南。

## Playwright 指南

### 端到端测试中的数据创建

运行端到端(e2e)测试成本很高。它们在资源方面成本高昂,可能需要大量精力来设置,并且对流程中任何地方的微小变化敏感,这可能使它们变得脆弱(容易报错)且难以长期维护。在选择这条路之前,请考虑其他选项。

如果你必须进行 e2e 测试:

好的做法 👍

- 每个测试都有自己的数据创建。即它创建完成检查所需的所有数据
- 每个测试都有一个后置步骤,即清理数据

不好的做法 ⚔️

- 依赖现有数据来执行测试
- 在测试后留下未清理的状态

### 页面对象模型 (POM)

每个页面都应该有一个相应的 [POM 文件](https://playwright.dev/docs/pom) 来帮助我们测试的可维护性和可扩展性。POM 文件应包含和给出 POM 相关的所有选择器和函数。

所有交互都应通过页面对象完成,即测试用例中不应包含选择器。

所有断言都应在你的测试中完成,即 POM 中不应包含断言。(**乙醇的评论:👀 这点见仁见智，很多时候 pom 中可能会出现一些保护性的等待断言，比如等待某个元素出现，如果不出现整个测试就失败了**)

你可以在我们关于 [软件测试设计模式](https://zoopla.blog/posts/2023/test-framework-migration/) 的博客中阅读更多关于我们如何利用 POM 的内容

好的做法 👍

```typescript
// POM 文件 './pom/foo'
// 添加与页面相关的所有定位器和函数。
// 允许所有测试重用

import { Locator, Page } from "@playwright/test";

export class FooPage {
  readonly page: Page;
  readonly pageTitle: Locator;
  readonly buttonFoo: Locator;

  constructor(page: Page) {
    this.page = page;
    this.pageTitle = page.locator("text=My Page");
    this.buttonFoo = page.locator("text=Foo");
  }
}

// tests/foo.spec.ts
// 调用 POM 以使用定位器和函数
// 执行测试所需的所有断言

import { FooPage } from "./pom/foo";

let fooPage: FooPage;

describe("显示 foo bar", () => {
  beforeEach(({ page }) => {
    fooPage = new FooPage(page);
  });

  test("bar 是可见的", async () => {
    await fooPage.buttonFoo.click();
    await expect(fooPage.titlePage).toBeVisible();
  });
});
```

不好的做法 ⚔️

```typescript
// tests/foo.spec.ts
// 直接在测试中包含定位器

import { Locator, Page } from "@playwright/test";

describe("显示 foo bar", () => {
  test("bar 是可见的", async () => {
    await page.locator("text=Foo").click();
    await expect(page.page.locator("text=My Page")).toBeVisible();
  });
});
```

### 测试结构 - Arrange, Act, Assert

在构建测试时遵循 AAA (Arrange, Act, Assert) 模式。在大多数情况下,Arrange 步骤可以包含在 Before 块中。

考虑添加注释以提高可读性。

好的做法 👍

```typescript
// 安排,创建一个 let 属性

await createProperty();

// 执行,提出一个收费

await raiseCharge();

// 断言,确认收费已提出

expect(charge).ToBe("raised");
```

### Linter

安装并使用 linting 规则。我们使用 [eslint-playwright-plugin](https://www.npmjs.com/package/eslint-plugin-playwright)

推荐的配置将有助于执行本博文中描述的一些指南。

```bash
npm install -D eslint-plugin-playwright
```

### 避免条件语句

避免在测试文件中使用条件逻辑。测试应该是确定性的,这意味着我们应该目标是拥有明确预期结果的测试。带有条件语句的测试可能难以维护和阅读。此外,除非你绝对确定应用程序的状态在进行断言时已经稳定,否则这类测试可能会不稳定。

有条件语句可能是一个测试用例做了太多事情的迹象,可以被拆分。

不好的做法 ⚔️

```typescript
import { FooPage } from "./pom/foo";

let fooPage: FooPage;

describe("条件测试", () => {
  beforeEach(({ page }) => {
    fooPage = new FooPage(page);
  });

  test("bar 是可见的", async () => {
    const isButtonVisible = await fooPage.buttonFoo.isVisible();

    if (isButtonVisible) {
      // 如果 buttonFoo 可见,点击它使 pageTitle 可见
      await fooPage.buttonFoo.click();
      // 然后检查 pageTitle 是否可见
      await expect(fooPage.pageTitle).toBeVisible();
    } else {
      // 否则只检查 pageTitle 是否可见
      await expect(fooPage.pageTitle).toBeVisible();
    }
  });
});
```

好的做法 👍

```typescript
// 为每个场景有单独的规范。
// 包含需要达到该状态的设置步骤

// fooPageVisible.spec.js

test("bar 最初是可见的", async () => {
  // 设置你的测试,使 bar 最初可见

  // 断言 bar 是可见的
  await expect(fooPage.pageTitle).toBeVisible();
});

// fooBarButton.spec.js

import { FooPage } from "./pom/foo";

let fooPage: FooPage;

test("点击 Foo 按钮后 bar 是可见的", async () => {
  // 设置你的测试,使按钮最初可见

  // 执行按钮操作
  await fooPage.buttonFoo.click();

  // 断言 bar 是可见的
  await expect(fooPage.pageTitle).toBeVisible();
});
```

### 等待

不要使用任何任意的等待。这可能导致不稳定的测试,因为你很少能确定等待时间是否足够。它还可能不必要地增加测试运行时间。相反,尝试:

- 使用 Playwright 的 [waitUntil: 'domcontentloaded'](https://playwright.dev/docs/api/class-page#page-event-dom-content-loaded)
- 等待特定的网络请求解析
- 等待页面状态稳定,例如元素在页面上可见/不可见

不好的做法 ⚔️

```typescript
await page.waitForTimeout(5000);
```

好的做法 👍

```typescript
// 在等待帮助文件中定义
// wait-helpers.ts

export const waitForAPIResponse = async (
  page: Page,
  url: string,
  statusCode: number
): Promise<void> => {
  await page.waitForResponse(
    (res) => res.url().includes(url) && res.status() === statusCode
  );
};

// 在你的测试文件中使用
//tests/foo.spec.ts

import { Locator, Page } from "@playwright/test";
import { waitForAPIResponse } from "../../helpers/wait-helpers";

describe("显示 foo bar", () => {
  test("bar 是可见的", async () => {
    await fooPage.buttonFoo.click();
    await waitForNewAPIResponse(this.page, "/Accounting/GetRaisedCharges", 200);
    await expect(fooPage.titlePage).toBeVisible();
  });
});
```

好的做法 👍

```typescript
//tests/foo.spec.ts

import { Locator, Page } from "@playwright/test";
import { waitForAPIResponse } from "../../helpers/wait-helpers";

describe("显示 foo bar", () => {
  test("bar 是可见的", async () => {
    await page.goto(fooBarURL, {
      waitUntil: "domcontentloaded",
    });
  });
});
```

好的做法 👍

```typescript
//tests/foo.spec.ts

import { Locator, Page } from "@playwright/test";
import { waitForAPIResponse } from "../../helpers/wait-helpers";

describe("导航到 foo bar", () => {
  test("页面已加载", async () => {
    await fooPage.buttonFoo.click();
    await expect(fooPage.titlePage).toBeVisible();
  });
});
```

### 选择器

避免使用与实现和页面结构绑定的选择器。

相反,我们根据 [testing-library 指导原则](https://testing-library.com/docs/queries/about/#priority) 优先考虑以下内容

- getByRole (这有助于可访问性,反映用户和辅助技术如何感知页面)
- getByText
- getByTestId (需要时添加)

不好的做法 ⚔️

```typescript
page.locator(".opt-u > div > .summary > div:nth-child(4) > div");
```

好的做法 👍

```typescript
page.locator("#foo-button");

page.getByText("OK");
```

### 标签

在 Playwright 中利用标签(tags)来对测试进行分组并进行有针对性的运行。标签测试的一些方法包括:

- 按测试类型 (例如 功能性、视觉,...)
- 按测试在流水线中运行的位置 (发布、回归,...)
- 按功能 (例如 日历、登录, …)

你可以在我们关于 [标签注释](https://zoopla.blog/posts/2022/playwright-tag-annotations/) 的博文中读到更多关于我们如何使用标签的内容。

好的做法 - 按测试类型 👍

```typescript
describe("显示 foo bar", () => {
  // 设置在每种测试类型之前运行的步骤
  beforeEach(async ({ page }) => {
    await page.goto("/foo/bar");
    fooPage.buttonFoo.click();
    await fooPage.titlePage.waitFor();
  });

  // 检查可访问性
  test("@accessibility", async ({ page }) => {
    await injectAxe(page);
    await checkA11y(page, undefined, a11yOpts);
  });

  // 对页面运行断言
  test("@functional @smoke", async ({ page }) => {
    await expect(fooPage.buttonFoo).toBeVisible();
    await expect(fooPage.titlePage).toBeVisible();
  });

  // 桌面的视觉快照
  test("@visual desktop", async ({ page, captureScreenshot }) => {
    await captureScreenshot("foo-desktop.png");
  });

  // 移动设备的视觉快照
  testMobile("@visual mobile", async ({ captureScreenshot }) => {
    await captureScreenshot("foo-mobile.png");
  });
});
```

**乙醇的注释：👆 上面在测试标题里打标签的方式已经过时了，现在 playwright 提供了一种新的做法，更加的工程化和可视化一些，具体看[这里](https://playwright.dev/docs/test-annotations#tag-tests)**

好的做法 - 按页面 / 功能 / 测试运行位置 👍

```typescript
//tests/foo.spec.ts

describe("@foobar @smoke 导航到 foo bar", () => {
  test("页面已加载", async () => {
    await fooPage.buttonFoo.click();
    await expect(fooPage.titlePage).toBeVisible();
  });
});
```

### 不稳定的测试

应优先解决不稳定的测试。如果你当时无法解决它,用 [.fixme](https://playwright.dev/docs/api/class-test#test-fixme-1) 标签它们。这将跳过该测试。

```typescript
//tests/foo.spec.ts

describe("显示 foo bar", () => {
  test.fixme("bar 是可见的", async () => {
    await fooPage.buttonFoo.click();
    await expect(fooPage.titlePage).toBeVisible();
  });
});
```

### 并行化和可重复性

构建测试以便在不干预的情况下重复运行。并与套件中的其他测试并行运行,即不干扰其他测试。

Playwright 通过启动同时运行的多个 [workders](https://playwright.dev/docs/test-parallel#worker-processes) 来实现开箱即用的并行测试。Playwright 可以根据可用资源扩展工作进程的数量。通过使用 [大型 github runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-larger-runners),我们可以在 CI 流水线中并行运行更多测试。

### 命名约定

#### 变量

使用 _**驼峰命名法**_ 声明。

#### 布尔值

以 'is', 'has', 'are', 'have' 开头。这有助于在浏览代码时识别这是一个布尔值。仍然使用 _**驼峰命名法**_ 声明。

```typescript
let isTurnedOn = false;
```

#### 页面对象 / 类

使用 _**帕斯卡命名法**_ 声明。

使用描述性命名,这可以帮助读者快速识别这是涵盖哪个页面或页面组件。根据需要使用你的产品中尽可能多的上下文来使名称有意义。

好的做法 👍

```typescript
export class AddWorksOrderModal
```

不好的做法 ⚔️

```typescript
export class newModal
```

#### 定位器

使用描述性命名,这可以帮助读者快速识别定位器所针对的元素。

例如,你可以使用包含 _**"动作 / 元素名称" + "元素类型"**_ 的命名结构。

_**定义元素类型**_ - 这些是你的基本 HTML 元素类型,它们将在设计系统中定义和命名,或者作为一个团队,你可以在元素的一致命名上达成一致。例如:checkbox, tickbox, button, tooltip

_**定义动作 / 名称**_ 考虑与此元素交互时将执行什么动作。或者元素的任何现有名称/文本

好的做法 👍

```typescript
//这个元素是一个保存按钮,位于属性的上下文中

readonly savePropertyButton: Locator;
```

好的做法 👍

```typescript
//这是一个报告日期的字段
readonly reportedDateField: Locator;
```

### 函数名

函数名总是以 _**"动词"**_ 开头,后跟函数正在交互的 _**"组件上下文"**_,即它对哪个实体产生影响。

好的做法 👍

```typescript
getWorksOrder();

printTransactions();

deleteProperty();
```

## 来源

[URL 来源](https://www.houseful.blog/posts/2023/playwright-standards/)
