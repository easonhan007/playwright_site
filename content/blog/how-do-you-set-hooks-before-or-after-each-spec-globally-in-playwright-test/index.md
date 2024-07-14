+++
date = 2023-09-04
title = "如何在 Playwright Test 中全局设置每个测试前后的钩子函数?"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

这是最近在 Playwright [Discord 频道](https://discord.com/channels/807756831384403968/1139590010111266816/1139590010111266816)中有人提出的问题。

> 我想在每个测试用例结束后对特定数据表进行某种"重置"操作。我可以在每个测试文件中设置 `afterAll` 钩子来实现,但这会导致大量重复代码(想象一下有 100 个测试文件)。所以我们之前在 `test.ts` 文件中添加了钩子函数。我们真的以为这样就能全局生效了。"哦,既然我们在测试文件中定义了这些钩子,它们就会像全局钩子一样工作"。但我们后来发现事实并非如此。我知道 Playwright 有全局的设置和清理函数,但据我所知它们只会在所有测试开始前和结束后各运行一次。我们确实需要一个在每个测试文件结束后运行的钩子函数。如果能在每个 `describe` 块后运行也可以,但我觉得我们无法覆盖它。这个功能目前是否在讨论或已被提出?如果没有,我该怎么做?或者有什么方法/技巧可以实现我们想要的效果?先谢谢大家!我很想听听你们的建议。

帖子中的第一个回答是来自 [Tally Barak](https://www.linkedin.com/in/tallybarak/) 的自动 fixture(Automatic Fixtures)链接。

[自动 fixture](https://playwright.dev/docs/test-fixtures#automatic-fixtures)

自动 fixture

文档中说:"自动 fixture 会为每个测试/工作进程设置,即使测试没有直接列出它们。要创建自动 fixture,请使用元组语法并传递 `{ auto: true }`。"

这意味着只要在文件顶部导入了 fixture,无论 fixture 中包含什么内容,都会自动运行,而不需要在 `test()` 块中引用它。

下面的解决方案并不能完全满足原始需求,因为问题提出者想要在每个 describe 块后或每个测试文件 `xxxx.spec.ts` 完成后运行某些操作。据我所知,目前还无法实现这一点。下面的解决方案将涵盖在每个测试运行后执行 afterEach 的用例。

我只实现过几个 fixture,所以我想尝试为这个问题提供一个解决方案。下面是一个示例。这个 fixture 扩展了 `test` 类,允许在 `await use()` 之前添加代码(这些代码将在测试代码之前执行),而在 `await use()` 之后添加的代码将在测试代码之后执行。

```javascript
// lib/fixtures/hook.ts

import { test as base } from "@playwright/test";

export const test = base.extend<{ testHook: void }>({
  testHook: [
    async ({}, use) => {
      console.log("来自fixture的 BEFORE EACH 钩子");
      // 这里的任何代码都将作为 before each 钩子运行

      await use();

      console.log("来自fixture的 AFTER EACH 钩子");
      // 在这里放置你想在每个测试后自动运行的代码
    },
    { auto: true },
  ],
});

export { expect } from "@playwright/test"; // 从基础测试中导出 'expect',以便在 spec.ts 文件中使用
```

使用该 fixture 的测试规范如下。我在这里使用 `console.log()` 来展示每行代码的运行时机。注意,我在这个测试文件中做的唯一改变是从我们上面创建的 fixture `../../lib/fixtures/hook` 中导入 `test` 和 `expect`。

```javascript
// tests/ui/hooks.spec.ts

import { test, expect } from "../../lib/fixtures/hook";

test.describe("最高层级", () => {
  let x: number;
  x = 1;

  test.beforeAll(() => {
    console.log("--所有测试之前的问候--");
  });

  test.afterAll(() => {
    console.log("--所有测试之后的问候--");
  });

  test.afterEach(() => {
    console.log("<<每个测试之后的问候");
  });

  test.beforeEach(() => {
    console.log(">>每个测试之前的问候");
  });

  test.afterAll(() => {
    console.log("所有测试之后的问候");
  });

  test("测试一", async ({ page }) => {
    expect(x).toBe(1);
  });

  test("测试一 v2", async ({ page }) => {
    expect(x).toBe(1);
  });

  test("测试二", async ({ page }) => {
    expect(x).toBe(1);
  });

  test("测试二 v2", async ({ page }) => {
    expect(x).toBe(1);
  });
});
```

测试结果的输出如下所示。

![Image 3](https://playwrightsolutions.com/content/images/2023/08/image-24.png)

这些更改的 pull request 可以在这里找到。

[pull request](https://github.com/BMayhew/playwright-demo/pull/29)

总结一下,如果你需要在每个测试之前或之后执行代码或捕获信息,使用这样的 fixture 可能会非常有用。

⚠️ 需要考虑的一个风险是,如果你在 before 或 after 钩子中通过数据库 seed 脚本(创建或删除数据库中数据的脚本)或重置脚本修改测试数据,并且运行多个 `shard` 或多个 `worker`,那么数据修改可能会影响其他正在运行的测试。

---

感谢阅读!如果你觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑 [给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下方订阅,别忘了留下一个 ❤️ 来表示你的喜爱。

## 来源

URL 来源: https://playwrightsolutions.com/how-do-you-set-hooks-before-or-after-each-spec-globally-in-playwright-test/

发布时间: 2023-09-04T12:30:14.000Z
