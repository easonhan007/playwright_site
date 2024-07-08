+++
date = 2024-07-08
title = "使用Playwright进行API契约测试"
description = "api契约测试其实并不神秘，playwright就可以做的很好"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "https://images.unsplash.com/photo-1720170494675-e2dcd6de34a7?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
+++

有时作为测试工程师,业务对测试的要求可能相当奇怪,你必须在一个测试套件中采用不同类型的测试。

![图片2: Midjourney提示](https://miro.medium.com/v2/resize:fit:1000/1*ZjhaucB1PZLN6UVIKR4A7Q.jpeg)

## 什么是契约测试

契约测试是一种软件测试类型,专注于验证单独组件/服务之间的交互(通常是两个微服务)。当两个微服务通过 API 交互时,一个服务以预定义的格式发送请求,另一个以预定义的格式响应。这种格式被称为"契约" - 服务(甚至开发团队)之间关于如何承诺相互通信的协议。

"契约"可以是 API 规范,但更常见的是仅仅是作为 JSON 文件的请求和响应体架构,这些文件在两个服务之间共享,它们都根据这些架构测试自己的 API - 这种方法甚至被区分为一种单独的测试方法"[基于架构的契约测试](https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/)"。

在客户端-服务器架构的情况下,前端可以作为各种 API 的消费者或提供者,反之亦然:

![图片3: 前端应用作为契约测试的消费者或提供者](https://miro.medium.com/v2/resize:fit:1000/1*2jB1pd0jqbgO9DqfPDRFww.png)

在许多文章中(参见文章末尾的链接),契约测试与集成测试或端到端测试相对立。但在本文中,我想展示**契约测试可以是端到端测试的一部分** - 它可以只是特定检查的工具。

这种情况可能发生在**前端自动测试的特定业务需求**的情况下,例如检查你的前端是否以特定格式向第三方 API 发出特定请求。换句话说,确保 UI 发送正确的数据。

此外,这些第三方 API[可能不允许在测试期间被请求](https://medium.com/@adequatica/layers-of-defense-against-data-modification-d73e9e93bdf7)。这看起来显然需要用模拟来"关闭"这些第三方 API,但如果你的测试项目上没有任何复杂的模拟基础设施(和/或不想有)怎么办?如果你的[测试在实时的模拟环境中运行](https://adequatica.medium.com/pros-and-cons-of-the-ways-of-end-to-end-automated-testing-in-ci-9bec51e231cb#552a),可能就是这种情况。在这种情况下,你可以在[网络级别通过 Playwright](https://playwright.dev/docs/network)来"关闭"对第三方 API 的请求。

> 在互联网上找到类似的项目并不是问题。有很多 DeFi 初创公司使用开放 API 作为他们的基础设施,但这些 API 大多是 GraphQL 和 JSON-RPC - 这给示例增加了一点复杂性。描述它们与 REST API 的区别不是本文的主题。

## 怎么做契约测试

至少我找到了[Sushi](https://www.sushi.com/swap)加密货币交换页面,其前端只向第三方 API 发出几个所需的 POST 请求(API 的 URL 与当前网站不同):

![图片4: 网站的前端向第三方API发出POST请求](https://miro.medium.com/v2/resize:fit:1000/1*n66Kj3vIydqm_7FfG1Fe2Q.png)

同样的情况在图示表示中如下所示:

![图片5: 网站的前端向第三方API发出POST请求](https://miro.medium.com/v2/resize:fit:1000/1*DYYfRmMtf_T6Qsz2DFTYGw.png)

> 让我提醒你,我关注第三方 API 是因为检查内部 API 不是本文的主题 - 你可以通过内部 API 测试和/或集成测试来检查你的内部 API。

在契约测试中,假定每个组件/服务都是相互隔离的。在这里,你可以使用 Playwright 的网络功能轻松地将前端与第三方 API 隔离:

1. 粗略地[中止请求](https://playwright.dev/docs/network#abort-requests) - 请求**不会**发送到外部 API;
2. 或者[模拟它](https://playwright.dev/docs/mock#mock-api-requests)。

对于第二种情况,如果你只使用[fulfill()](https://playwright.dev/docs/api/class-route#route-fulfill)类,你可以通过中止请求来修改响应。但如果你将`fulfill()`与[fetch()](https://playwright.dev/docs/api/class-route#route-fetch)一起使用,请求将被发送到外部 API。无论哪种方式,**当你用 JSON 填充响应体时 - 你就在进行契约测试**(检查客户端是否正在处理填充的响应),如果这个 JSON 模式与外部 API 端用于测试的模式相同。

对于这两种情况,**你通过**[**waitForRequest()**](https://playwright.dev/docs/api/class-page#page-wait-for-request)**类拦截请求,以测试 POST 的**[**请求体**](https://playwright.dev/docs/api/class-request#request-post-data)**是否符合你的契约**(当然,对于 PUT 或 PATCH 方法也是如此):

![图片6: 通过Playwright拦截HTTP请求](https://miro.medium.com/v2/resize:fit:1000/1*MQiNBfNwaPX0LmbR8anUhw.png)

如果你的请求体是 JSON 格式(我认为这种情况会占 90%),你可以立即使用[postDataJSON()](https://playwright.dev/docs/api/class-request#request-post-data-json)类,通过你喜欢的工具比较 JSON 模式:[Ajv](https://ajv.js.org/json-schema.html), [Zod](https://zod.dev/),或者如果由于某些原因你决定直接比较两个 JSON 对象,可以使用[toEqual()](https://playwright.dev/docs/api/class-genericassertions#generic-assertions-to-equal)断言。

当你只检查请求的契约时,你可能不需要响应,可以简单地中止它(注意,正确的行为取决于你的应用,也许你必须模拟响应以防止应用崩溃):

![图片7: route.abort()在Playwright Inspector中的工作原理](https://miro.medium.com/v2/resize:fit:1000/1*auBhQDfBeHiJFU1s_9HVFw.png)

这里是这样一个测试的[代码示例](https://github.com/adequatica/ui-testing/blob/main/tests/sushi-swap-contract-testing.spec.ts):

```typescript
import { expect, type Page, test } from "@playwright/test";
import { z } from "zod";

// 契约
const schema = z.object({
  jsonrpc: z.string(),
  id: z.number(),
  method: z.string(),
  params: z.array(z.union([z.string(), z.boolean()])),
});

let page: Page;

test.beforeAll(async ({ browser }) => {
  const context = await browser.newContext();
  page = await context.newPage();

  await page.route(
    /.+lb\.drpc\.org\/ogrpc\?network=ethereum.+/,
    async (route) => {
      if (route.request().method() === "POST") {
        await route.abort();
        return;
      }
    }
  );
});

test("Open Sushi Swap", async () => {
  // 等待请求应该在.goto()方法之前,
  // 因为所需的请求可能在页面完全加载之前完成。
  const requestPromise = page.waitForRequest(
    (request) =>
      request.url().includes("lb.drpc.org/ogrpc?network=ethereum") &&
      request.method() === "POST"
  );

  await page.goto("/swap");

  const request = await requestPromise;
  await expect(
    () => schema.parse(request.postDataJSON()),
    "Should have a request by the contract"
  ).not.toThrowError();
});
```

其中,

- `const schema`是[Zod](https://zod.dev/)格式的模式声明;
- 在`beforeAll`钩子中,所有匹配`https://lb.drpc.org/ogrpc?network=ethereum&dkey=Ak765fp4zUm6uVwKu4annC8M80dnCZkR7pAEsm6XXi_w`的 POST 请求都被阻止;
- `const requestPromise`接收匹配`https://lb.drpc.org/ogrpc?network=ethereum&dkey=Ak765fp4zUm6uVwKu4annC8M80dnCZkR7pAEsm6XXi_w`的第一个请求的数据;
- 在`expect()`断言中,参考模式与请求的数据进行解析。如果解析/验证过程没有失败,测试就通过 - `[toThrowError()](https://jestjs.io/docs/expect#tothrowerror)`。

上面呈现的测试可能包含更多步骤和检查,因为契约检查可能只是端到端套件的一部分。

阅读更多关于契约测试的内容:

- [什么是契约测试,为什么我应该尝试它](https://pactflow.io/blog/what-is-contract-testing/)?
- [契约测试 vs 集成测试](https://pactflow.io/blog/contract-testing-vs-integration-testing/);
- [API 契约测试完全指南](https://testsigma.com/blog/api-contract-testing/);
- [API 契约测试:4 个需要验证以满足期望的事项](https://blog.postman.com/api-contract-testing-4-things-to-validate/);
- [契约测试:解锁 CI/CD 管道中 E2E 测试瓶颈的关键](https://www.youtube.com/watch?v=RSl_JcWKE3M)。

此外,理论上,相同的模拟方法可以应用于前端的所有 HTTP API 请求:

![图片8: 模拟API](https://miro.medium.com/v2/resize:fit:1000/1*3pflE2qXx7QlMt7b4A1enQ.png)

## 来源

[来源](https://adequatica.medium.com/api-contract-testing-on-frontend-with-playwright-4509b74b3008)

发布时间: 2023-12-25
