+++
date = 2023-10-16
title = "Playwright API 自动化测试权威指南:第14部分 - 通过扩展 Expect 创建自定义断言"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

本周我将回顾并重构一些测试,为我的代码库添加自定义断言。这是我早期考虑实现的功能,但当时为了保持简单而决定不做。随着 1.39 版本的发布,Playwright 团队推出了一些更简单的方法,通过一个固定文件来扩展你的测试用例和 expect 断言。详见下面的发布说明。

[发布说明 | Playwright 版本 1.39 !](https://playwright.dev/docs/release-notes#version-139)

如果你是第一次加入我们,可以查看[介绍文章](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/)和 [playwright-api-test-demo 代码库](https://github.com/playwrightsolutions/playwright-api-test-demo),其中包含了所有代码示例。

### 为什么你应该关注这个?

最如果你现有的方法对你来说已经足够好,那么你不必在项目中实现自定义断言。但是如果你发现自己一遍又一遍地编写相同的冗长断言,那么自定义 expect 可能会派上用场。

例如,下面的断言可以转换为更简单、更易读的形式。

```javascript
// 我正在对报告数组中的每个预订进行断言
body.report.forEach((booking) => {
  //旧的方式
  expect(isValidDate(booking.start)).toBe(true);
  expect(isValidDate(booking.end)).toBe(true);
  expect(typeof booking.title).toBe("string");

  // 新的方式
  expect(booking.start).toBeValidDate();
  expect(booking.end).toBeValidDate();
  expect(booking.title).toBeString();
});
```

随着最新的 1.39 版本发布,通过 fixture`扩展`expect 的能力以及`mergeExpects`和`mergeTests`的能力,这简化了在所有测试中导入 fixture 的过程! 在此之前,自定义断言是添加到`playwrightconfig.ts`文件中的。这可以在下面的文章中看到。

[在 Playwright 中创建自定义 expects:如何编写你自己的断言](/blog/creating-custom-expects-in-playwright-how-to-write-your-own-assertions)

### 实现自定义 Expects

那么让我们开始通过 fixture 实现一些自定义 expects。我们将从`toBeValidDate()`开始。在之前的例子中,我们创建了一个辅助函数,我们调用它并验证如果日期可解析就返回`true`,今天我们将扩展 expect 文件以包含这个自定义 expect。

```javascript
// lib/fixtures/toBeValidDate.ts

import { expect as baseExpect } from "@playwright/test";

export { test } from "@playwright/test";

export const expect = baseExpect.extend({
  toBeValidDate(received: any) {
    const pass =
      Date.parse(received) && typeof received === "string" ? true : false;
    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeValidDate() 断言失败。\n你期望 '${received}' 是一个有效的日期。\n`,
        pass: false,
      };
    }
  },
});
```

这个自定义 expect 的逻辑很直接,从 expect 接收数据,并验证使用[Date.parse(received)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/parse)方法判断字符串是否可以解析成正确的 date(并且不返回 NaN,这是一个[falsey 值](<https://www.freecodecamp.org/news/falsy-values-in-javascript/#:~:text=Description,)%2C%20and%20false%20of%20course.>))。然后我们返回重写 expect 所需的详细信息。

注意,我在这个 fixture 中同时导出了`test`和`expect`,以便在测试中使用这个 fixture 时可以访问`test`。这是我做出的决定,你在测试中不必这样做。这确实允许我只使用一个 test/expect 导入,而不是从 @playwright/test 导入`test`。

```javascript
// tests/auth/login.post.spec.ts

// 如果我没有导出 test
import { expect } from "lib/fixtures/fixtures"; (关于 fixtures 的更多信息见下文)
import { test } from "@playwright/test";

// 因为我确实导出了 test,所以我可以这样做
import { test, expect } from "lib/fixtures/fixtures";


test.describe("auth/login POST 请求", async () => {
  ...
  test("POST 没有主体", async ({ request }) => {
    const response = await request.post(`auth/login`, {});

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.timestamp).toBeValidDate();
    expect(body.status).toBe(400);
    expect(body.error).toBe("Bad Request");
    expect(body.path).toBe(`/auth/login`);
  });
});
```

我还添加了一些其他的自定义 expects,其中一些在这个项目中不会使用,但对其他人可能有用。下面的自定义断言在我工作中的代码库里被大量使用,因为我们有一个 API,这个接口根据输入的不同有很多潜在的值。在对具有多个返回数组的大型 GET items 请求进行断言时,我们可以为多个值创建更通用的断言。

```javascript
// lib/fixtures/toBeOneOfValues.ts

import { expect as baseExpect } from "@playwright/test";

export { test } from "@playwright/test";

export const expect = baseExpect.extend({
  toBeOneOfValues(received: any, array: any[]) {
    const pass = array.includes(received);
    if (pass) {
      return {
        message: () => "passed",
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

下面的自定义 expects 使得断言响应否是为正确类型变得超级简单!

```javascript
// lib/fixtures/typesExpects.ts

import { expect as baseExpect } from "@playwright/test";

export { test } from "@playwright/test";

export const expect = baseExpect.extend({
  toBeOneOfTypes(received: any, array: string[]) {
    const pass =
      array.includes(typeof received) ||
      (array.includes(null) && received == null);

    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeOneOfTypes() 断言失败。\n你期望 '${
            received == null ? "null" : typeof received
          }' 类型是 [${array}] 类型之一\n${
            array.includes(null)
              ? `警告: [${array}] 数组包含 'null' 类型,这在错误中不会被打印\n`
              : null
          }`,
        pass: false,
      };
    }
  },

  toBeNumber(received: any) {
    const pass = typeof received == "number";
    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeNumber() 断言失败。\n你期望 '${received}' 是一个数字,但它是 ${typeof received}\n`,
        pass: false,
      };
    }
  },

  toBeString(received: any) {
    const pass = typeof received == "string";
    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeString() 断言失败。\n你期望 '${received}' 是一个字符串,但它是 ${typeof received}\n`,
        pass: false,
      };
    }
  },

  toBeBoolean(received: any) {
    const pass = typeof received == "boolean";
    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeBoolean() 断言失败。\n你期望 '${received}' 是一个布尔值,但它是 ${typeof received}\n`,
        pass: false,
      };
    }
  },

  toBeObject(received: any) {
    const pass = typeof received == "object";
    if (pass) {
      return {
        message: () => "passed",
        pass: true,
      };
    } else {
      return {
        message: () =>
          `toBeObject() 断言失败。\n你期望 '${received}' 是一个对象,但它是 ${typeof received}\n`,
        pass: false,
      };
    }
  },
});
```

在下面的 spec 中,你可以看到在一个测试中使用的所有不同的自定义 expects。

```javascript
// tests/test.spec.ts

import { test, expect } from "from "lib/fixtures/fixtures"; // 导入自定义断言定义

test.describe("自定义断言", async () => {
  test("使用fixture", async ({ request }) => {
    const response = await request.post(`auth/login`, {});

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.timestamp).toBeValidDate();

    const dateStr = "2021-01-01";
    expect(dateStr).toBeValidDate();

    const number = 123;
    expect(number).toBeNumber();

    const boolean = true;
    expect(boolean).toBeBoolean();

    const string = "string";
    expect(string).toBeString();

    expect(body.status).toBeOneOfValues([400, 401, 403]);
    expect(body.status).toBeOneOfTypes(["number", "null"]);
  });
});
```

### MergeExpects fixture

如果你在上面的例子中仔细观察,你可能注意到我只有一个导入 `import { test, expect } from "@fixtures/fixtures";` 用于我们添加的所有不同 fixture。在 1.39 版本中,playwright 团队引入了一种简单的方法来合并 `expect.extend` 和 `test.extend`,使你的导入更简洁和整洁! 发布说明可以在[这里](https://playwright.dev/docs/release-notes#version-139)找到。

对于我们的例子,我创建了一个 `fixtures.ts` 文件,内容如下。我正在导入 `mergeExpects()`,这是最新版本的新增功能,以及所有其他 `expect.extend` fixture。然后我创建并导出一个新的 `expect 变量`,将其设置为 `mergeExpects(fixture1, fixture2, fixture3, etc)` 的响应。这将创建一个单一的 `fixture`,可以导入到所有使用这些自定义断言的测试中。

💡 如果你无法访问 `mergeExpects`,你需要在 package.json 文件中将 Playwright 更新到至少 1.39 版本。

```javascript
// lib/fixtures/fixtures.ts

import { mergeExpects } from "@playwright/test";
import { expect as toBeOneOfValuesExpect } from "lib/fixtures/toBeOneOfValues";
import { expect as toBeValidDate } from "lib/fixtures/toBeValidDate";
import { expect as typesExpects } from "lib/fixtures/typesExpects";

export { test } from "@playwright/test";

export const expect = mergeExpects(
  toBeOneOfValuesExpect,
  toBeValidDate,
  typesExpects
);
```

但在我们开始导入 fixture 之前,让我们更新我们的 `tsconfig.json` 并添加 `@fixtures` 相对路径,并用新的导入更新之前的用例和 `fixtures.ts` 文件。

```json
// tsconfig.json

{
  "compilerOptions": {
    "baseUrl": ".",
    "esModuleInterop": true,
    "paths": {
      "@datafactory/*": ["lib/datafactory/*"],
      "@helpers/*": ["lib/helpers/*"],
      "@fixtures/*": ["lib/fixtures/*"]
    }
  }
}
```

有了上面的更改,导入应该看起来像这样

```javascript
// 新的
import { test, expect } from "@fixtures/fixtures";

// 旧的
import { test, expect } from "lib/fixtures/fixtures";
```

你可以在下面的 pull request 中看到整个代码库中添加的所有更改。我没有对 "@playwright/test" 进行查找和替换,尽管我本可以这样做。

[pull request](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/17)

### 我在 VSCode 中遇到的奇怪错误

对于一个我在尝试使用一些自定义 expects 时持续遇到的错误,我仍然有点困惑。见下文。

```
Property 'toBeValidDate' does not exist on type 'MakeMatchers<void, any,
{ toBeOneOfValues(this: State, received: any, array: any[]):
{ message: () => string; pass: true; }
| { message: () => string; pass: false; }; }
& { toBeValidDate(this: State, received: any):
{ ...; }
| { ...; }; }
& { ...; }>'.ts(2339) any
```

我怀疑这可能是 Playwright 代码库的一个 bug,因为它只在存在 `expect(any)` 类型时显示这个错误,在下面的例子中,`body.timestamp` 是 `any` 类型,因为它直到异步响应调用后才被设置。如果我将 `body.timestamp` 改为时间戳的字符串,IDE 错误就会消失。

![图片 7](https://playwrightsolutions.com/content/images/2023/10/image.png)

我花了相当多的时间试图找到一种测量 API 调用持续时间的方法。我最初尝试创建一个请求 fixture,但始终无法使其工作,因为我可以捕获持续时间,但无法将这个持续时间计算传递给 `request` 对象以在响应断言中使用,不过我可以在断言中通过 console.log 打印出来。所以我转而为测试添加了一个持续时间,可以在下面找到一种实现方法。这很冗长,我不太喜欢,但至少是一个前进的方向。

```javascript
// tests/auth/login.post.spec.ts

//COVERAGE_TAG: POST /auth/login

import { test, expect } from "@fixtures/fixtures";
import Env from "@helpers/env";

test.describe("auth/login POST 请求", async () => {
  const username = Env.ADMIN_NAME;
  const password = Env.ADMIN_PASSWORD;

  test("使用有效凭证的 POST", async ({ request }) => {
    // 计算持续时间
    const start = Date.now();

    const response = await request.post(`auth/login`, {
      data: {
        username: username,
        password: password,
      },
    });

    // 计算持续时间
    const end = Date.now();
    const duration = end - start;

    // 断言持续时间
    expect(duration).toBeLessThan(1000);

    expect(response.status()).toBe(200);

    const body = await response.text();
    expect(body).toBe("");
    expect(response.headers()["set-cookie"]).toContain("token=");
  });
});
```

### 总结

1.39 版本的最新功能应该使管理 fixture 的 `imports` 变得更加容易,因为我们可以根据需要合并 fixture! 我相信这对通过 fixture 扩展 `test` 的影响会比扩展 `expect` 更大,因为这可能会使通过 fixture 管理页面对象变得更加容易。

![图片 8](https://playwrightsolutions.com/content/images/2023/10/image-1.png)

## 来源

[URL 来源](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-14-custom-assertions-extending-expect/)

发布时间: 2023-10-16
