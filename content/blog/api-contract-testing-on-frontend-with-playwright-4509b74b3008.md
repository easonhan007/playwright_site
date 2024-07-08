+++
date = 2024-07-08
title = "API Contract Testing on Frontend with Playwright"
description = "playwright和selenium的区别是什么？playwright会取代selenium吗？"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础"]
[extra]
math = false
image = "https://images.unsplash.com/photo-1720170494675-e2dcd6de34a7?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
+++

Title: API Contract Testing on Frontend with Playwright - Andrey Enin - Medium

URL Source: https://adequatica.medium.com/api-contract-testing-on-frontend-with-playwright-4509b74b3008

Published Time: 2023-12-25T07:56:19.943Z

Markdown Content:
Sometimes, as a test engineer, business requirements for testing may be quite weird, and you have to adopt different types of testing in one suite.

---

[![Image 1: Andrey Enin](https://miro.medium.com/v2/resize:fill:88:88/2*bQ4xmdoPtrdMchCQCia7iQ.png)](https://adequatica.medium.com/?source=post_page-----4509b74b3008--------------------------------)

![Image 2: Midjourney prompt](https://miro.medium.com/v2/resize:fit:1000/1*ZjhaucB1PZLN6UVIKR4A7Q.jpeg)

_Midjourney prompt: http api contact test frontend application, 2d abstract scheme, engineering drawing, kandinsky style, white background_

Contract testing is a type of software testing that focuses on verifying the interaction between separate components/services (more often, it is two microservices). When two microservices interact via the API, one service sends requests in a predefined format, and another responds in a predefined format. This format is called a «contract» — an agreement between services (and even dev teams) on how they commit to communicating with each other.

A «contract» can be an API specification, but more often, it is just a request and response bodies’ schemas as JSON files, which are shared between two services, and both of them test their APIs against these schemas — this approach is even distinguished into a separate testing method «[schema-based contract testing](https://pactflow.io/blog/contract-testing-using-json-schemas-and-open-api-part-1/)».

In the case of client-server architecture, the frontend can act as a consumer or provider for various APIs and vice versa:

![Image 3: Frontend application as a consumer or provider for contract testing](https://miro.medium.com/v2/resize:fit:1000/1*2jB1pd0jqbgO9DqfPDRFww.png)

Fig. 1. Frontend application as a consumer or provider for contract testing

In many articles (see links at the end of the article), contract testing is opposed to integration or end-to-end testing. But in this article, I want to show that **contract testing can be a part of end-to-end testing** — it can be just a tool for specific checks.

This occasion can happen in the case of **specific business requirements for frontend autotests**, for example, to check that your frontend makes specific requests to third-party APIs in a particular format. In other words, to ensure that UI sends correct data.

Moreover, these third-party APIs [may not allowed to be requested](https://medium.com/@adequatica/layers-of-defense-against-data-modification-d73e9e93bdf7) during the tests. That looks like an obvious necessity to «close» these third-party APIs by mocks, but what if you don’t have any complex mocking infrastructure on your test project (and/or don’t want to have)? It can be so if your [tests run against a live staging environment](https://adequatica.medium.com/pros-and-cons-of-the-ways-of-end-to-end-automated-testing-in-ci-9bec51e231cb#552a). In such cases, you can «close» requests to third-party APIs on a [network level by Playwright](https://playwright.dev/docs/network).

> It was not a problem to find a similar project on the Internet. There are a lot of DeFi startups who use open APIs for their infrastructure, but these APIs are mostly GraphQL and JSON-RPC — which adds a little bit of complexity to the example. The description of their differences from REST API is not the topic of this article.

At least I found [Sushi](https://www.sushi.com/swap) cryptocurrency swap page, whose frontend does just a few desired POST requests to third-party API (API’s URL is different from the current website):

![Image 4: Website’s frontend does POST requests to third-party APIs](https://miro.medium.com/v2/resize:fit:1000/1*n66Kj3vIydqm_7FfG1Fe2Q.png)

Fig. 2. [Website](https://www.sushi.com/swap)’s frontend does POST requests to third-party APIs

The same case in a scheme representation looks like this:

![Image 5: Website’s frontend does POST request to third-party API](https://miro.medium.com/v2/resize:fit:1000/1*DYYfRmMtf_T6Qsz2DFTYGw.png)

Fig. 3. Website’s frontend does POST request to third-party API

> Let me remind you that I focus on third-party APIs because checking an internal API is not the case for this article — you can check your internal APIs by your internal API tests and/or integration ones.

In contract testing, it is implied that each component/service is isolated from each other. Here, you can easily isolate frontend from third-party API with Playwright’s network capabilities:

1.  Roughly [abort request](https://playwright.dev/docs/network#abort-requests) — the request **will not be sent** to an external API;
2.  Or [mock it](https://playwright.dev/docs/mock#mock-api-requests).

For the second case, you can modify the response with the abortion of the request if you use only `[fulfill()](https://playwright.dev/docs/api/class-route#route-fulfill)` class. But if you use `fulfill()` with `[fetch()](https://playwright.dev/docs/api/class-route#route-fetch)`, the request will be sent to the external API. In both ways, **when you fulfill the response body with JSON — you make contract testing** (checking that the client is processing the fulfilled response) if this JSON scheme is the same as the one used for testing on the side of the external API.

For both cases, **you intercept the request by** `[**waitForRequest()**](https://playwright.dev/docs/api/class-page#page-wait-for-request)` **class for testing POST’s** [**request body**](https://playwright.dev/docs/api/class-request#request-post-data) **against your contract** (and, of course, for PUT or PATCH methods):

![Image 6: HTTP request interception through Playwright](https://miro.medium.com/v2/resize:fit:1000/1*MQiNBfNwaPX0LmbR8anUhw.png)

Fig. 4. HTTP request interception through Playwright

If your request body is in JSON format (I think this will happen 90 percent of the time), you can instantly use `[postDataJSON()](https://playwright.dev/docs/api/class-request#request-post-data-json)` class for comparison JSON schemes by your favorite tool: [Ajv](https://ajv.js.org/json-schema.html), [Zod](https://zod.dev/), or use `[toEqual()](https://playwright.dev/docs/api/class-genericassertions#generic-assertions-to-equal)` assertion, if for some reason you decide to compare the two JSON objects head-on.

While you are checking only the request’s contract, you may not need the response and may simply abort it (attention, the right behavior depends on your application, and maybe you have to mock the response to prevent the application’s crash):

![Image 7: How route.abort() works in Playwright Inspector](https://miro.medium.com/v2/resize:fit:1000/1*auBhQDfBeHiJFU1s_9HVFw.png)

_Fig. 5. How route.abort() works in Playwright Inspector_

Here is the [code example](https://github.com/adequatica/ui-testing/blob/main/tests/sushi-swap-contract-testing.spec.ts) of such a test:

import { expect, type Page, test } from '@playwright/test';  
import { z } from 'zod';// Contract  
const schema = z.object({  
 jsonrpc: z.string(),  
 id: z.number(),  
 method: z.string(),  
 params: z.array(z.union(\[z.string(), z.boolean()\])),  
});

let page: Page;

test.beforeAll(async ({ browser }) => {  
 const context = await browser.newContext();  
 page = await context.newPage();

await page.route(/.+lb\\.drpc\\.org\\/ogrpc\\?network=ethereum.+/, async (route) => {  
 if (route.request().method() === 'POST') {  
 await route.abort();

return;  
 }  
 },  
 );  
});

test('Open Sushi Swap', async () => {  
 // Waiting for a request should be before .goto() method,  
 // because desired request can be done before the page is fully loaded.  
 const requestPromise = page.waitForRequest(  
 (request) =>  
 request.url().includes('lb.drpc.org/ogrpc?network=ethereum') &&  
 request.method() === 'POST',  
 );

await page.goto('/swap');

const request = await requestPromise;  
 await expect(  
 () => schema.parse(request.postDataJSON()),  
 'Should have a request by the contract',  
 ).not.toThrowError();  
});

Where,

- `const schema` is a scheme declaration in [Zod](https://zod.dev/)’s format;
- In `beforeAll` hook, all POST requests to URLs match `https://lb.drpc.org/ogrpc?network=ethereum&dkey=Ak765fp4zUm6uVwKu4annC8M80dnCZkR7pAEsm6XXi_w` are blocking;
- `const requestPromise` receives data from the first request matches `https://lb.drpc.org/ogrpc?network=ethereum&dkey=Ak765fp4zUm6uVwKu4annC8M80dnCZkR7pAEsm6XXi_w`;
- In `expect()` assertion, the reference scheme is parsed against the request’s data. The test passes if the parsing/validating process does not fail — `[toThrowError()](https://jestjs.io/docs/expect#tothrowerror)`.

The test presented above may contain more steps and checks because the contract’s check may be just a part of the end-to-end suite.

Read more about contract testing:

- [What is contract testing and why should I try it](https://pactflow.io/blog/what-is-contract-testing/)?
- [Contract Testing Vs Integration Testing](https://pactflow.io/blog/contract-testing-vs-integration-testing/);
- [A Complete Guide to API Contract Testing](https://testsigma.com/blog/api-contract-testing/);
- [API contract testing: 4 things to validate to meet expectations](https://blog.postman.com/api-contract-testing-4-things-to-validate/);
- [Contract Testing: The Key to Unlocking E2E Testing Bottlenecks in CI/CD pipelines](https://www.youtube.com/watch?v=RSl_JcWKE3M).

Furthermore, in theory, the same approach to mocking can be applied to all HTTP API requests on frontend:

![Image 8: Mock APIs](https://miro.medium.com/v2/resize:fit:1000/1*3pflE2qXx7QlMt7b4A1enQ.png)

Fig. 6. Mock APIs
