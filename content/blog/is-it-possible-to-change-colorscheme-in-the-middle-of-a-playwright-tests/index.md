+++
date = 2023-07-24
title = "如何在 Playwright 测试中途把浏览器改成暗夜模式?"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

这个问题最近在 Playwright Discord 服务器的 #help-playwright 频道中被提出。如果你还没加入,现在就[加入吧](https://discord.gg/playwright-807756831384403968)!

> 大家好,我希望能在测试过程中改变系统/浏览器的主题偏好,因为我的应用可以在不刷新页面的情况下响应用户偏好的变化。为了验证这一点,我需要能够在测试运行时更改系统/浏览器的主题。

值得注意的是,有多种方法可以实现这一目标,让我们来看看!

## 使用 test.use()

第一种方法是使用 codegen 工具来构建 UI 测试。使用以下命令时,会以暗夜模式的 `color-scheme` 启动 codegen 工具。

```bash
npx playwright codegen --color-scheme=dark
```

默认情况下,生成的 codegen 文件如下:

```javascript
import { test, expect } from "@playwright/test";

test.use({
  colorScheme: "dark",
});

test("test", async ({ page }) => {});
```

这个例子展示了如何在测试用例外使用 `test.use()` 功能。这将确保该文件中运行的所有测试都使用深色 `colorScheme`。

[playwright 的模拟能力](https://playwright.dev/docs/emulation#color-scheme-and-media)

## 使用 page.emulateMedia()

另一种实现方法是在测试用例里使用 `page.emulateMedia()`。这允许你在同一个测试中进行多次检查和断言。在下面的例子中:

- 我访问 [https://www.reddit.com](https://www.reddit.com/)
- 创建一个名为 postContainer 的定位器变量
- 将页面设置为深色模式(暗夜模式) `colorScheme`
- 验证 CSS 背景颜色是深灰色
- 将页面设置回浅色模式(白天模式) `colorScheme`
- 验证 CSS 背景颜色是白色

```javascript
import { test, selectors, expect } from "@playwright/test";

test("验证深色和浅色 CSS", async ({ page }) => {
  selectors.setTestIdAttribute("data-testid");

  await page.goto("https://www.reddit.com/");

  const postContainer = page.getByTestId("post-container").first();

  await page.emulateMedia({ colorScheme: "dark" });
  await expect(postContainer).toHaveCSS(
    "background-color",
    "rgba(26, 26, 27, 0.8)"
  );

  await page.screenshot({
    path: `tests/ui/reddit.com/screenshot/reddit-home-dark.png`,
  });

  await page.emulateMedia({ colorScheme: "light" });
  await expect(postContainer).toHaveCSS(
    "background-color",
    "rgba(255, 255, 255, 0.8)"
  );

  await page.screenshot({
    path: `tests/ui/reddit.com/screenshot/reddit-home-light.png`,
  });
});
```

特别感谢 Twitter 上的 [@r_ydv](https://twitter.com/r_ydv?ref_src=twsrc%5Etfw%7Ctwcamp%5Eembeddedtimeline%7Ctwterm%5Escreen-name%3Ar_ydv%7Ctwcon%5Es2),他创建了下面这篇文章,指导你如何进行 CSS 断言!

[Playwright 验证 CSS](https://testerops.com/playwright-and-css-validation/)

## 在 newContext 和 newPage 中指定

在下面的例子中,我们将在 `test` 块用 context 动态设置 `colorScheme`。

```javascript
test("探索其他选项", async ({ page, browser }) => {
  // 创建深色模式的上下文
  const context = await browser.newContext({
    colorScheme: "dark", // 或 'light'
  });

  // 创建深色模式的页面
  const newPage = await browser.newPage({
    colorScheme: "dark", // 或 'light'
  });

  await newPage.goto("https://www.reddit.com/");

  await newPage.screenshot({
    path: `tests/ui/reddit.com/screenshot/reddit-home-dark-context.png`,
  });

  await context.close();
});
```

## 总结

通过这些例子,你应该有足够多的方法来更新你正在测试的浏览器的 `colorScheme`。所有代码示例都可以在[这里](https://github.com/BMayhew/playwright-demo/tree/master/tests/ui/reddit.com)找到。享受深色模式下的测试乐趣吧!

![图片 5](https://playwrightsolutions.com/content/images/2023/07/image-12.png)

---

感谢阅读!如果你觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下面订阅,别忘了留下一个 ❤️ 来表示你的喜爱。

## 来源

来源 URL: https://playwrightsolutions.com/is-it-possible-to-change-colorscheme-in-the-middle-of-a-playwright-tests/

发布时间: 2023-07-24
