+++
date = 2024-05-09
title = "playwright中如何参数化项目配置"
description = "本文描述了如何为不同的项目设置不同测试数据的功能"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

引言

今天,我在公司的 Playwright 项目中遇到了一个有趣的挑战,我想记录下我的发现。

**任务是同时运行多个项目,每个项目使用不同的数据集。**

幸运的是,Playwright 提供了一个功能来解决这个需求 — 声明**TestOptions**的能力。

在本文中,我将指导您如何利用 Playwright 的 TestOptions 声明功能来高效地管理和同时执行多个项目。

> _在我的 GitHub 仓库上探索演示项目的代码片段:_[](https://github.com/nora-weisser/playwright_demo)_[github.com/nora-weisser/playwright_demo](https://github.com/nora-weisser/playwright_demo)_

## **步骤 1**: 安装项目

`npm init playwright@latest`

Playwright 将下载所有需要的浏览器并创建以下项目结构:

```bash
playwright.config.ts
package.json
package-lock.json
tests/
  example.spec.ts
test-examples/
  test.examples.ts
```

## **步骤 2**. 添加 Playwright 项目配置

打开 `playwright.config.ts` 文件。这个文件是 Playwright 配置的中心,允许您设置 Playwright 测试的首选浏览器等设置。在配置中,找到 'use' 部分并设置基础 URL。在这个演示中,我选择了 '[https://www.saucedemo.com/](https://www.saucedemo.com/)' 作为演示用的基础 URL。

```javascript
use: {
    /* 在像 `await page.goto('/')` 这样的操作中使用的基础 URL。 */
    baseURL: 'https://www.saucedemo.com/',
    /* 在重试失败的测试时收集跟踪。查看 https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
 },
```

## **步骤 3**. 了解 Playwright 项目

在文件的下方,您会遇到各种项目。我在下面引用了 Playwright 文档中的定义供您参考:

> 项目是使用相同配置运行的测试的逻辑组。我们使用项目来在不同的浏览器和设备上运行测试。项目在 playwright.config.ts 文件中配置,配置完成后,您可以在所有项目上运行测试,或仅在特定项目上运行。您还可以使用项目在不同的配置下运行相同的测试。例如,您可以在登录和未登录状态下运行相同的测试。

## **步骤 4**. 概述特定测试场景

**测试用例**: 实现登录测试用例并使用各种数据集执行它

参数化功能在这里起着关键作用,它允许配置每个项目用不同的用户名/密码进行测试。

## **步骤 5**. 考虑测试数据

测试数据长这个样子 👇

![图片 1](https://miro.medium.com/v2/resize:fit:1400/1*2RzF1FFuHfqIEiAmNRNJ7Q.png)

## **步骤 6**. 创建测试数据

建立一个 'test_data' 文件夹,并在其中创建 'login.data.ts'。首先声明一个包含必要属性(用户名和密码)及其数据类型的接口。

```javascript
export interface USER_DATA {
  username: string;
  password: string;
}
```

引入变量 USERS 并列出所有的测试数据。

```javascript
export const USERS: { [type: string]: USER_DATA } = {
  standard_user: {
    username: "standard_user",
    password: "secret_sauce",
  },
  locked_out_user: {
    username: "locked_out_user",
    password: "secret_sauce",
  },
  problem_user: {
    username: "problem_user",
    password: "secret_sauce",
  },
  performance_glitch_user: {
    username: "performance_glitch_user",
    password: "secret_sauce",
  },
  error_user: {
    username: "error_user",
    password: "secret_sauce",
  },
  visual_user: {
    username: "visual_user",
    password: "secret_sauce",
  },
};
```

## **步骤 7**. 扩展 TestOptions

为了将 'user' 参数整合到测试用例和项目中,必须声明 TestOptions 'targetUser'。创建一个 'helper' 文件夹,并在其中建立 'test-option.ts'。

通过引入新的 TestOptions 'targetUser' 来扩展现有的 'TestOptions',以帮助用户参数的集成。

```javascript
import { test as base } from "@playwright/test";
import { USER_DATA } from "../test_data/login.data";
import { USERS } from "../test_data/login.data";

export interface TestOptions {
  targetUser: USER_DATA;
}
export const test =
  base.extend <
  TestOptions >
  {
    targetUser: [USERS["standard_user"], { option: true }],
  };
```

## **步骤 8**. 在测试用例中使用 TestOptions

```javascript
import { expect } from "@playwright/test";
import { test } from "../helpers/test-options";

test("使用现有用户名和有效密码登录", async ({ page, targetUser }) => {
  await page.goto("/");
  //await page.goto('https://www.saucedemo.com/');
  await page.locator('[data-test="username"]').click();
  await page.locator('[data-test="username"]').fill(targetUser["username"]);
  await page.locator('[data-test="password"]').click();
  await page.locator('[data-test="password"]').fill(targetUser["password"]);
  await page.locator('[data-test="login-button"]').click();
  const currentURL = page.url();
  expect(currentURL).toBe("https://www.saucedemo.com/inventory.html");
  await expect(page.locator("#header_container")).toContainText("Swag Labs");
});
```

重要提示: 使用以下路径 '../helpers/test-options' 从我们创建的辅助函数中导入 'test' 函数。

## **步骤 9.** 更新项目配置

```javascript
import { defineConfig, devices } from '@playwright/test';
import type { TestOptions } from './helpers/test-options';
import { USERS } from './test_data/login.data';

export default defineConfig<TestOptions>({
projects: [
    {
      name: 'standard_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['standard_user'] },
    },
    {
      name: 'locked_out_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['locked_out_user'] },
    },
    {
      name: 'problem_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['problem_user'] },
    },
    {
      name: 'performance_glitch_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['performance_glitch_user'] },
    },
    {
      name: 'error_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['error_user'] },
    },
    {
      name: 'visual_user',
      use: { ...devices['Desktop Chrome'], targetUser: USERS['visual_user'] },
    },
}
```

## **步骤 10**. 执行所有项目并查看报告

运行命令: `npx playwright test`

默认情况下,Playwright 生成包含测试执行信息、单个测试成功或失败以及测试运行期间遇到的任何错误的测试报告。reporter 的目的是提供测试结果的可见性,使开发人员或测试人员更容易理解自动化测试的结果。

![图片 2](https://miro.medium.com/v2/resize:fit:1400/1*FKtwbhYN6xoz_QcxbcVHIw.png)

Playwright 报告视图 👆

在这个特定的实例中,列出了执行的测试用例以及已处理的用户信息。我故意包含了一个失败的测试用例 'locked-out-user',以展示登录失败的场景。

![图片 3](https://miro.medium.com/v2/resize:fit:1400/1*eIUhJD0Ysc6hofVN8wL2FA.png)

失败测试用例的附加信息 👆

## **步骤 11**. 执行特定项目

使用以下命令: `npx playwright test -project=<项目名称>`。此命令针对指定项目的预定义数据集执行登录测试用例。

## 结论

在本文中,我分享了关于 Playwright 项目中参数化的发现,涵盖了从创建测试数据到更新配置和实现 TestOptions 的各个方面。通过利用这个功能,我们可以提高用例的可维护性,扩大测试覆盖范围,并提高定位问题的效率。

**资源**:

1.  _测试参数化_: [https://playwright.dev/docs/test-parameterize](https://playwright.dev/docs/test-parameterize)
2.  _固定装置_: [https://playwright.dev/docs/test-fixtures](https://playwright.dev/docs/test-fixtures)
3.  _演示项目仓库_: [https://github.com/nora-weisser/playwright_demo](https://github.com/nora-weisser/playwright_demo)
