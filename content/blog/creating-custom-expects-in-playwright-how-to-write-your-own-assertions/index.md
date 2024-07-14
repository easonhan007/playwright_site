+++
date = 2023-06-26
title = "如何在playwright中创建自定义断言"
description = "可以非常显著的增加测试代码的可读性"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我喜欢阅读，特别是在气温在 80 华氏度中段的时候。坐在泳池边，手捧一本好书，是多么惬意的享受。当一本书写得很好时，阅读起来就很轻松，我可以花几个小时翻页，让我的想象力创造场景和人物……其实代码也是一样的。当代码写得很好时，我通过阅读它就能轻松理解测试/断言在做什么，就像读书一样。我尽量写出可读性强的代码：从有意义的变量名到在逻辑上合适的地方添加空行（“意大利面条类型的代码”我实在看不下去）。

Playwright 可以比较容易的编写出可读性强的代码。以下是一些示例：

```javascript
import { expect } from "@playwright/test";

expect(student.grade).toBeGreaterThanOrEqual(1);
expect(student.loan).toBeTruthy();
expect(student.employer).toBeNull();
```

## 默认断言

这是一个通用值断言的[链接](https://playwright.dev/docs/api/class-genericassertions)。

但是如果你期望一个字符串而你不太关心其值，只想检查其类型该怎么办呢？不幸的是，没有开箱即用的方法，所以我以前是这样写的：

```javascript
// 我以前如何检查字符串
let framework = "playwright";

expect(typeof framework).toBe("string");
```

我不是说它不可读，但我更希望代码写成这样：

```javascript
// 我现在如何检查字符串
let framework = "playwright";

expect(framework).toBeString();
```

如果你阅读了上面代码块中的注释（另一种使代码可读的方法），你可能已经猜到可以编写自己的 expect。你来到这个页面是为了扩展你的知识，现在我们要扩展你的 expect！

要使 `toBeString()` 检查工作，你需要在 `playwright.config.ts` 中添加以下内容

playwright.config.ts👇

```javascript
expect.extend({
  toBeString(received: string) {
    const check = typeof received == "string";

    if (check) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeString() 断言失败。\n你期望 '${received}' 是一个字符串，但它是一个 ${typeof received}\n`,
        pass: false,
      };
    }
  },
});
```

解释：我们通过添加 `toBeString()` 断言扩展了我们的 expect。即使看起来断言接受一个参数，但实际上并没有。 `received` 是 `expect(value)` 的第一个括号中的值。然后我们检查接收到的值是否是字符串类型，如果是，则检查通过。如果不是，我们就让检查失败，并通过添加自定义消息使代码更具可读性。

让我们看看它是如何工作的。

```javascript
let value = 123;

expect(value).toBeString();
```

这个断言会失败 ☹️

由于在这个例子中 `value` 显然不是字符串，所以我预计它会失败。果然不出所料，注意自定义的错误信息，这个很好 👇。

![图片2](https://playwrightsolutions.com/content/images/2023/06/2023-06-24_09-35-32-1.jpg)

我还在我的工具包中添加了 `.toBeNumber()` 和 `.toBeBoolean()`。

几周前，我写了 `.toBeOneOfValues()`，这是一个改变游戏规则的方法。我在无法预测确切值的时候使用它，但我知道它应该是已知值之一。我主要用于为 GET 请求编写 API 检查。例如，当我有一个返回的收费参数，它可能是“pending”（待处理）、“failed”（失败）或“successful”（成功），我只想检查每一个返回的结果都有一个预期的值。

```javascript
let validValues = ["failed", "pending", "successful"];
let testValue = "created";

expect(testValue).toBeOneOfValues(validValues);
```

在底层我们将检查数组是否包含传递的值

同样，它会打印出自定义的错误信息 👇。

![图片3](https://playwrightsolutions.com/content/images/2023/06/2023-06-24_10-56-02.jpg)

以下是需要添加到 `playwright.config.ts` 中的源代码

playwright.config.ts

```javascript
expect.extend({
  toBeOneOfValues(received: any, array: any[]) {
    const check = array.includes(received);

    if (check) {
      return {
        message: () => "通过",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeOneOfValues() 断言失败。\n你期望 [${array}] 包含 '${received}'\n`,
        pass: false,
      };
    }
  },
});
```

这里最重要的收获是要意识到你可以创建你需要的自定义断言，以提高可读性。对我有帮助的是查看我要检查的值，并在脑海中说“我希望这个值……”然后用英语完成这个句子。这样你就得到了伪代码。(中文用户表示增加英文的可读性其实 😂，你懂的)

这篇文章是基于[此文档](https://playwright.dev/docs/test-configuration#add-custom-matchers-using-expectextend)编写的。如果你使用 TypeScript，则需要额外的一步使自定义断言工作，这涉及添加一个 `global.d.ts` 文件。以下是我为上述两个 expect 编写的文件。

global.d.ts

```typescript
export {};

declare global {
  namespace PlaywrightTest {
    interface Matchers<R> {
      toBeOneOfValues(array: any[]): R;
      toBeString(): R;
    }
  }
}
```

## 来源

URL 来源: https://playwrightsolutions.com/creating-custom-expects-in-playwright-how-to-write-your-own-assertions/

发布时间: 2023-06-26T12:30:49.000Z
