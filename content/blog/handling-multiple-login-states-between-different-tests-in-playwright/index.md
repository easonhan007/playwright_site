+++
date = 2023-07-17
title = "在 Playwright 中处理不同测试间的多种登录状态"
description = "其实用多个用户就可以了"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

本周，我受到了与同事 [Joel](https://playwrightsolutions.com/author/joel/) 的对话以及在 [Discord 频道](https://discord.com/channels/807756831384403968/1128777494401663020/1128777494401663020) 中被提到的问题的启发，写下了如何在 Playwright 项目中处理不同登录状态的文章。

> 我按照 [https://playwright.dev/docs/auth](https://playwright.dev/docs/auth) 中的文档将“已登录”状态存储在 JSON 文件中。接下来的测试一切顺利，直到我测试注销功能的那一步。在注销测试场景之后，接下来的测试中用户的登录态没了!!。为什么会这样？请帮我理解并修复它。谢谢！

**注意**：有许多不同的方法可以解决这个问题，我将介绍我选择的解决方法，这取决于我正在测试的 web 应用程序。如果你有更简单或更健壮的方法来解决这个问题，请与我联系，我很想听听你的意见！

**注意 2**：我在下面测试用例中的断言是不太完美的。我在这里投入了最少的时间，以突出 `sessionStorage` 和测试设置。

## 探索我们将要测试的网站

但在开始之前，我们必须了解我们将要编写自动化测试的网站。我们将使用 [https://practicesoftwaretesting.com/](https://practicesoftwaretesting.com/) 作为我们的测试系统（有关该站点的更多详细信息，请参阅 [GitHub 项目页面](https://github.com/testsmith-io/practice-software-testing)。

在我的探索性测试过程中，我发现管理员 `auth-token` 在登录时生成，并且可以在同一浏览器的不同标签页中用于保持认证状态。如果我打开一个新的隐身窗口，会话不会激活，我没有登录，但我可以使用相同的用户名和密码创建第二个已认证会话。这两个会话可以同时存在。一旦我使用注销功能，我发现与之对应的 `auth-token` 现在失效了，而另一个 `auth-token` 仍然可以使用。这告诉我，当我要编写验证注销功能的测试时，直接依赖于当前登录用户的测试是行不通的。

这告诉我，我们正在测试的应用程序具有良好的安全性实践。当我们从系统注销时，`auth-token` 会失效。因此，当我们创建注销测试时，可能应该避免使用我们的默认 `auth-token`。

## 在 Playwright 中创建一个设置项目

我使用的提交代码的仓库可以在下面找到。

[使用 Playwright 测试 https://practicesoftwaretesting.com 示例 - GitHub](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com)

我们需要做的第一步是建立一个新的 `setup project`。在下面的配置文件中，我们有两个项目，第一个是 `setup`，它查找 `*.setup.ts` 文件并运行它们，第二个项目是 `ui-tests`，它依赖于 `setup` 项目成功运行才能继续。有关 defineConfig 的更多信息，请参阅 playwright 文档中的 [测试配置](https://playwright.dev/docs/test-configuration) 部分。

```javascript
// playwright.config.ts

import { defineConfig } from "@playwright/test";
import type { APIRequestOptions } from "./lib/fixtures/apiRequest";
import { TestOptions } from "./lib/pages";

require("dotenv").config();

export default (defineConfig < APIRequestOptions) &
  (TestOptions >
    {
      projects: [
        { name: "setup", testMatch: /.*\.setup\.ts/, fullyParallel: true },
        {
          name: "ui-tests",
          dependencies: ["setup"],
        },
      ],
      testDir: "./tests",
      fullyParallel: true,
      forbidOnly: !!process.env.CI,
      retries: process.env.CI ? 2 : 0,
      workers: process.env.CI ? 1 : undefined,
      reporter: [["html"], ["list"]],
      use: {
        testIdAttribute: "data-test",
        baseURL: process.env.UI_URL,
        apiURL: process.env.API_URL,
        apiBaseURL: process.env.API_URL,
        trace: "on",
      },
    });
```

## 添加我们的设置脚本

如你所见，`auth.setup.ts` 依赖于我在此文件（.env 和 LoginPage）下的一些代码块。因为这个设置文件被设置为一个项目，我们可以访问重命名为 `setup` 的测试块，以表明这些是初始化步骤而不是真正的测试。

`auth.setup.ts` 文件的前半部分为不同的电子邮件、密码和文件名设置变量。这些变量在每个设置块中使用。分解实际的 `setup` 步骤，包括：

- 创建一个 LoginPage 类，以便我们可以利用页面对象
- 访问登录页面
- 使用登录异步函数，传入指定的电子邮件和密码
- 验证用户已登录
- 将 `storageState` 保存到指定文件

在三个不同用户（管理员、customer01 和 customer02）的三个设置块中重复这些步骤。

另一个需要注意的是，我在 `playwright.config.ts` 中设置了 `fullyParallel: true`，这将在多个工作线程中运行时同时运行每个 setup 步骤。这将有助于加快 setup 步骤的速度。

```javascript
// tests/auth.setup.ts

// 通过设置测试将你的存储状态保存到 .auth 目录中的文件

import { LoginPage } from "@pages";
import { test as setup, expect } from "@playwright/test";

let adminEmail = process.env.ADMIN_USERNAME;
let adminPassword = process.env.ADMIN_PASSWORD;
const adminAuthFile = ".auth/admin.json";

let customer01Email = process.env.CUSTOMER_01_USERNAME;
let customer01Password = process.env.CUSTOMER_01_PASSWORD;
const customer01AuthFile = ".auth/customer01.json";

let customer02Email = process.env.CUSTOMER_02_USERNAME;
let customer02Password = process.env.CUSTOMER_02_PASSWORD;
const customer02AuthFile = ".auth/customer02.json";

setup("Create Admin Auth", async ({ page, context }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  await loginPage.login(adminEmail, adminPassword);
  expect(await loginPage.navAdminMenu.innerText()).toContain("John Doe");

  await context.storageState({ path: adminAuthFile });
});

setup("Create Customer 01 Auth", async ({ page, context }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  await loginPage.login(customer01Email, customer01Password);
  expect(await loginPage.navUserMenu.innerText()).toContain("Jane Doe");

  await context.storageState({ path: customer01AuthFile });
});

setup("Create Customer 02 Auth", async ({ page, context }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  await loginPage.login(customer02Email, customer02Password);
  expect(await loginPage.navUserMenu.innerText()).toContain("Jack Howe");

  await context.storageState({ path: customer02AuthFile });
});
```

首先要注意的是，我使用了 `dotenv` 包来管理存储在 `.env` 文件中的环境变量。

```javascript
// .env

# URLS
UI_URL=https://practicesoftwaretesting.com
API_URL=https://api.practicesoftwaretesting.com

# Logins
CUSTOMER_01_USERNAME=customer@practicesoftwaretesting.com
CUSTOMER_01_PASSWORD=welcome01
CUSTOMER_02_USERNAME=customer2@practicesoftwaretesting.com
CUSTOMER_02_PASSWORD=welcome01
ADMIN_USERNAME=admin@practicesoftwaretesting.com
ADMIN_PASSWORD=welcome01
```

我还使用了 `登录页面` 的页面对象。这是从我在 `tsconfig.json` 文件中设置的 `@pages` 路径导入的。我在任何指南中都没有涵盖这一点，但计划很快写一些文章说明一下，现在只需知道它是一个不错的快捷方式，我可以使用它，而无需在导入中使用完整路径。在页面文件中，我们有一些定位器和两个方法。一个用于访问登录页面，另一个用于登录，需要传入电子邮件和密码作为变量。

这样做可以简化我的测试和设置文件。

```javascript
// lib/pages/loginPage.ts

import { Page } from "@playwright/test";

export class LoginPage {
  readonly username = this.page.getByTestId("email");
  readonly password = this.page.getByTestId("password");
  readonly submit = this.page.getByTestId("login-submit");
  readonly navUserMenu = this.page.getByTestId("nav-user-menu");
  readonly navAdminMenu = this.page.getByTestId("nav-admin-menu");
  readonly navSignOut = this.page.getByTestId("nav-sign-out");
  readonly navSignIn = this.page.getByTestId("nav-sign-in");

  async goto() {
    await this.page

.goto(`${process.env.UI_URL}/sign-in`);
  }

  async login(email: string, password: string) {
    await this.username.fill(email);
    await this.password.fill(password);
    await this.submit.click();
    await this.page.waitForTimeout(1000); // 添加一个短暂的延迟以确保登录过程完成
  }

  async logout() {
    await this.navSignOut.click();
    await this.navSignIn.waitFor({ state: "visible" });
  }
}
```

从页面对象中，我们返回到 `auth.setup.ts` 文件。我们创建了三个用于认证的文件，这些文件会随着页面一起使用。

```javascript
// auth.setup.ts

setup("Create Admin Auth", async ({ page, context }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();

  await loginPage.login(adminEmail, adminPassword);
  expect(await loginPage.navAdminMenu.innerText()).toContain("John Doe");

  await context.storageState({ path: adminAuthFile });
});
```

一旦我们将 `setup` 设置为一个项目，我们就可以在 `ui-tests` 项目中使用这些存储的文件。我们可以在 `playwright.config.ts` 文件中将其作为存储状态的一部分提供给 `context` 对象。我们通过设置 `storageState` 为 `authFile` 路径中的 `storageState` 属性来实现。

```javascript
// playwright.config.ts

export default defineConfig({
  projects: [
    {
      name: "setup",
      testMatch: /.*\.setup\.ts/,
      fullyParallel: true,
    },
    {
      name: "ui-tests",
      dependencies: ["setup"],
      use: {
        storageState: ".auth/admin.json",
      },
    },
  ],
});
```

在此示例中，我们可以使用相同的方法为 `ui-tests` 项目提供任何 `authFile`。`authFile` 由实际测试使用，并且可以在存储状态下的 `use` 属性中设置。

## 创建我们的测试

以下是我们需要的一个简单示例，展示如何在项目中实现这一点。

```javascript
// tests/auth.spec.ts

import { test, expect } from "@playwright/test";

test("Verify that the authenticated user can log out", async ({ page }) => {
  // 通过使用存储状态文件，登录用户的状态会自动加载到页面中
  await page.goto("/");

  // 断言用户已登录
  await expect(page.getByTestId("nav-admin-menu")).toContainText("John Doe");

  // 调用登出方法
  const loginPage = new LoginPage(page);
  await loginPage.logout();

  // 断言用户已注销
  await expect(page.getByTestId("nav-sign-in")).toBeVisible();
});
```

在此示例中，我们导入 `test` 和 `expect` 来自 `@playwright/test`，并编写了一个简单的测试，展示了如何使用存储状态来验证用户是否已登录并能够注销。

## 总结

如你所见，我们有很多不同的方法可以用来在 Playwright 项目中处理不同的登录状态。通过创建一个 setup 项目，并在 `ui-tests` 项目中使用存储状态文件，我们能够有效地管理多个用户的登录状态。这样可以确保每个测试都在正确的登录状态下执行，并且在注销测试后，其他测试不会受到影响。

我们希望这篇文章对你有所帮助，并激发你在 Playwright 项目中处理类似问题的灵感。如果你有任何问题或建议，请随时与我们联系！

## 来源

URL 来源：https://playwrightsolutions.com/handling-multiple-login-states-between-different-tests-in-playwright/

发布时间：2023-07-17T12:30:51.000Z
