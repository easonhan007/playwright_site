+++
date = 2024-07-08
title = "为什么我从 Cypress 转向了 Playwright "
description = "playwright比cypress其实更加现代一些"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我从 2019 年开始使用 [Cypress](https://www.cypress.io/),当时我所在的公司决定在新项目中放弃 [Protractor](https://www.protractortest.org/)。那时我使用的框架是 [Angular](https://angular.io/),我有机会实施 Cypress 概念验证。最近,我换了工作,现在使用 [React](https://react.dev/),在那里我也有机会实施 [Playwright](https://playwright.dev/) 概念验证。

在 Angular 和 React 方面都有经验后,我偏好使用 `data-testid` 属性进行测试。这让我能够保持一致的 UI 端到端测试方法,我没有观察到 Angular 和 React 应用程序测试之间有任何显著差异。

注意:本文中我使用 React 应用作为 Cypress 和 Playwright 的示例。

<div class="w-full md:w-1/2 mx-auto">
  <img src="https://miro.medium.com/v2/resize:fit:600/0*8FsR8lzrCfAf8W2J.jpg"/>
</div>

## 这两个测试框架提供了什么?

Cypress 和 Playwright 都提供了出色的 UI 测试体验(您也可以测试 API)。它们的自动等待功能使开发人员能够轻松编写测试,它们提供了 UI 来可视化运行的测试,还可以生成测试的屏幕截图和视频,并支持 TypeScript。

这两个框架还支持可视化组件测试,但我不会在本文中涉及这个主题。

由于这两个框架提供了非常相似的功能,我将分析它们如何实现以下方面,以及它们如何影响开发人员的体验/生产力:

- 用于编写测试的语法在学习曲线和每个框架的整体易用性方面起着关键作用。包括但不限于使用自定义命令扩展框架和录制用例。
- 测试执行和可维护性是影响开发人员对测试信心和花费在调试上的时间的重要因素,特别是在速度和稳定性方面。
- 测试报告在测试过程中起着关键作用,评估它们的设置 ease 和提供的信息级别对两个框架都很重要。

## 我的 Cypress 经验

安装 Cypress 很简单,基本上就是一个 NPM 依赖项,然后就可以开始了。然而,不久之后就遇到了需要了解的 Cypress 复杂细节,才能使用它。以下是一些主要的问题:

- **用于编写测试的语法:** Cypress 使用类似 promise 的语法来编写测试。这一开始可能看起来并不令人困惑,但开发人员往往认为因为他们的 API 看起来像 promise,所以它的行为就像 promise(async/await)。悲哀的现实是它不是这样的,这导致开发人员花费大量时间学习如何使用 Cypress API 并使其适合他们特定的测试场景。  
  如果您需要使用 async/await,您有两个选择:要么将其包装在 Cypress 命令中以便将其添加到 _Cypress 命令链_ 中,要么使用像 [cypress-promise](https://www.npmjs.com/package/cypress-promise) 这样的库。以下是每个选项的示例:

```typescript
// async-await.spec.ts
import promisify from "cypress-promise";

function sleep(milliseconds: number) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function asyncFunction(text: string) {
  console.log("started asyncFunction " + text);
  await sleep(3000);
  console.log("finalized asyncFunction " + text);
}

context("Async/Await Test", () => {
  beforeEach(() => {
    cy.visit("/");
  });

  it("convert promises into cypress commands, do not write tests using async/await", () => {
    cy.wrap(null).then(() => asyncFunction("first"));
    cy.wrap(null).then(() => asyncFunction("second"));
  });

  it("convert cypress commands to promises, should be able to code with async/await", async () => {
    const foo = await promisify(cy.wrap("foo"));
    const bar = await promisify(cy.wrap("bar"));
    expect(foo).to.equal("foo");
    expect(bar).to.equal("bar");
  });
});
```

- **测试报告:** Cypress 缺乏内置的测试报告功能,这意味着获得所有测试的综合摘要、它们的持续时间以及失败的额外元素(如屏幕截图和链接视频)可能是一个具有挑战性和繁琐的过程。尽管在配置报告方面投入了相当大的努力,但仍可能存在生成的报告中缺少屏幕截图的情况。

![图片 3](https://miro.medium.com/v2/resize:fit:700/1*QgXR5prXZLNJ8HBm3tLfqg.png)

```json
 // package.json: 繁琐的测试报告设置示例
  "scripts": {
    "-------------------- E2E Commands --------------------": "",
    "cypress:open": "nyc cypress open",
    "cypress:run": "npm-run-all -s --continue-on-error _clean _cypress-run:run _cypress-run:html",
    "-------------------- Supporting Commands --------------------": "",
    "_clean": "npx rimraf coverage cypress/output/junit cypress/output/mocha-json cypress/output/mocha-html/*.html cypress/output/mocha-html/*.json .nyc_output",
    "_coverage-report": "npx nyc report --reporter html",
    "_cypress-run:run": "nyc cypress run --headless --browser chrome",
    "_cypress-run:html:merge-json": "mochawesome-merge cypress/output/mocha-json/*.json > cypress/output/mocha-html/merged-mochawesome.json",
    "_cypress-run:html:gen-html-from-json": "marge cypress/output/mocha-html/merged-mochawesome.json -f cypress -o cypress/output/mocha-html -i true --charts true",
    "_cypress-run:html": "npm-run-all -s _cypress-run:html:merge-json _cypress-run:html:gen-html-from-json _coverage-report"
  },
```

- **如何运行有界面测试:** Cypress 在其自己的浏览器应用程序内运行您的 web 应用程序。它首先打开一个列出所有 `specs` 的页面,然后您可以单击一个 spec 来运行该 spec 内的所有测试。我可能会补充说,所有这些都相当慢。此外,如果您只想运行 `spec` 中的一个测试,您需要将其标记为 `only`,保存,然后只有该测试会自动重新加载。

![图片 4: 在 Cypress 浏览器中运行的应用程序。](https://miro.medium.com/v2/resize:fit:700/1*DA01oS_nrO9ZdiSIb37IRw.png)

- **如何在无界面运行中访问浏览器控制台日志:** 浏览器控制台日志仅在以有界面形式运行测试时可见(打开 DevTools)。这意味着如果您的测试在本地成功运行但在 CI 流水线上失败,那么您将花费很长时间试图将这些日志带到流水线控制台。幸运的是,有一个插件可以简化这个过程,但由于 Cypress 插件的工作方式,它不仅仅是即插即用的工作。

![图片 5](https://miro.medium.com/v2/resize:fit:700/1*pBBISRJOKqAbxp0kxmQlXg.png)

只有在打开 DevTools 时才能看到浏览器控制台日志。

```typescript
// cypress/plugins/index.ts
interface Browsers {
  family: string;
  name: string;
}

interface LaunchOptions {
  args: string[];
}

const cypressPLugins = (on: unknown, config: unknown) => {
  require("@cypress/code-coverage/task")(on, config);
  // 将 console.* 消息记录到 cypress 控制台,
  // 当 CI/CD 流水线上出现错误时会有帮助
  require("cypress-log-to-output").install(on, consoleToLogConfig);
  require("@cypress/react/plugins/react-scripts")(on, config);
  // @ts-ignore
  on(
    "before:browser:launch",
    (browser: Browsers, launchOptions: LaunchOptions) => {
      if (browser.family === "chrome" || browser.name === "chrome") {
        console.log("Adding chrome config...");
        launchOptions.args.push("--disable-dev-shm-usage");
        launchOptions.args.push("--lang=en");
      }
      return launchOptions;
    }
  );
  return config;
};

export const consoleToLogConfig = (
  _type: unknown,
  event: { level: string; type: string }
) => {
  // 从此插件返回 true 或 false 以控制事件是否记录在 cypress 控制台上
  // `type` 是 `console` 或 `browser`
  // 如果 `type` 是 `browser`, `event` 是 `LogEntry` 类型的对象:
  //  https://chromedevtools.github.io/devtools-protocol/tot/Log/#type-LogEntry
  // 如果 `type` 是 `console`, `event` 是传递给 `Runtime.consoleAPICalled` 的对象类型:
  //  https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#event-consoleAPICalled

  // 只显示错误事件:
  return event.level === "error" || event.type === "error";
};

export default cypressPLugins;
```

- **调试测试:** Cypress 有几种不同的调试选项,网上有很多关于这个主题的文章。主要的要点是,由于 Cypress 命令异步运行,您不能简单地添加一个 `debugger` 命令。  
  本质上,Cypress 为您提供了两个有用的命令: `debug()` 和 `pause()`。第一个将 `debugger` 命令添加到 Cypress 运行器中,而后者则在该点停止测试运行。两者都允许您检查 DOM,但只有使用 `pause()` 才能逐步执行测试中即将到来的每个 Cypress 命令。  
  鉴于 Cypress 使用类似 promise 的链式 API,您可以将这两个命令中的任何一个与任何 Cypress 命令链接起来:

```typescript
cy.get([data-testid="username-input"]).type("my-username").pause();
```

![图片 6](https://miro.medium.com/v2/resize:fit:700/1*Z1gGMf2DP-xhqNg8YIQDkA.png)

- **测试并行化:** Cypress 不支持在本地并行运行测试。有很多库可以帮助您实现并行化,但这并非易事。在我之前的公司,我们试图并行化我们的测试以改善流水线运行时间,但努力结果如此巨大,以至于我们降低了它的优先级。  
  副作用是,开发人员很少在本地运行完整的 Cypress 测试套件,他们只是等待流水线的反馈。
- **速度:** Cypress 在无界面和有界面浏览器格式下运行时都很慢。这是我们想要并行化测试的主要原因。即使在本地运行测试也非常慢。在开发测试时,当您修改文件时,测试会自动重新加载,即使在我的 MacBook Pro 上,这也可能需要几秒钟。
- **测试稳定性:** Cypress 以在 CI/CD 流水线上不稳定而闻名,这导致开发人员花费大量时间追踪幽灵。我见过开发人员实施的常见 _黑客解决方案_ 是在测试中添加 `cy.wait(<ms>)`,并在 CI/CD 流水线中添加重试。
- **自定义命令:** 如果您在测试中经常使用常见功能,您很可能想要为其创建一个自定义 Cypress 命令。不幸的是,添加这样的命令既不直观也不类型安全(除非您额外努力):

```typescript
// cypress/support/commands.ts
Cypress.Commands.add("getByTestId", (selector: string, ...args: unknown[]) => {
  return cy.get(`[data-testid=${selector}]`, ...args);
});

// cypress/typings/cypress.d.ts
declare namespace Cypress {
  interface Chainable {
    getByTestId(selector: string, ...args: unknown[]): Chainable;
  }
}

// 您现在可以在测试中使用此命令:
it("should type username in username input", () => {
  cy.getByTestId("username-input").type("my-username");
});
```

- **录制用例:** Cypress 现在提供了 _Cypress Studio_,这是一个我个人还没有尝试过的实验性功能。

## 我的 Playwright 经验

我从 2023 年初开始使用 React,当时我的团队还没有任何 UI 测试。因此,我决定考虑引入 Cypress。然而,我们也开始引入 web 组件,并计划使用 [Storybook](https://storybook.js.org/) 来记录和测试我们的 web 组件。由于 Storybook 在底层使用 Playwright,我调查了 Playwright 能提供什么。最初的吸引力是:我的团队只需要学习一个框架就可以测试 web 组件和我们的 UI。

安装 Playwright 非常简单:不到一小时我就完成了全面的测试。

- **用于编写测试的语法:** 编写 Playwright 测试就像编写普通的 TypeScript 代码一样简单,没有特殊的 API 需要学习。最好的部分是您可以编写普通的 async/await 代码,因此您可以使用所有正常的 TypeScript 支持函数。示例:

```typescript
import { test } from "@playwright/test";

test.describe("Playwright test with async/await", () => {
  function sleep(milliseconds: number) {
    return new Promise((resolve) => setTimeout(resolve, milliseconds));
  }

  async function asyncFunction(text: string) {
    console.log("started asyncFunction " + text);
    await sleep(3000);
    console.log("finalized asyncFunction " + text);
  }

  test("should open storybook and click around", async ({ page }) => {
    await page.goto("http://localhost:6006/");
    await page
      .getByRole("link", {
        name: "Storybook 7.1.1 is available! Your current version is: 7.0.2 Dismiss notification",
      })
      .click();
    await page.getByRole("link", { name: "Storybook" }).click();
    await page.locator("#internal-components-overview--docs").click();
  });

  test("should test the async methods used in previous example", async ({
    page,
  }) => {
    await asyncFunction("first");
    await asyncFunction("second");
  });
});
```

- **测试报告:** 这是一个如此令人愉快的惊喜:我不需要做任何事情!Playwright 生成的开箱即用报告非常棒。您还可以非常轻松地在多个浏览器上运行测试(只需更改配置,Playwright 将为您安装所需的浏览器)。  
  我将其配置为仅包含失败测试的跟踪信息、屏幕截图和视频;否则,就像 Cypress 一样,测试运行会很慢。在下面的示例中,我们的第一个测试失败了。如果我们点击它,我们会得到以下信息:导致失败的异常、测试的哪些步骤失败了、测试的视频以及测试的完整跟踪。

![图片 7](https://miro.medium.com/v2/resize:fit:700/1*i7YqewHSh9Pu93jRBCioew.png)

Playwright HTML 报告概览

![图片 8](https://miro.medium.com/v2/resize:fit:700/1*VVDm5lT4OEQbhKZ0HCoscA.png)

失败测试 Playwright 报告摘要

![图片 9](https://miro.medium.com/v2/resize:fit:700/1*WOa3ZZLGfQGUR7GTfRxPLw.png)

Playwright 测试跟踪

- **如何运行有界面测试:** Playwright 由 Microsoft 开发,所以他们当然为 [VS Code](https://code.visualstudio.com/) 提供了一个插件。我自己是 IntelliJ 用户,但当我想运行 Playwright 测试时,我发现自己会切换到 VS Code。

与 Cypress 不同,您不必启动任何东西就可以运行一个或多个测试。只需在 VS Code 中打开您的代码,然后点击常用的单元测试绿色三角形,或者如果您之前已经运行过测试,则点击绿色勾号/红色 X。您还可以选择是否要打开浏览器或跟踪查看器。  
这里的开发人员体验非常棒。测试打开速度快,反应灵敏。

![图片 10](https://miro.medium.com/v2/resize:fit:1000/1*TNZ7F8L-5g02deAoA09xGg.png)

- **如何在无界面的浏览器运行中访问浏览器控制台日志:** 与 Cypress 一样,Playwright 不会在运行 Playwright 的控制台中显示浏览器日志。为了实现这一点,您可以扩展 Playwright `Page` 对象以将浏览器日志转发到控制台日志(还有其他方法可以做到这一点,例如扩展 `test` 对象本身)。

```typescript
// utils/console.util.ts
export const configureLogForwarding = (page: Page) => {
  page.on('console', (msg) => {
    if (process.env.PLAYWRIGHT_LOG_TO_CONSOLE === 'true') {
      switch (msg.type()) {
        case 'info':
        case 'log': {
          // eslint-disable-next-line no-console
          console.log(`Log: "${msg.text()}"`);
          break;
        }
        case 'warning': {
          // eslint-disable-next-line no-console
          console.log(`Warning: "${msg.text()}"`);
          break;
        }
        case 'assert':
        case 'error': {
          // eslint-disable-next-line no-console
          console.log(`Error: "${msg.text()}"`);
          break;
        }
      }
    }
  });
};

// tests/demo-tests.spec.ts
test.describe('Playwright test with async/await', () => {
  test.beforeEach(async ({ page }) => {
    configureLogForwarding(page);
    hostAppNavigationPo = new HostAppNavigationPo(page);
    genericAssetModalPo = new GenericAssetModalPo(page);
  });
// ...
```

- **调试测试:** 这是我最喜欢的功能之一。要调试测试,设置一个断点,然后右键单击绿色三角形/绿色勾号/红色 X,然后单击 _调试测试_。浏览器将打开,运行将在您的断点处停止。从这里开始,它就是开发人员习惯的正常调试会话。

![图片 11](https://miro.medium.com/v2/resize:fit:700/1*YpMNIAHnhHhMDNG7JWX1zA.png)

在 Playwright 中开始调试会话

![图片 12](https://miro.medium.com/v2/resize:fit:700/1*018sTeChOw29tDN9uGVuJg.png)

Playwright 正在进行的调试会话

- **测试并行化:** Playwright 支持开箱即用的并行化(当然,您的被测系统必须能够支持并行运行测试)。考虑到我们的 CI/CD 工具没有太多资源,因此速度较慢,我们在流水线中关闭了并行测试。然而,当我在编码时,我能够在本地非常快速地运行所有测试。诚然,我们只使用了 Playwright 大约 5 个月,所以我们只有约 80 个测试。这里有一些非科学的数字:约 80 个测试,在 CI/CD 中 5 分钟(1 个工作进程),在本地 2 分钟(1 个工作进程),在本地 55 秒(5 个工作进程)。

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  /* 其他配置... */
  /* 在 CI 上选择退出并行测试。 */
  workers: process.env.CI ? 1 : undefined,
  /* 并行运行 spec 文件中的测试 */
  fullyParallel: true,
});
```

- **速度:** 当以无界面形式运行等效测试时(就像在 CI/CD 流水线中那样),Playwright 比 Cypress 快约 1.5 倍。  
  此外,Playwright 能够在不到一秒的时间内在浏览器上启动测试(在我的 MacBook Pro 上)。这意味着我可以随时运行任何测试,在任何规范中,而无需启动 _Playwright 服务器_ 等。与 Cypress 不同,对于 Cypress,您首先必须启动 Cypress UI,然后在该 UI 中导航到要运行的测试。  
  这为开发人员提供了绝佳的体验!
- **测试稳定性:** 我们已经编写测试 5 个月了,我们还没有遇到任何不稳定的情况,也不需要在测试中使用任何等待或睡眠。由于我不再在之前使用 Cypress 的公司工作,很难确定将那些不稳定的测试迁移到 Playwright 是否会使它们稳定下来。
- **自定义命令:** Playwright 提供了一种[扩展基础](https://playwright.dev/docs/api/class-test#test-extend) `[test](https://playwright.dev/docs/api/class-test#test-extend)` 的方法,这样您就可以在测试期间轻松访问自定义命令和/或页面对象。这种模式简单易懂,直观且类型安全。Playwright 的示例:

```typescript
// my-test.ts
import { test as base } from "@playwright/test";
import { TodoPage } from "./todo-page";

export type Options = { defaultItem: string };

// 通过提供 "defaultItem" 选项和 "todoPage" fixture 来扩展基本测试。
export const test = base.extend<Options & { todoPage: TodoPage }>({
  // 定义一个选项并提供默认值。
  // 我们稍后可以在配置中覆盖它。
  defaultItem: ["Do stuff", { option: true }],

  // 定义一个 fixture。请注意,它可以使用内置 fixture "page"
  // 和一个新选项 "defaultItem"。
  todoPage: async ({ page, defaultItem }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await todoPage.addToDo(defaultItem);
    await use(todoPage);
    await todoPage.removeAll();
  },
});

// example.spec.ts
import { test } from "./my-test";

test("test 1", async ({ todoPage }) => {
  await todoPage.addToDo("my todo");
  // ...
});
```

- **录制用例:** Playwright 提供了使用他们的 VS Code 插件记录 UI 测试的选项。您只需按下 `Record new` 按钮,Playwright 就会为您打开一个浏览器。然后输入 web 应用程序的 URL 并开始点击。Playwright 记录的最好部分是,如果存在 `data-testid` 选择器,它会选择该选择器 ( `await page.getByTestId('dialog-title');` )。

![图片 13](https://miro.medium.com/v2/resize:fit:700/1*clsfh46nro1biK36LZC0RQ.png)

Playwright 还有许多其他优势,我在本文中没有涵盖,主要是因为我没有大量使用这些方面,但这里有一些例子:

- **iFrames:** Playwright 开箱即用地与 iFrames 配合使用,体验非常流畅。我们在当前的工作中使用 iFrames,但在我之前的工作中没有使用(当时我在使用 Cypress)。然而,据我所知,您需要安装 Cypress 插件才能测试 iFrames。这篇[文章](https://www.cypress.io/blog/2020/02/12/working-with-iframes-in-cypress/)详细解释了为什么 Cypress 在处理 iFrames 时遇到困难以及如何测试它们。
- **Web 应用服务器:** Cypress 和 Playwright 都需要您的应用程序正在运行才能运行测试。对 Cypress 的一个常见请求是希望框架能够在运行测试之前启动被测系统。我个人在运行测试时总是让我的应用程序保持运行状态,无论是在本地还是在 CI/CD 流水线中。然而,开发人员的愿望已经被听到了(被 Playwright):

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  // 在开始测试之前运行您的本地开发服务器。
  webServer: {
    command: "npm run start",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

- **禁止** `only` **关键字:** 一个常见的用例是,当开发人员想要运行单个测试时,他们会将其标记为 `only`。不幸的是,他们经常忘记在提交之前删除它。Playwright 带有一个配置来检测这一点,而对于 Cypress,我们必须添加 eslint 规则。

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  /* 如果您在源代码中不小心留下了 test.only,在 CI 上使构建失败。 */
  forbidOnly: !!process.env.CI,
});

// example.spec.ts
test.describe('Playwright test with async/await', () => {

  test.only('should test the async methods used in previous example', async ({
    page,
  }) => {
    await asyncFunction1();
    await asyncFunction2();
  });

  // 更多测试...
```

- **多个页面:** Cypress 在其自己的 web 应用程序中运行您的 web 应用程序,这带来了 Cypress 一次只能在一个页面上运行测试的限制。而 Playwright 则可以在每个浏览器中打开多个 [BrowserContext](https://playwright.dev/docs/api/class-browsercontext) 和/或多个 `Page`,所有这些都可以有不同的网站/域等,并在它们之间运行测试。

- **多语言支持:** 在 Cypress 中,您可以选择使用 JavaScript 或 TypeScript 编写测试。然而,在 Playwright 中,编写测试的语言选项更加多样化。您可以选择使用 JavaScript、TypeScript、Java、Python 或 .NET 编写测试,为开发人员提供了更大的灵活性,可以选择他们喜欢的编程语言进行测试自动化。

## 结论

在多年成为 Cypress 的粉丝并强烈倡导 UI 测试之后,开始使用一个我不确定是否会像 Cypress 那样好，使用的新框架并不是一个容易的决定。话虽如此,发现 Playwright 不仅可以做到 Cypress 所能做到的,而且在我能想到的所有方面都超越了它,这是一个如此令人愉快的惊喜。

最后,Cypress 和 Playwright 的开发者社区都相当庞大。尽管 Cypress 仍然更受欢迎,但随着更多开发者发现 Playwright 的开发体验有多棒,Playwright 社区正在快速增长。

我建议任何已经在使用 Cypress 或正在考虑进行 UI 测试的人都应该考虑 Playwright 作为一个值得的选择。

## 来源

[来源](https://medium.com/@oldiazg/why-i-switched-from-cypress-to-playwright-dc41ce4d5e1b)

发布时间: 2023-08-02
