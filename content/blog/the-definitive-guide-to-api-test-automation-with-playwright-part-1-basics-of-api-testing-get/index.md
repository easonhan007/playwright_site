+++
date = 2023-03-13
title = "Playwright API 测试权威指南：第1部分 - API 测试基础之 GET 请求（包括需要登录和不需要登录的接口）"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

现在让我们开始构建 Playwright 的 API 测试。首先,我们需要一个可以测试的网站。我有一个不断更新的优秀网站列表。

[GitHub - BMayhew/awesome-sites-to-test-on](https://github.com/BMayhew/awesome-sites-to-test-on)

从这个列表中,我选择了一个我知道有前后端分离,而且在可预见的未来不会挂掉的网站。[https://automationintesting.online/](https://automationintesting.online/)

这个网站是 [Mark Winteringham](https://www.linkedin.com/in/markwinteringham/) 和 [Richard Bradshaw](https://www.linkedin.com/in/friendlytester/) 的[测试自动化研讨会](https://automationintesting.com/)的配套网站,同时也是《Testing Web APIs》一书中的主要测试系统(这是一本我强烈推荐的好书)。该书使用 Java 提供了 API 自动化的示例,而我将使用 Playwright 构建相同的示例以及书中的其他示例。

[![图片 3](https://playwrightsolutions.com/content/images/2023/03/image.png)](https://www.amazon.com/Testing-Web-APIs-Mark-Winteringham/dp/1617299537?crid=2Y3N4STRLVSBA&keywords=api+test+book&qid=1678342103&sprefix=api+test+book%2Caps%2C120&sr=8-9&ufe=app_do%3Aamzn1.fos.006c50ae-5d4c-4777-9bc0-4513d670b6bc&linkCode=ll1&tag=amazonid54611-20&linkId=e32a5140f8d1ddd80cabbc7b471a4d42&language=en_US&ref_=as_li_ss_tl)

👆 Testing Web APIs 书籍封面

我不会详细介绍这个网站的功能，但我建议你花些时间用浏览器的开发者工具中的 Network 标签页来探索这个网站。这样做可以帮助你很好地了解不同 API 接口的作用及其在网站 UI 中的使用方式。需要注意的是，我们今天要自动化测试的 API 接口只在网站的管理员页面使用（页面底部有一个链接，用户名：admin | 密码：password）。

### 预订 api 接口

我们首先关注 restful booker 平台的预订 api 接口。幸运的是,有一个 Swagger 文档([https://automationintesting.online/booking/swagger-ui/index.html](https://automationintesting.online/booking/swagger-ui/index.html))可以查看可用的 api 接口。

在开始编写代码之前,我总是先通过像 Postman 这样的工具把 api 接口调通。这次我尝试使用 [Thunder Client](https://www.thunderclient.com/),这是一个可以在 VS Code 中使用的扩展。

![图片 4](https://playwrightsolutions.com/content/images/2023/03/image-1.png)

我首先注意到的是一些 api 接口需要 token/鉴权/登录。

- [https://automationintesting.online/booking/summary?roomid=1](https://automationintesting.online/booking/summary?roomid=1) (不需要 token)
- [https://automationintesting.online/booking/](https://automationintesting.online/booking/) (需要 token)

经过一番探索，我发现有一个 API 接口（[https://automationintesting.online/auth/swagger-ui/index.html#/](https://automationintesting.online/auth/swagger-ui/index.html#/)），可以用来生成令牌。我可以将这个令牌作为 HTTP header 传递到上面的 /booking/ 调用中，格式为 `cookie: token={token-goes-here}`。API 认证有很多不同的方式，这是构建 API 自动化时首先需要弄清楚的事情之一。这里有一篇不错的文章，介绍了认证中使用的一些不同技术：[HTTP 初学者指南第 5 部分 认证](https://dev.to/abbeyperini/beginners-guide-to-http-part-5-authentication-3p2p)。

### 探索被测系统!!!

这一步至关重要。如果你对正在测试的系统没有深入了解，请先停下来做这件事。对我来说，我先在 Thunder Client 中建立了一个包含所有 API 接口的集合。在这个过程中，我了解了哪些 API 接口需要认证，哪些 API 接口需要参数，还了解了 JSON 主体未记录的限制（例如：电话号码至少需要 11 个字符，并且在请求主体中需要一个字符串）。下面是我录制的一个交互所有 API 接口的演示会话。我将令牌参数化为一个环境变量，因为我发现必须在每个请求中更新它。这让我意识到，随着测试套件的增长，我肯定会将其保存为 API 自动化中的一个变量！

当我第一次探索应用并开始思考如何自动化所有内容时，一个问题是我们将如何管理测试数据。我注意到一个非常好的事情是，大约每 10 分钟，创建的任何数据都会从数据库中清除，并重新填充一些静态数据（特别是 James Dean 的一个预订，入住日期在过去，即 `2022-02-01`）。在本教程中，我们将基于这些数据创建大部分断言，因为我们假设它们将始终可用。如果不是这样，我们每次都需要创建数据来进行断言（我们将在后面的教程中讲到）。

### 让我们编写第一个用例!

创建一个目录来存放你的测试套件。如果你是第一次做这件事情，你可以创建一个新文件夹。假设你已经安装了 node,进入空文件夹所在的目录,让我们运行

```bash
npm init playwright@latest
```

运行这条命令之后，工具会问你一些问题,我的回答是:

1. Typescript
2. tests
3. n (我们现在还不需要 GitHub actions 文件。)
4. n (我们不需要浏览器,我们在测试 API!)

![图片 5](https://playwrightsolutions.com/content/images/2023/03/image-2.png)

命令完成后,你的主目录中应该有一个 `tests` 和 `tests-examples` 文件夹,以及 `package.json` 和 `playwright.config.ts`。

首先,我们将 `playwright.config.ts` 改动一下

```javascript
import { defineConfig, devices } from "@playwright/test";
import { config } from "dotenv";

config();

export default defineConfig({
  use: {
    baseURL: process.env.URL,
    ignoreHTTPSErrors: true,
    trace: "retain-on-failure",
  },
  retries: 0,
  reporter: [["list"], ["html"]],
});
```

安装 `dotenv`,这将允许我们在项目根目录使用 .env 文件来存储环境变量。

```bash
npm install dotenv --save
```

接下来删除 `/tests-examples/` 目录

然后我们将修改 `example.spec.ts` 来实现一个最简单的 API GET 请求。官方 [API 测试文档](https://playwright.dev/docs/test-api-testing#writing-api-test)描述了两种发起 API 调用的方法,内置的 `request` fixture(我们将在下面使用)或使用 `request context`。我们将重点使用 `request` fixture 进行测试,它可以在用例内部使用。当我们需要在测试用例外进行 API 调用时(从测试块外的另一个文件中的函数),我们将使用 `request context`。

```javascript
import { test, expect } from "@playwright/test";

test("GET booking summary", async ({ request }) => {
  const response = await request.get(
    "https://automationintesting.online/booking/summary?roomid=1"
  );

  expect(response.status()).toBe(200);
  const body = await response.json();
  console.log(JSON.stringify(body));
});
```

这个测试将对 发送 1 个不需要鉴权的 GET 请求，地址是 summary?roomid=1。我目前将响应保存到 `response` 变量中,它代表 [APIResponse](https://playwright.dev/docs/api/class-apiresponse) 类。这使我们可以访问响应体对象、JSON 格式的响应体、文本格式的响应体、响应头、状态码、状态文本、URL,以及一个名为 `.ok()` 的方法,如果状态码在 200-299 之间,它将返回 true。

对于我们的第一个测试,我只对 `response.status()` 进行断言,期望它为 200。我还展示了如何判断 JSON 返回值里的内容,因为我们将希望对它进行一些断言。

![图片 6](https://playwrightsolutions.com/content/images/2023/03/image-3.png)

简单 GET 请求的输出 👆

![图片 7](https://playwrightsolutions.com/content/images/2023/03/image-6.png)

耶!我们做到了 👆

### 让我们整理一下并添加一些更好的断言

首先在根目录创建一个 `.env` 文件，然后加入这一行。这一行的作用是设置了 URL 个环境变量作为接口测试的 BaseURL

```bash
URL=https://automationintesting.online/
```

现在我们可以重构我们的 spec 文件了。

- 我想按 api 接口组织我的 spec,所以我要在测试目录中创建一个 `/booking/` 文件夹。
- 将 `example.spec.ts` 重命名为 `booking.get.spec.ts`
- 更新 spec,添加一个 describe 块,一个更好的测试名称,以及一些额外的断言。
- 最后再添加一个辅助函数 isValidDate() 来验证返回的入住和退房日期是否为真实日期。

```javascript
import { test, expect } from "@playwright/test";

test.describe("booking/summary?roomid={id}", async () => {
  test("GET booking summary with specific room id", async ({ request }) => {
    const response = await request.get("booking/summary?roomid=1");

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(isValidDate(body.bookings[0].bookingDates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingDates.checkout)).toBe(true);
  });
});

export function isValidDate(date: string) {
  if (Date.parse(date)) {
    return true;
  } else {
    return false;
  }
}
```

### 实现更多 GET api 接口并实现自动检查

接下来的两个 GET api 接口需要通过保存为 cookie 的 token 进行认证,所以我们必须将 cookie 放到 header 里才能成功发起调用。剩下的两个接口是 `GET /booking` 和 `GET /booking/{id}`。我回到 thunder client 把这两个接口调通了,这也可以通过用例本身完成。

![图片 8](https://playwrightsolutions.com/content/images/2023/03/image-7.png)

⬆️ 对 booking/ 进行 GET 调用时 Thunder Client 的响应

修改现有的代码，我首先在第 4 行的 `describe` 块内添加了一个新变量 `savedToken`，这是一个我们将在下一步中以编程方式设置的值，但为了测试，我先硬编码了一个值。你可以看到我们的 GET 请求现在有了一个额外的 header 选项，我们在其中传递了一个 cookie，值为 `token=${savedToken}`。在 JavaScript 中，当使用 \` 定义字符串时，js 允许你在 ${} 内添加代码，这称为插值，在编写自动化测试时非常方便。我们还将对我们期望存在的数据进行断言，另外请注意，我们对返回的 response 中的每个值都进行了断言。如果我们假设所有数据都应该返回，这通常是一个好的做法。

在此过程中，我还发现了一个应该报告给开发人员的 bug，在 `booking/summary` 调用中，`bookingDates` 是驼峰式的，而在 `booking/` 的响应中，`bookingdates` 对象是全小写的。这虽然是个小问题，但通过自动化这部分内容，很容易注意到这些差异。

```javascript
import { test, expect } from "@playwright/test";

test.describe("booking/ GET requests", async () => {
  const savedToken = "r2dBKvt8rCo5p74s";

  test("GET booking summary with specific room id", async ({ request }) => {
    const response = await request.get("booking/summary?roomid=1");

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(isValidDate(body.bookings[0].bookingDates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingDates.checkout)).toBe(true);
  });

  test("GET all bookings with details", async ({ request }) => {
    const response = await request.get("booking/", {
      headers: { cookie: `token=${savedToken}` },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(body.bookings[0].bookingid).toBe(1);
    expect(body.bookings[0].roomid).toBe(1);
    expect(body.bookings[0].firstname).toBe("James");
    expect(body.bookings[0].lastname).toBe("Dean");
    expect(body.bookings[0].depositpaid).toBe(true);
    expect(isValidDate(body.bookings[0].bookingdates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingdates.checkout)).toBe(true);
  });
  //booking/{id}
});

export function isValidDate(date: string) {
  if (Date.parse(date)) {
    return true;
  } else {
    return false;
  }
}
```

下一步，我们将为带详细信息的 GET booking by id 接口添加自动化用例，即 GET booking/1。为此，我复制了前面的测试并开始修改，以匹配我在 Thunder Client 中看到的内容。首先，这里没有 bookings 数组，所以我从每个断言中删除了所有这些，并移动了 toBeGreaterThanOrEqual() 断言。

```javascript
import { test, expect } from "@playwright/test";

test.describe("booking/ GET requests", async () => {
  const savedToken = "r2dBKvt8rCo5p74s";

  test("GET booking summary with specific room id", async ({ request }) => {
    const response = await request.get("booking/summary?roomid=1");

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(isValidDate(body.bookings[0].bookingDates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingDates.checkout)).toBe(true);
  });

  test("GET all bookings with details", async ({ request }) => {
    const response = await request.get("booking/", {
      headers: { cookie: `token=${savedToken}` },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(body.bookings[0].bookingid).toBe(1);
    expect(body.bookings[0].roomid).toBe(1);
    expect(body.bookings[0].firstname).toBe("James");
    expect(body.bookings[0].lastname).toBe("Dean");
    expect(body.bookings[0].depositpaid).toBe(true);
    expect(isValidDate(body.bookings[0].bookingdates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingdates.checkout)).toBe(true);
  });

  test("GET booking by id with details", async ({ request }) => {
    const response = await request.get("booking/1", {
      headers: { cookie: `token=${savedToken}` },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.bookingid).toBe(1);
    expect(body.roomid).toBe(1);
    expect(body.firstname).toBe("James");
    expect(body.lastname).toBe("Dean");
    expect(body.depositpaid).toBe(true);
    expect(isValidDate(body.bookingdates.checkin)).toBe(true);
    expect(isValidDate(body.bookingdates.checkout)).toBe(true);
  });
});

export function isValidDate(date: string) {
  if (Date.parse(date)) {
    return true;
  } else {
    return false;
  }
}
```

现在我们有了一组很好的用例,测试了预订 API 下三个 GET 调用的正常路径场景。接下来,我们在 beforeAll() 钩子里增加 1 个请求，然后保存 鉴权要用到的 cookie 的值。

我首先创建了一个 post 请求,将用户名和密码传入 data,并检查 [APIResponse](https://playwright.dev/docs/api/class-apiresponse) 返回的响应。我使用 VS Code 的 Playwright 调试器来做这件事,它在编写代码和深入了解 Playwright 和 JavaScript 的工作原理时非常有用。

通过对 response header 的研究,我决定直接使用 `response.headers()` 来拿到响应返回的 header，然后进一步拿到 cookie 的值。

```javascript
import { test, expect } from "@playwright/test";

test.describe("booking/ GET requests", async () => {
  let cookies = "";

  test.beforeAll(async ({ request }) => {
    const response = await request.post("auth/login", {
      data: {
        username: "admin",
        password: "password",
      },
    });
    expect(response.status()).toBe(200);
    const headers = await response.headers();
    cookies = headers["set-cookie"];
  });
...
```

如你所见，我在 `describe` 块内创建了变量，然后在 `beforeAll` 块中对其进行设置。这是我和团队一直遵循的最佳实践，因为这样可以在所有测试中重复使用这些变量。请注意，我使用了 `let` 关键字声明变量，这样可以让变量在 `beforeAll` 块中被修改或设置。

现在我们有了 cookies 值，里面的信息很多，但我们只关注 token,我们可以重构我们的代码来实现这一点。

```javascript
// from
  test("GET all bookings with details", async ({ request }) => {
    const response = await request.get("booking/", {
      headers: { cookie: `token=${savedToken}` },
    });

// to
 test("GET all bookings with details", async ({ request }) => {
    const response = await request.get("booking/", {
      headers: { cookie: cookies },
    });
```

为确保我们的代码不会出现偶发性故障,我将运行 `npx playwright test --repeat-each=10`命令,这将使每个测试运行 10 次,然后很幸运 💥 它们全都通过了!

![图片 9](https://playwrightsolutions.com/content/images/2023/03/image-8.png)

测试结果 30 个通过 👆

---

可以在[这里](https://github.com/playwrightsolutions/playwright-api-test-demo)找到代码的仓库和分支(api-part1)。

在下一部分(第 2 部分)中,我们将继续处理这个示例代码,为 GET booking api 接口添加更多断言,并覆盖其他的预订 api 接口。我们还将重构一些代码,将可重用的方法放在代码库的单独区域,使一切整洁有序。

非常感谢 [Joel Black](https://www.linkedin.com/in/joel-black-1344a267/) 和 [Sergei Gapanovich](https://www.linkedin.com/in/sgapanovich/),没有他们的影响、反馈和代码审查,这些例子会糟糕得多 😅。

---

感谢阅读!如果你觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下方订阅。

## 来源

URL 来源: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-1-basics-of-api-testing-get/

发布时间: 2023-03-13
