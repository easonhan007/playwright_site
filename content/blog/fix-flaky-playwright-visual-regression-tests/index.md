+++
date = 2023-10-31
title = "如何让Playwright 视觉回归测试稳定运行不出错"
description = "通过截图比较的方案进行自动化测试的成功实践"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我们在流水线中使用视觉回归测试，以确保我们即将发布的代码没有意外更改任何视觉内容。我们通过使用 Playwright 的截图功能捕获页面并上传到 [Percy](https://percy.io/) 来实现这一目标。我们选择 Percy 而不是 Playwright 内置的 [截图比较方案](https://playwright.dev/docs/test-snapshots)，因为我们喜欢一个简单直观的用户界面来查看差异。如果 主干代码 和我们提交的更改之间有差异，我们会得到一个这样的视图，如果满意的话可以进行审核和批准：

![Image 1: Visual regression test in Percy](https://www.houseful.blog/gifs/visual-test-percy-diff.gif)

这已被证明是我们测试工具中的一个非常有价值的工具。然而，视觉测试通常很难保持稳定。这是因为运行在客户端的代码往往并不简单——我们要应对异步触发的脚本、行为不一致的第三方脚本、加载状态、动画、模态框等各种复杂情况。这种复杂性可能导致不稳定和“容易失败”的测试运行结果。

为了让测试用例可以合理的应对我们的更改有，它们需要稳定。如果测试用例老是误报错误，那么开发人员可能会忽略它们，并盲目的把流程转到下一步，这将使它们在流水线中运行的目的失去意义。

在 [Alto](https://www.altosoftware.co.uk/)，我们目前捕获大约 200 张截图，并且这个列表会随着时间的推移而增长。虽然大多数截图是稳定的，但我们发现有一些是非常容易失败的。我们最近花时间解决这些测试问题，使它们稳定，并重建对我们视觉测试的信任。

## mock, mock, mock(模拟、模拟、模拟)

这是一个很好的起点——不要依赖数据库/api 服务提供的数据进行视觉测试。你的应用程序需要在视觉上保持一致，才能使截图比较产生意义，所以我们需要一致的数据集。

我们使用 [Mock Service Worker](https://mswjs.io/) 来模拟：

- api 响应
- 用户配置文件
- feature toggle(功能的开关)

我们选择 Mock Service Worker 是因为我们希望在整个技术栈中使用相同的 mock 技术，不过 Playwright 也有内置的 [API mock](https://playwright.dev/docs/mock)，也可以用于同样的目的。

除了数据模拟，考虑你依赖的浏览器功能。例如，对于日期，我们使用 [这个工具](https://github.com/microsoft/playwright/issues/6347#issuecomment-1085850728) 来模拟它。

## 利用等待

在进行截图之前，请使用 Playwright 的 `waitFor`。`waitFor` 的默认状态是 `visible`，所以在这个例子中，我们知道标题在进行截图之前是可见的：

```javascript
await page.getByRole("heading", { name: "My Heading" }).waitFor();

await page.screenshot({
  path: "myapp/foo-bar.png",
  fullPage: true,
});
```

如果在拍摄截图之前需要运行某些异步操作，你可以等待其视觉状态的变化。在下面的例子中，我们希望确保加载的转菊花从视图中隐藏，并且我们的图像在截图之前是可见的。这确保页面在捕获之前处于正确的状态：

```javascript
// 等待菊花隐藏
await page.getByTestId("loading-spinner").waitFor({
  state: "hidden",
});
// 等待图像可见
await page.getByAltText("My Image").waitFor();

await page.screenshot({
  path: "myapp/foo-bar.png",
  fullPage: true,
});
```

## 捕获你需要的内容

我们注意到在较小的设备尺寸上，当内容显示在模态框中时会出现不稳定情况。它会在不同的地方打开。以下面的例子为例：

![Image 2: A modal appearing over a page](https://www.houseful.blog/img/reeVg1wBML-383.jpeg)

这会引起用例错误导致误报，因为模态框中的所有元素都处于稍微不同的位置。我们问自己，我们在这里试图测试什么？我们已经在点击模态框之前捕获了页面，所以有价值的是模态框的内容。我们的方法是只截图模态框：

![Image 3: The contents of a modal](https://www.houseful.blog/img/zWNN3UMh8s-312.jpeg)

```javascript
await page.getByLabel("My element").screenshot({
  path: "myapp/foo-bar.png",
});
```

这种方法一直很稳定，并且仍然捕获了足够的信息，使我们对频繁的代码修改保持有信心，因为我们的测试用例是可靠的。

## 隐藏/阻止第三方

第三方脚本可能是不可预测且难以测试的。它们在不同的时间点触发，延迟页面加载和交互。回到我们的“捕获你需要的内容”的方法——如果我们有一个嵌入的第三方地图，它在一个 `iframe` 中加载——我们不能信心满满的等待其内容加载，因为第三方代码运行在自己的 document 元素中，并且也容易受到选择器、样式、功能等任何变化的影响。这也不是我们的应用程序代码。在这种情况下，为了让我们的测试更加稳定，我们可以选择屏蔽它：

```javascript
await page.screenshot({
  path: "myapp/foo-bar.png",
  fullPage: true,
  mask: page.locator("#map"),
});
```

![Image 4: A modal appearing over a page](https://www.houseful.blog/img/cZxyNokaS--414.jpeg)

我们仍然可以看到它占据的空间，但我们不会截图这部分的具体内容。

另一种方法是阻止第三方脚本的触发。如果你有 google 或者百度分析、google tag 等类似的异步脚本——任何不属于视觉测试的东西，直接屏蔽掉 👍！

```javascript
// 在访问页面之前阻止谷歌地图
await page.route(/googletagmanager.com/, (route) => route.abort());

await page.goto("https://yourapplication.com");
```

## 禁用动画

动画如过渡可能是不可预测的测试对象，幸运的是我们可以传递 `animations: 'disabled'` 给我们的截图，“有限的动画会快速前进到完成状态，因此它们会触发 transitionend 事件。无限动画会取消到初始状态，然后在截图后重新播放。”（[来源](https://playwright.dev/docs/api/class-elementhandle#element-handle-screenshot-option-animations)）。很简单！

## Chrome 全页面截图错误

我们注意到在某些全页面截图中出现了一些奇怪的行为，图像会被裁剪：

![Image 5: A modal appearing over a page](https://www.houseful.blog/img/ObdrN_-RVl-365.jpeg)

我们得出结论，这很可能是由于 [这个 Chromium 的 bug](https://bugs.chromium.org/p/chromium/issues/detail?id=760596)，可惜的是它被标记为“不会修复”。我们采用了在截图之前滚动页面长度的方法（如[这里](https://github.com/microsoft/playwright/issues/620#issuecomment-578022596) 所建议）来处理截图裁剪问题：

```javascript
// 工具方法
export const scrollFullPage = async (page: Page) => {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let totalHeight = 0;
      const distance = 100;
      const timer = setInterval(() => {
        const scrollHeight = document.body.scrollHeight;
        window.scrollBy(0, distance);
        totalHeight += distance;

        if (totalHeight >= scrollHeight) {
          clearInterval(timer);
          resolve(true);
        }
      }, 100);
    });
  });
};

// 首先滚动页面
await scrollFullpage(page);

// 然后截图
await page.screenshot({
  path: "myapp/foo-bar.png",
  fullPage: true,
});
```

这种方法虽然感觉仍然没有必要，但已经产生了一致的结果。

## 建立稳定性文化

一旦我们对测试的稳定性感到满意，我们需要保持这种状态，所以我们实施了零易碎政策。这意味着，如果发现一个容易失败的视觉测试，它需要立即修复或用 [fixme](https://playwright.dev/docs/api/class-test#test-fixme-1) 标记，直到工程师可以去修复它。这帮助我们维护了一套稳定的测试用例，并确保我们的工程师始终信任回归测试的结果。我们采用这种策略，因为对我们来说，不测试反而比天天运行容易失败的用例要好，测试用例不稳定，还不如不运行。

## 结论

这些只是我们保持视觉测试稳定运行的几个小方法。视觉回归很难做到绝对正确，有很多异常情况，并且很容易变得不稳定。然而，一旦你的测试套件表现的很好，你的开发就有信心对代码进行足够多的修改，并准确的知道用户最终会看到什么。 这就是我们拥有自动化测试的整个目的。

## 来源

[URL 来源](https://www.houseful.blog/posts/2023/fix-flaky-playwright-visual-regression-tests/)
