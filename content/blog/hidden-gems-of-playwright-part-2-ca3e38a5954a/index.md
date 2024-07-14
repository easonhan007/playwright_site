+++
date = 2024-05-23
title = "挖掘playwright的隐藏宝藏: 第 2 部分- Andrey Enin "
description = "断言重试和只运行失败的用例非常好用"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

[在上一篇文章](https://adequatica.medium.com/hidden-gems-of-playwright-68fcf8896bcb)中,我介绍了一些 Playwright 的实用方法,我把这些方法封装到了我的自动化测试框架里,大大简化了测试的过程。

本文将继续探讨这个强大工具的一些有趣特性:

- [为特定测试用例或者用例集重写全局配置]
- [设备模拟]
- [离线模式设置]
- [断言重试机制]
- [等待选择器(已弃用但仍可用) / 等待元素]
- [GitHub Actions 集成报告]
- [仅运行上次失败的测试]

这些特性的部分示例代码可以在这个[GitHub 仓库](https://github.com/adequatica/ui-testing)中找到。

## 为特定测试集重写全局配置

相关文档: [测试配置选项](https://playwright.dev/docs/test-use-options), [TestOptions 接口](https://playwright.dev/docs/api/class-testoptions/)

Playwright 提供了一个[全局配置文件](https://playwright.dev/docs/test-configuration)来管理测试运行的各种选项。然而,某些测试可能需要完全不同的设置,比如测试的 URL、浏览器配置或特定的用户环境(如窗口大小、地理位置等)。

要为单个测试重写全局配置,可以在测试开始处使用`[test.use()](https://playwright.dev/docs/api/class-test#test-use)`方法来设置所需的参数:

```javascript
test.use({
 baseURL: 'http://localhost:3000',
 ...devices\['Pixel 7'\],
});

test('移动端首页测试', async ({ page }) => {
 await test.step('打开页面', async () => {
 await page.goto('/');
 });
});
```

## 设备模拟

[相关文档](https://playwright.dev/docs/emulation#devices)

Playwright 配置的另一个优势是其设备模拟功能。无需手动设置移动浏览器的 User Agent、视口大小等参数,只需在配置中直接指定目标设备即可(也可以通过上面提到的`test.use()`方法重写配置):

```javascript
use: {
...devices\['iPhone 14'\],
},
```

完整的可模拟设备列表可以
在[Playwright 的 GitHub 仓库](https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json)中找到。

## 离线模式设置

[相关文档](https://playwright.dev/docs/api/class-browsercontext#browser-context-set-offline)

我在一个测试中使用了这个功能,主要是为了检查应用在网络连接丢失时的行为。通过[BrowserContext](https://playwright.dev/docs/api/class-browsercontext)可以轻松启用离线模式:

```javascript
test('测试离线状态', async ({ browser, page }) => {
    await test.step('打开页面并切换到离线', async () => {
    const context = await browser.newContext();
    page = await context.newPage();
    await page.goto('/');
    await context.setOffline(true);
});
```

**需要注意的是,这并非完全的离线模式。** 它会停止网络活动(模拟网络离线),但无法测试那些使用[addEventListener()方法](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)监听[online/offline 事件](https://developer.mozilla.org/en-US/docs/Web/API/Window/offline_event)的应用功能:

```javascript
// 如果你的应用代码中有这样的监听:
window.addEventListener("offline", (event) => {});
// 那么使用 browserContext.setOffline(true)将无法触发这个事件
```

## 断言重试机制

[相关文档](https://playwright.dev/docs/test-assertions#expecttopass)

这是一个非常巧妙的方法,它允许在`expect`内部"重试"[断言](https://playwright.dev/docs/test-assertions):

```javascript
await expect(async () => {
    // 按指定间隔重试,直到请求成功
    const response = await page.request.get('https://sso-motd-api.web.cern.ch/api/motd/');
    expect(response.status()).toBe(200);
}).toPass({
    // 重试间隔: 1 秒, 2 秒, 10 秒, 10 秒
    intervals: \[1000, 2000, 10000\],
    // toPass 的超时设置不受自定义 expect 超时影响
    timeout: 60000,
});
```

这个功能对于测试不稳定的后端 api 接口特别有用。

> 还有一个类似但略有不同的`[expect.poll](https://playwright.dev/docs/test-assertions#expectpoll)`方法,它在断言中实现了[HTTP 轮询](https://medium.com/cache-me-out/http-polling-and-long-polling-bd3f662a14f#0f5c)的概念。

## 等待选择器(已弃用但仍可用) / 等待元素

[相关文档](https://playwright.dev/docs/api/class-elementhandle#element-handle-wait-for-selector)

这是另一个用于检查选择器的优秀方法。

有一种观点认为**不应该在**[**页面对象模型**](https://playwright.dev/docs/pom)中包含断言,尽管 Playwright 自身的示例中也这么做了。

![图 1: 不建议在页面对象中这样做](https://miro.medium.com/v2/resize:fit:700/1*9ItTFE2kQ2BonWtFf7jviA.png)

👆*不建议在页面对象中包含断言*

相反,你可以等待所需的选择器出现,而不使用显式的 assert 或 expect:

```javascript
// 页面工具栏对象
export class Toolbar {
    private page: Page;
    private toggleLocator: Locator;

    constructor(page: Page) {
    this.page = page;
    this.toggleLocator = page.locator('\[class\*=toggle\]');
}

async clickOnToggle(): Promise<void> {
    await this.toggleLocator.click();
    // 已弃用,推荐使用基于定位器的 locator.waitFor()
    await this.page.waitForSelector('\[data-testid="dropdown-menu"\]');
}
}
```

需要注意的是,**这个方法已被弃用,**现在推荐使用`[waitFor()](https://playwright.dev/docs/api/class-locator#locator-wait-for)`。因此,上面的页面对象代码应该改写为:

```javascript
// 页面工具栏对象
export class CernToolbar {
    private page: Page;
    private toggleLocator: Locator;
    private dropdownMenu: Locator;

    constructor(page: Page) {
        this.page = page;
        this.toggleLocator = page.locator('\[class\*=toggle\]');
        this.dropdownMenu = page.getByTestId('dropdown-menu');
    }

    async clickOnToggle(): Promise<void> {
        await this.toggleLocator.click();
        await this.dropdownMenu.waitFor({state: 'visible'});
    }
}
```

更多相关内容:

- [自动化测试编写原则](https://adequatica.medium.com/principles-of-writing-automated-tests-a2b72218264c)

## GitHub Actions 集成报告

[相关文档](https://playwright.dev/docs/test-reporters#github-actions-annotations)

如果你正在使用[GitHub Actions](https://docs.github.com/en/actions/automating-builds-and-tests/about-continuous-integration)进行 CI/CD,那么`github`[报告器](https://playwright.dev/docs/test-reporters)是一个必备的配置选项:

```javascript
// GitHub Actions CI 中使用'github',本地运行时使用'list'
reporter: process.env.CI ? 'github' : 'list',
```

文档中提到这个 reporter 有注释功能,但并未详细说明。实际上,这些注释在 PR 代码中可以直接指出 diff 中失败的代码行。

![图 2: PR中的GitHub报告器注释](https://miro.medium.com/v2/resize:fit:700/1*7YM1yDhsJfqVlalooK7ogQ.png)

👆*PR 中的 GitHub 报告器注释示例*

在工作流作业中,`github`报告器的输出与常规的`list`报告类似。

![图 3](https://miro.medium.com/v2/resize:fit:700/1*zzuw0WClgGOCxeehXiGAVQ.png)

👆*作业中的 GitHub 报告器输出*

## 仅运行上次失败的测试

[CLI 文档](https://playwright.dev/docs/test-cli#reference)

最新版本([1.44](https://playwright.dev/docs/release-notes#version-144))引入了一个新的 CLI 选项,允许只运行上一次执行中失败的测试。

这是 Playwright 测试运行器的一个重大改进。在此之前,我们需要编写自定义脚本来重新运行失败的测试,而现在这个功能已经内置了。

![图 4: last-failed选项只运行失败的测试](https://miro.medium.com/v2/resize:fit:700/1*_ClgjN-zvyqGKOggTHMEsw.png)

_使用 last-failed 选项只运行失败的测试_

## 来源

原文链接: https://adequatica.medium.com/hidden-gems-of-playwright-part-2-ca3e38a5954a

发布时间: 2024 年 5 月 23 日 05:33:13 UTC
