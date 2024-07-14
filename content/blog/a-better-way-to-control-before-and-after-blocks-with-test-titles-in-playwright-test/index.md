+++
date = 2023-06-05
title = "一种更好的方法来通过测试名称控制 before and after 钩子函数"
description = "可以使用testInfo类来动态获取用例的执行状态"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

> "没有持续的成长和进步，改进、成就和成功这样的词就毫无意义。" - 本杰明·富兰克林

你是否曾经看着几个月前写的代码，开始想："哇，'过去的我'认为这很不错，但实际上只是还凑合"？我喜欢这样的时刻，因为它们证明我正在学习和成长，找到新的方法来解决问题或甚至做出小的改进。

去年，我需要有条件地运行 afterEach 块，解决方案是这个：[如何在 Playwright 测试中有条件地使用 afterEach](https://playwrightsolutions.com/how-to-conditionally-use-aftereach) 现在，我为同样的问题找到了另一个解决方案（我个人认为这是一种更好的风格）。

上周，我在编写一组测试时意识到，我需要有条件地运行 beforeEach 块来创建一些测试数据。使用之前用于 afterEach 的相同逻辑似乎不太合适，而且会导致严重依赖测试的顺序。此外，在几个测试中复制相同的代码也不符合 DRY（不要重复自己）原则。

多亏了 `testInfo` 类，你可以在前后块中获取测试标题（注意：beforeAll 只能访问第一个测试，而 afterAll 只能访问最后一个测试）。我不打算告诉你 `testInfo` 有多有用，因为这里已经有一篇关于它的文章：[在 Playwright 测试运行时是否可以获取当前测试名称？](https://playwrightsolutions.com/untitled-2)

有了 `testInfo` 这个武器，我们可以通过测试标题（或其中的关键词）和块本身的简单 if 语句来控制 beforeEach 和 afterEach 块。

```typescript
import { test } from "@playwright/test";
test.describe("通过测试标题控制前后块", async () => {
  test.beforeEach(async ({}, testInfo) => {
    if (testInfo.title.includes("#runBeforeEach"))
      console.log("beforeEach() 已执行");
  });
  test.afterEach(async ({}, testInfo) => {
    if (testInfo.title.includes("#runAfterEach"))
      console.log("afterEach() 已执行");
  });
  test("第一个测试", async () => {
    console.log("第一个测试");
  });
  test("第二个测试 #runBeforeEach", async () => {
    console.log("第二个测试");
  });
  test("第三个测试 #runAfterEach", async () => {
    console.log("第三个测试");
  });
});
```

![图片 1](https://playwrightsolutions.com/content/images/2023/05/code-2.jpg)
输出

显然，`#runBeforeEach` 和 `#runAfterEach` 可以替换为你想要的任何内容。只要确保代码仍然可读并且有意义 😉

请记住，你可以使用 `if` 语句不仅用于整个前/后块，还可以用于其中的一部分。

```typescript
test.beforeEach(async ({}, testInfo) => {
  /*
      需要在每个测试之前运行的一些代码
    */
  if (testInfo.title.includes("#runBeforeEach"))
    console.log("beforeEach() 已执行");
});
```

[URL 来源](https://playwrightsolutions.com/a-better-way-to-control-before-and-after-blocks-with-test-titles-in-playwright-test/)

发布时间: 2023-06-05
