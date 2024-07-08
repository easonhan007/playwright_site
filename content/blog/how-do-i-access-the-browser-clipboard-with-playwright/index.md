+++
date = 2024-07-07
title = "如何使用 playwright 访问浏览器的剪切板"
description = "用javascript就可以了，不过如何绕过授权是个问题"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

最近我遇到了一个问题，我想与我正在测试的系统中的一个具有“复制到剪贴板”功能的部分交互。这具体是一个我可以生成然后分享的链接。这个部分是我们客户入职流程的一部分，我们认为需要对此进行自动化检查。

![图片1](https://playwrightsolutions.com/content/images/2023/01/image-1.png)

我们将使用 codepen.io 示例进行测试

我们要做的第一件事是导航到网站：[https://codepen.io/shaikmaqsood/pen/XmydxJ](https://codepen.io/shaikmaqsood/pen/XmydxJ)，并点击一个链接或按钮，将某个项目复制到浏览器剪贴板。接下来，我们将实际与浏览器交互以获取复制的值。为了与剪贴板交互，我们将使用在页面类`page.evaluate()`上调用的 evaluate 方法。代码如下所示。

```typescript
//copyToClipboard.spec.ts

import { test, expect } from "@playwright/test";

test("验证复制到剪贴板功能1", async ({ page }) => {
  await page.goto("https://codepen.io/shaikmaqsood/pen/XmydxJ");

  await page
    .frameLocator("#result")
    .getByRole("button", { name: "Copy TEXT 1" })
    .click();

  let clipboardText1 = await page.evaluate("navigator.clipboard.readText()");
  expect(clipboardText1).toContain("Hello, I'm TEXT 1");
});
```

[Github 代码示例](https://github.com/BMayhew/playwright-demo/blob/master/tests/ui/codepen/copyToClipboard.spec.ts)

为了在无人干预的情况下运行此代码，还有另一个步骤，即授予浏览器访问剪贴板的权限。具体来说，需要在`use:{}`块中添加`permissions: ["clipboard-read"]`。没有这个选项，你将在 chrome 中看到这个弹窗，你必须手动允许。

![图片2：codepen.io请求查看复制到剪贴板的文本和图片（阻止/允许按钮）](https://playwrightsolutions.com/content/images/2023/01/image.png)

通过添加以下权限，你将不再收到此由 playwright 控制的浏览器中的弹出窗口。值得注意的是，为了在 headless: true 模式下与 codepen.io 网站交互，我必须传递一个自定义的 userAgent 来绕过 Cloudflare 的“你是人类吗”检查。

```typescript
//playwright.config.ts

import { PlaywrightTestConfig } from "@playwright/test";

const config: PlaywrightTestConfig = {
  use: {
    browserName: "chromium",
    headless: true,
    permissions: ["clipboard-read"],
    userAgent: "some custom ua",
  },
};

export default config;
```

## 引用

[来源网址](https://playwrightsolutions.com/how-do-i-access-the-browser-clipboard-with-playwright/)

发布时间：2023-01-09
