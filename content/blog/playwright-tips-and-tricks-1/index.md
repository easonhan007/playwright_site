+++
date = 2023-12-07
title = "Playwright 使用技巧与诀窍  #1"
description = "非常实用"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

当你使用一个框架工作时，你会开始遇到各种可以学习的情况。有些事情非常重要，但并不容易仅通过阅读文档或跟随教程就能发现。这些都是通过经验积累的。我想分享一些我最近关于 Playwright 学到的知识。

在下面的陈述中，我将谈论使用`page.locator()`作为定位器方法的占位符，但这并不意味着我建议只使用`locator()`。关于这个话题，我实际上推荐使用 Playwright 创建的内置定位器方法，主要是`getByTestId()`，如果你尝试了所有方法都不起作用，那么再使用`.locator()`。

---

### 1. 如何在只有父元素有唯一 ID 的情况下查找子元素

例如，如果你有 `uniqueIDParent > div1 > div2 > span`（其中 span 有你想要的"文本"），但有多个具有不同文本的子元素（spans），如果你给 Playwright 它的父元素、祖父元素或更高级的祖先，它将遍历所有子元素并提取所有文本。`expect(uniqueID).toHaveText("text you want")` 将起作用。同时，`page.getByTestId(uniqueIDParent).filter({ hasText: "text you want" })` 如果你只针对具有你想要文本的子元素，也能很好地工作。[过滤](https://playwright.dev/docs/locators?ref=blog.martioli.com#filtering-locators)效果神奇。

---

### 2. 为什么有时在 Playwright 中会出现 the error browser has been closed 错误

原因可能是你可能在某处忘记了`await`。Playwright 以异步方式工作，意味着它全是 Promise，但你需要你的测试步骤按顺序、从上到下运行并按该顺序执行操作。这是通过使用`await`关键字来解决 Promise 并保持步骤顺序，以避免竞争条件问题。有时 VS Code 会建议你不需要一些 await，请忽略它，你**确实**需要它们。

---

### 3. 自动等待

以下是 Selenium 中一些典型的断言，在 playwright 里你不再需要这么做

- 你不必在与元素交互之前断言元素可见。Playwright 将在交互前执行以下操作：

> - 检查元素是否可见
> - 检查是否附加到 DOM
> - 检查是否稳定，动画已完成

- 当你打开页面或点击链接重定向到页面时，你不必断言页面已加载才能与元素交互，playwright 会先等待页面完全加载
- 当你等待元素出现或等待元素消失时，你不必编写显式等待。Playwright 有[内置超时](https://playwright.dev/docs/test-timeouts?ref=blog.martioli.com)（你在 Selenium 中熟悉的显式等待），它将等待一个元素并在设定的时间间隔内尝试找到它（例如：默认情况下，`expect(locator).toBeVisible()`的等待时间是 5 秒）

---

### 4. 有时会出现超时不起作用的非常特殊的情况

或者你就是无法弄清楚该怎么办，你还有最后一个选择，就是简单地使用[waitForTimeout()](https://playwright.dev/docs/next/api/class-frame?ref=blog.martioli.com#frame-wait-for-timeout)等待固定的秒数。通常不建议这样做，但有时你就是别无选择。

---

### 5. 如何在 Playwright 中断言字符串数组？

`expect(locator).toHaveText(array)` - 它实际上可以接受一个数组，并且在底层会遍历它以断言项目存在。

---

### 6. 如何在 Playwright 中处理多个元素？

Playwright 定位器将使用相同的方法找到一个或多个具有相同特征的元素，取决于你提供的内容。如果你想处理多个元素（在 Selenium 中，你会使用`findElements`，它会返回一个元素数组），在 Playwright 中，如果你执行`page.locator(multipleElements)`，这将返回多个元素，但**仅仅**是 Playwright 在底层的多个元素，而不是为你返回（至少不是简单的对象数组）。你得到的只是一个单一的定位器（对象）。**为什么会这样？**因为你可能想找到一个单一元素并尝试点击它，所以当你执行操作时，如果属性属于多个元素，它不会让你点击多个元素，并且会抛出错误，建议你如何修复你的测试。但如果你**真的**想处理所有元素，怎么做？你必须在末尾添加`.all()`。示例：`page.locator(multipleElements).all()`

---

### 7. 如何处理较大的文本块？

有时你可能有多个具有文本的项目，如果你给 Playwright 所有项目的父元素，那么 Playwright 可以将这些文本提取为数组。你可以通过`page.locator(parentOfElementsWithText).allTextContents()`或`.allInnerTexts()`来实现。这种方法的缺点是不建议断言文本的精确匹配，主要是因为有时会获取换行符（/n）、逗号或额外空格，但它可以与`expect(locator).toContain()`一起使用。

---

### 8. 如何在 Playwright 中断言元素不存在？

你可以在 stackoverflow 上找到这个小技巧：`expect(locator).toHaveCount(0)`。这类似于 Selenium 的`findElements`，如果没有找到元素，它只返回一个空数组。这很好，因为它不会使测试失败。但是，我建议使用 Playwright 内置的[NOT 运算符](https://playwright.dev/docs/next/test-assertions?ref=blog.martioli.com#negating-matchers)，这才是你实际应该使用的。示例：`locator(element).not.toBeVisible()`。作为一般实践，所有断言方法都可以与**NOT**一起使用。

---

### 9. 如何处理简单使用 getByTestId()不够的情况？

有各种场景，比如表格，你需要组合父元素和子 Web 元素以获取所需数据。因此，在转向`locator()`并构建超复杂的`css选择器`或`xpath`之前，考虑使用[and 运算符](https://playwright.dev/docs/api/class-locator?ref=blog.martioli.com#locator-and)，例如`page.getByText(elem).and(page.getByText(elem))`，或者你可以这样做`page.getByTestId(elem).getByTestId(elem)`。另一个选择是使用[过滤定位器](https://playwright.dev/docs/next/locators?ref=blog.martioli.com#filtering-locators)。过滤器也可以与[NOT 运算符](https://playwright.dev/docs/next/locators?ref=blog.martioli.com#filter-by-not-having-text)混合使用。

---

### 10. 使用一个父元素执行多个操作

你可以将元素存储在`const element = page.locator()`中。注意，这是少数几种不需要在`page.locator()`前使用`await`的场景之一。你可以将其视为占位符。稍后在你的代码中，你可以执行`element.click()`或通过其子元素搜索`element.getByTestId(child)`。关于这个的**酷**特性是，每次调用元素时，它都会重新查询 DOM。

---

### 11. 不要使用$(locator)或$$(multiple)

在 Playwright 中使用$或$$是[元素句柄](https://playwright.dev/docs/api/class-elementhandle?ref=blog.martioli.com)，这是Playwright强烈不推荐的。主要原因是你可能遇到使用$只引用 DOM 先前版本中的元素的情况。你可能最终会看到众所周知的 Selenium 错误`StaleElementReferenceException`。

---

### 12. 如果必须等待应用响应，并且响应时间超过通常的 5 秒怎么办？

你可能会遇到这种情况，例如当你执行一个操作、点击、提交，并且获得响应需要更长的时间，可能会出现"旋转加载器"或类似情况。如果你知道会发生这种情况，你可以增加等待响应的超时时间，仅针对单个特定操作，例如`expect(locator).toBeVisible({ timeout: 20000 })`。通过在方法内传递超时时间，这将只覆盖该行代码的默认 Playwright 配置（希望你不再看到错误`error: timed out 5000ms waiting for expect(locator).tobevisible()`，并且你的测试将通过）。

---

### 13. 为什么有时 expect 没有通常的 toHaveText()方法？

但如果我尝试`toBe()`，它就有效了。这取决于你给`expect()`的对象。如果你给它一个标准定位器，它将具有所有[Web 优先断言](https://playwright.dev/docs/best-practices?ref=blog.martioli.com#use-web-first-assertions)，但如果你给它一个修改后的对象，类似于`page.locator(elementWithText).innerText()`，由于`innerText()`方法，这不再是标准的 Playwright 对象，而对于其他对象，它使用[jest expect 方法](https://jestjs.io/docs/expect?ref=blog.martioli.com)。Playwright 的 expect 对象将检测你给它的对象类型，并将使用 jest expect 的`toBe()`或 Playwright 方法的`toHaveText()`。只需记住 Playwright 方法有自动等待重试，而 jest 方法没有。

---

### 14. Web 元素上的多个数据测试 ID 属性

我们可以在 Playwright 中配置使用自定义测试 ID 属性。使用`getByTestId()`方法时，Playwright 默认为`data-testid="selector"`，因此如果你的 Web 应用程序有不同的默认 ID 定位器，你必须首先[设置 testIdAttribute](https://playwright.dev/docs/api/class-testoptions?ref=blog.martioli.com#test-options-test-id-attribute)。这包括如果你的网站在`id="selector"`格式下有唯一 ID。但是**你能配置使用多个测试 ID 属性吗**？答案是**不**。不过，有一个小技巧。你可以在一般配置中使用不同的`testIdAttribute`，并在项目中使用不同的属性。或者你可以有具有不同 ID 的不同项目。当你有两个团队或团队组，他们开发了使用一种类型唯一 ID 的应用程序，另一个使用不同的唯一 ID 时，这很有用。这可能是从旧版应用程序迁移的情况。下面是一个示例：

```
  projects: [
    {
      name: "new-mega-awesome-app",
      testDir: "./tests",
      use: {
        ...devices["Desktop Chrome"],
        testIdAttribute: "id",
        baseURL: "https://newapp.domain.com",
      },
    },
    {
      name: "legacy-app",
      testDir: "./tests-for-legacy-app",
      use: {
        ...devices["Desktop Chrome"],
        testIdAttribute: "data-testid",
        baseURL: "https://legacyapp.domain.com",
      },
    },
  ],
```

如果你觉得这很有用，请点赞。或者如果你想更多地激励我，甚至可以[请我喝咖啡](https://ko-fi.com/adrianmaciuc?ref=blog.martioli.com)。

## 来源

[https://blog.martioli.com/playwright-tips-and-tricks-1/](https://blog.martioli.com/playwright-tips-and-tricks-1/)
