+++
date = 2023-06-19
title = "如何在playwright的测试用例里参数化被测接口的域名? "
description = "环境变量比较简单，扩展起来也方便"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

最近有人问我如何在 Playwright 测试中处理 apiURL 和 baseURL。Playwright 的一大优势是可以直接进行 API 调用来创建数据,或者拦截网络请求以获取用于断言的数据。并非所有人都会遇到这个问题,但如果你的 API 和 UI 使用不同的 URL,希望这篇文章能对你有所帮助。

我发现有 4 种方法可以解决这个问题:

1. 在测试中用例里硬编码 API URL
2. 使用 process.env 环境变量
3. 使用类来创建公共值
4. 使用 Fixtures(我会介绍两种不同的方法)

在示例中,我将使用[Practice Software Testing](https://practicesoftwaretesting.com/),这是一个现代化的结账体验演示网站,由[Roy De Kleijn](https://twitter.com/TheWebTester)创建。以下是一些了解该网站的资源:

- [Practice Software Testing API Swagger 文档](https://api.practicesoftwaretesting.com/api/documentation)
- [Twitter 上介绍不同选项的帖子](https://twitter.com/TheWebTester/status/1593906285300400128)
- [Practice Software Testing GitHub 仓库](https://github.com/testsmith-io/practice-software-testing)

## 在测试中硬编码 API URL

第一种方法是直接在代码中使用 API URL,这并不推荐。因为如果你想测试本地环境、临时环境或沙盒环境,就需要在多处更新代码,这并不理想。

## 使用 process.env 环境变量

第二种方法是在代码中使用环境变量。这也不是最佳方案,但可以让你的项目快速启动。当你有相当数量的测试后,可能需要进一步抽象。

## 使用类来创建公共值

第三种方法是使用静态类。在类中,你可以定义一个公共静态变量,在导入类时可以在任何 Playwright 文件中使用。这种方法非常灵活且可扩展,因为你还可以添加多个静态数据信息或环境变量,同时还能享受智能提示的便利!

```javascript
// lib/helpers/staticVariables.ts

export class StaticVariables {
  public static staticApiURL = process.env.API_URL;
}
```

以下 3 个例子可以在名为`login.ts`的数据工厂文件中看到。这个数据工厂函数`getLoginToken()`的作用是在 UI 测试中使用任意邮箱/密码组合进行 API 调用,获取认证 token,然后将其保存到会话存储中,以便在 Angular UI 应用程序中进行身份验证。

```javascript
// lib/datafactory/login.ts

import { expect, request } from "@playwright/test";
import { StaticVariables } from "../helpers/staticVariables";

let apiURL;

// 硬编码URL
apiURL = "https://api.practicesoftwaretesting.com";

// 直接使用环境变量
apiURL = process.env.API_URL;

// 使用专用类访问变量
apiURL = StaticVariables.staticApiURL;

export async function getLoginToken(email: string, password: string) {
  const createRequestContext = await request.newContext();
  const response = await createRequestContext.post(apiURL + "/users/login", {
    data: {
      email: email,
      password: password,
    },
  });

  expect(response.status()).toBe(200);

  const body = await response.json();
  return body.access_token;
}
```

在这 3 种方法中,我最喜欢的是第 3 种。这种方法可以在任何 TypeScript 文件中使用,这让我觉得它是一个很好的前进方向。

## 使用 Fixtures 创建 apiURL

我将提供两种方法。

### 方法 1:使用 page.ts fixture

这是我最初解决问题的方法。这种方法创建了一个 fixture 来扩展`test`,在 Test Options 中添加了`apiURL`类型的字符串。默认情况下,如果没有提供 apiURL,将分配一个空字符串。我把下面的例子添加到了`lib/pages.ts`文件中,这个文件是我用于基础页面对象的,这样我就不用在每个 UI 测试中导入所有文件。

```javascript
// lib/pages.ts

import { test as base } from "@playwright/test";

export * from "./pages/loginPage";
export * from "./pages/homePage";
export * from "./pages/checkoutPage";

export type TestOptions = {
  apiURL: string,
};

// 这允许你在playwright.config.ts中设置apiURL
export const test =
  base.extend <
  TestOptions >
  {
    apiURL: ["", { option: true }],
  };

export default test;
```

要使用这个方法,你必须在 Playwright 测试用例中从 lib/pages 导入 test,并在`playwright.config.ts`中设置`apiURL`(注意我们这里使用的是`apiURL`,下一节我们将使用`apiBaseURL`。我这样做主要是为了看两个 fixtures 如何并行工作)。

```javascript
// playwright.config.ts

import { defineConfig } from "@playwright/test";
import type { APIRequestOptions } from "./lib/fixtures/apiRequest";
import { TestOptions } from "./lib/pages";

require("dotenv").config();

export default (defineConfig < APIRequestOptions) &
  (TestOptions >
    {
      testDir: "./tests",
      fullyParallel: true,
      forbidOnly: !!process.env.CI,
      retries: process.env.CI ? 2 : 0,
      workers: process.env.CI ? 1 : undefined,
      reporter: [["html"], ["list"]],
      use: {
        baseURL: process.env.UI_URL,
        apiURL: process.env.API_URL,
        apiBaseURL: process.env.API_URL,
        trace: "retain-on-failure",
      },
    });
```

在下面的测试文件中,注意我们从"../lib/pages"导入`test`,这让我们可以在 beforeEach 块中使用在`playwright.config.ts`中设置的 apiURL。

```javascript
// tests/checkoutWithPageFixture.spec.ts

import { expect } from "@playwright/test";
import { test, CheckoutPage, HomePage } from "../lib/pages";

test.describe("使用Page Fixture的基本UI检查", () => {
  const username = process.env.USERNAME || "";
  const password = process.env.PASSWORD || "";

  test.beforeEach(async ({ page, request, apiURL }) => {
    // 使用fixture中的apiBaseURL通过API调用获取登录token
    const response = await request.post(apiURL + "/users/login", {
      data: {
        email: username,
        password: password,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    const token = body.access_token;

    // 使用登录token设置本地存储,使用户保持登录状态
    await page.addInitScript((value) => {
      window.localStorage.setItem("auth-token", value);
    }, token);
  });

  test("添加到购物车并结账", async ({ page }) => {
    const homePage = new HomePage(page);
    const checkoutPage = new CheckoutPage(page);

    await homePage.goto();

    await homePage.product2.click();
    await homePage.addToCart.click();
    await homePage.navCart.click();

    await checkoutPage.proceed1.click();
    await checkoutPage.proceed2.click();
    await checkoutPage.address.fill("123 test street");
    await checkoutPage.city.fill("testville");
    await checkoutPage.state.fill("test");
    await checkoutPage.country.fill("united states");
    await checkoutPage.postcode.fill("12345");

    await checkoutPage.proceed3.click();
    await checkoutPage.paymentMethod.selectOption("2: Cash on Delivery");

    await checkoutPage.accountName.fill("testy");
    await checkoutPage.accountNumber.fill("1234124");
    await checkoutPage.finish.click();

    await expect(checkoutPage.success.first()).toBeVisible();
  });
});
```

### 方法 2:使用 apiRequests.ts fixture

这种方法的功劳完全归于[Yury Semikhatsky](https://github.com/yury-s),他在为添加[api 接口 baseURL](https://github.com/microsoft/playwright/issues/23738)的功能请求提供反馈时提出了这个方法(如果感兴趣,可以去给这个请求点个 👍)。

这种方法与第一种 fixture 方法非常相似,但 Yury 更进一步,不仅创建了一个可以从`playwright.config.ts`文件导入的`apiBaseURL` TestOption(与上面的文件相同),还用`apiRequest`扩展了`test`,当调用时会默认使用`apiBaseURL`替换`baseURL`。这非常巧妙,但如果你与项目中的初级开发人员一起工作,可能不太直观。

```javascript
// lib/fixtures/apiReqeusts.ts

import { test as base, APIRequestContext, request } from "@playwright/test";

export type APIRequestOptions = {
  apiBaseURL: string,
};

type APIRequestFixture = {
  apiRequest: APIRequestContext,
};

// 这个fixture会在使用时用playwright.config.ts中的apiBaseURL覆盖baseURL
export const test =
  (base.extend < APIRequestOptions) &
  (APIRequestFixture >
    {
      apiBaseURL: ["", { option: true }],

      apiRequest: async ({ apiBaseURL }, use) => {
        const apiRequestContext = await request.newContext({
          baseURL: apiBaseURL,
        });

        await use(apiRequestContext);
        await apiRequestContext.dispose();
      },
    });
```

在 spec 中的实现需要你从`../lib/fixtures/apiRequest`文件导入`test`,当使用`apiRequest`进行 API 调用时,你甚至不需要传入 baseURL,它会自动用`playwright.config.ts`中的 apiBaseURL 替换 baseURL。

```javascript
// tests/checkoutWithApiFixture.spec.ts

import { expect } from "@playwright/test";
import { test } from "../lib/fixtures/apiRequest";
import { CheckoutPage, HomePage } from "../lib/pages";

test.describe("使用API Fixture的基本UI检查", () => {
  const username = process.env.USERNAME || "";
  const password = process.env.PASSWORD || "";

  test.beforeEach(async ({ page, apiRequest }) => {
    // 使用fixture中的apiBaseURL通过API调用获取登录token,但全部都在fixture中,所以你甚至不需要在测试中添加apiURL
    const response = await apiRequest.post("/users/login", {
      data: {
        email: username,
        password: password,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    const token = body.access_token;

    // 使用登录token设置本地存储,使用户保持登录状态
    await page.addInitScript((value) => {
      window.localStorage.setItem("auth-token", value);
    }, token);
  });

  test("添加到购物车并结账", async ({ page }) => {
    const homePage = new HomePage(page);
    const checkoutPage = new CheckoutPage(page);

    await homePage.goto();

    await homePage.product2.click();
    await homePage.addToCart.click();
    await homePage.navCart.click();

    await checkoutPage.proceed1.click();
    await checkoutPage.proceed2.click();
    await checkoutPage.address.fill("123 test street");
    await checkoutPage.city.fill("testville");
    await checkoutPage.state.fill("test");
    await checkoutPage.country.fill("united states");
    await checkoutPage.postcode.fill("12345");

    await checkoutPage.proceed3.click();
    await checkoutPage.paymentMethod.selectOption("2: Cash on Delivery");

    await checkoutPage.accountName.fill("testy");
    await checkoutPage.accountNumber.fill("1234124");
    await checkoutPage.finish.click();

    await expect(checkoutPage.success.first()).toBeVisible();
  });
});
```

Yury 的代码库/示例可以在这里找到:

[GitHub - yury-s/bug-23738: bug-23738 bug-23738](https://github.com/yury-s/bug-23738)

本文中的所有代码示例都可以在这个仓库中找到:

[GitHub - playwrightsolutions/playwright-practicesoftwaretesting.com](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com/tree/main)

总结一下,有很多方法可以解决这个问题,我相信还有更多我没有涉及到的方法,但希望这些方法中的一种能让你的 Playwright 测试更加简洁和易于维护。如果你希望 Playwright 原生支持这个功能,请为这个功能请求投票!

[\[Feature\]: 在 playwright.config.ts 中添加 apiEndpoint(类似于 baseUrl) · Issue #23738](https://github.com/microsoft/playwright/issues/23738)

---

感谢阅读!如果你觉得这篇文章有帮助,可以在[LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew)上联系我,或者考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想接收更多内容,可以在下方订阅,别忘了点个 ❤️ 表示支持。

## 来源

URL 来源: https://playwrightsolutions.com/how-do-you-define-an-apiurl-along-with-the-baseurl-in-playwright/

发布时间: 2023-06-19T12:30:01.000Z
