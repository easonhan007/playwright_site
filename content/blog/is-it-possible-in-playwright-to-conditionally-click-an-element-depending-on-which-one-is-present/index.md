+++
date = 2022-12-16
title = "Playwright 中如何根据元素可见性来条件性点击?"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

最近在 Playwright 的 Slack 频道中有人询问是否可以在两个元素中点击可见的那个。有一个回答让我深入了解了 JavaScript 中的 Promise。

解决方案使用了 Promise.race() 方法,该方法接受一个 Promise 数组,并返回最先完成的那个 Promise。

> Promise.race() 方法是 Promise 并发方法之一。当你想要第一个完成的异步任务,但不关心它最终的状态(成功或失败)时,这个方法很有用。

这对我们来说很棒,因为只要我们要交互的定位器有一个是存在的,测试就不会失败。我发现 the-internet.herokuapp.com 网站有一个消失元素的页面可以验证这一点。刷新页面时,"Portfolio"元素总是存在,而"Gallery"元素只是偶尔出现。

下面的代码片段的注释解释了发生的事情,还有一些可用于调试的 console.log 注释。这种实现的优点是,如果被测系统有多个需要考虑的状态,你可以随意向数组中添加任意数量的定位器。

```javascript
test("使用 promise.race 点击数组中的一个元素", async ({ page }) => {
  await page.goto("https://the-internet.herokuapp.com/disappearing_elements");
  // 构建一个可以传入 Promise 数组的 promise
  const waitForLocator = (locator: Locator): Promise<Locator> => {
    return locator.waitFor().then(() => locator);
  };
  let returnedLocator = await Promise.race(
    // Promise/定位器数组
    [
      waitForLocator(page.getByRole("link", { name: "Gallery" })),
      waitForLocator(page.getByRole("link", { name: "Portfolio" })),
    ]
  );
  // console.log(await returnedLocator.innerText());
  await returnedLocator.click();
  // console.log(page.url());
  await expect(page).toHaveURL(/.*gallery|.*portfolio/);
});
```

经过这次尝试后,我开始思考是否有更简单直接的方法来处理这种条件,于是我开始用 if 语句构思解决方案。几分钟后,我就有了一个不错的可行方案,更容易理解。在下面的代码中,我们检查 locator.isVisible(),如果为 true 则继续,如果为 false 则转到下一个代码块。我倾向于使用这种解决方案,因为它能完成任务,而且更易于理解。

```javascript
test("在两个元素中点击可见的那个", async ({ page }) => {
  await page.goto("https://the-internet.herokuapp.com/disappearing_elements");
  const gallery = page.getByRole("link", { name: "Gallery" });
  const portfolio = page.getByRole("link", { name: "Portfolio" });
  if (await gallery.isVisible()) {
    await gallery.click();
  } else if (await portfolio.isVisible()) {
    await portfolio.click();
  }
  await expect(page).toHaveURL(/.*gallery|.*portfolio/);
});
```

**2024 年来自乙醇的注释 👀：我更倾向于第 1 种方案，第 1 种方案更有 javascript 的味道一点，而且支持超过 2 个的 locator。然而，在 2024 年的今天，上面两种方案都不推荐。比较好的实现是 playwright 自带的[locator.or](https://playwright.dev/docs/locators#matching-one-of-the-two-alternative-locators)方案，代码如下**

```javascript
const newEmail = page.getByRole("button", { name: "New" });
const dialog = page.getByText("Confirm security settings");
await expect(newEmail.or(dialog).first()).toBeVisible();
if (await dialog.isVisible())
  await page.getByRole("button", { name: "Dismiss" }).click();
await newEmail.click();
```

---

感谢阅读!如果你觉得这篇文章有帮助,可以在 LinkedIn 上联系我,或考虑给我买杯咖啡。如果你想获得更多内容直接发送到你的收件箱,请在下方订阅。

## 来源

URL 来源：https://playwrightsolutions.com/is-it-possible-in-playwright-to-conditionally-click-an-element-depending-on-which-one-is-present/

发布时间：2022 年 12 月 26 日 13:30:38
