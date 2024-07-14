+++
date = 2024-06-09
title = "如何在 Playwright 中创建动态定位器(locator)?"
description = "这里演示了从api请求里获取动态id，然后生成动态的locator"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

这是一个在 [Playwright Discord](https://aka.ms/playwright/discord) 帮助频道中经常被问到的热门问题。我认为这个问题如此受欢迎的主要原因之一是,没有人想为同一操作反复编写相似的代码，因为每次都只是输入略有不同，写重复的代码会显得比较啰嗦。处理这个问题有很多不同的方法,我将分享我的方法。

我使用的示例网站并不像其他网站那样直观,因为我将从网络请求中获取一个唯一 ID,并将其传递给动态定位器。我测试的网站是 [https://practicesoftwaretesting.com](https://practicesoftwaretesting.com/)。

![图片 1](https://playwrightsolutions.com/content/images/2023/08/image-29.png)

在这个网站上,页面从 API 接口获取数据,并填充了一个可以交互的产品网格。我想创建一个动态定位器,允许我传入一个参数,根据传入的内容动态选择不同的元素。下面是"Combination Pliers"项目的 HTML 代码。

```html
<a
  class="card"
  style="text-decoration: none; color: black"
  data-test="product-01H8ABYWDYXDAYW9HM37N5FC5F"
  href="#/product/01H8ABYWDYXDAYW9HM37N5FC5F"
></a>
<div class="card-img-wrapper">
  <img class="card-img-top" src="assets/img/products/pliers01.jpeg" />
</div>
<div class="card-body">
  <h5 data-test="product-name" class="card-title">Combination Pliers</h5>
</div>
<div class="card-footer">
  <span class="float-end text-muted">
    <span data-test="product-price">$14.15</span>
  </span>
</div>
```

在这个例子中,我们将使用链接上的 `data-test` 属性,其值为 `product-{unique_id}`。我们将构建一个动态定位器,允许我们传入 `unique_id` 来与我们想要交互的项目进行交互。下面的代码出现在我的 `homePage.ts` 文件中。我将 `productId` 设置为一个动态定位器。请看下面的使用示例。

```javascript
// lib/pages/homePage.ts

import { Page } from "@playwright/test";

export class HomePage {
  readonly productId = (id: string) =>
    this.page.locator(`[data-test="product-${id}"]`);

  readonly addToCart = this.page.locator('[data-test="add-to-cart"]');
  readonly navCart = this.page.locator('[data-test="nav-cart"]');

  async goto() {
    await this.page.goto("/#/");
  }

  constructor(private readonly page: Page) {}
}
```

在 spec 文件中,我们需要实际拥有要传入的 `unique_id`。`await homePage.productId(productId).click();` 为了获取唯一的 productId,我使用 `page.route()` 来拦截网络流量并在我的测试中使用这些值。你可以在[这里阅读一个简单的例子](https://playwrightsolutions.com/get-a-response-value-of-an-underlying-network-request-when-running-a-playwright-test/)以了解更多信息。

```javascript
// tests/checkout.spec.ts

import { expect } from "@playwright/test";
import { test, CheckoutPage, HomePage } from "@pages";
import { getLoginToken } from "@datafactory/login";
import { productIdRoute } from "@fixtures/productPageRoute";

test.describe("Basic UI Checks", () => {
  const username = process.env.CUSTOMER_01_USERNAME || "";
  const password = process.env.CUSTOMER_01_PASSWORD || "";
  let productId;

  test.beforeEach(async ({ page }) => {
    // 通过API调用获取登录token
    const token = await getLoginToken(username, password);

    // 在本地存储中设置登录令牌,使用户保持登录状态
    await page.addInitScript((value) => {
      window.localStorage.setItem("auth-token", value);
    }, token);

    productId = await productIdRoute(page);
  });

  test("Add to Cart and Checkout", async ({ page }) => {
    const homePage = new HomePage(page);
    const checkoutPage = new CheckoutPage(page);

    await homePage.goto();
    await homePage.productId(productId).click();
    await homePage.addToCart.click();
    await homePage.navCart.click();

    await checkoutPage.proceed1.click();
...
  });
});

```

在这个例子中,我用异步方法实现了 `page.route()`。

```javascript
// lib/fixtures/productPageRoute.ts

import { HomePage } from "@pages";

/**
 * 设置一个路由来从API响应中检索产品ID。
 * @param page - Playwright页面对象。
 * @param name - 可选的字符串名称,用于获取特定ID。
 * @returns 产品ID。
 * @example
 * const page = await browser.newPage();
 * const productId = await productIdRoute(page); // 获取第二个产品ID
 *
 * const productId = await productIdRoute(page, "Pliers") // 获取名为"Pliers"的产品ID
 */
export async function productIdRoute(page: any, name?: string) {
  let productId;

  await page.route(
    "https://api.practicesoftwaretesting.com/products?between=price,1,100&page=1",
    async (route) => {
      let body;
      const response = await route.fetch();
      body = await response.json();
      if (name) {
        productId = findIdByName(body, name);
        console.log("pid: " + productId);
      } else {
        // 获取列表中的第二个产品
        productId = body.data[1].id;
      }
      route.continue();
    }
  );

  const homePage = new HomePage(page);
  await homePage.goto();

  return productId;
}

function findIdByName(json: any, name: string): string | undefined {
  const data = json.data;
  for (let i = 0; i < data.length; i++) {
    if (data[i].name === name) {
      return data[i].id;
    }
  }
  return undefined;
}
```

我构建的路由器会拦截返回 JSON 的网络流量,并返回 `id`。我添加了一个可选参数 `name`,如果传入该参数,它将动态遍历请求返回的 json 字符串,如果产品名称完全匹配(包括大小写),则返回该 `id` 以供后来使用。

通过这种方式,我可以按名称搜索,获取底层的 `data-id`,然后使用该 `data-id` 动态定位页面上的元素。这只需几行代码就能提供极大的灵活性。示例代码可以在下面找到。

[添加动态定位器和路由以通过名称获取 productId by BMayhew](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com/pull/4)

---

感谢阅读!如果您觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上与我联系,或考虑[为我买杯咖啡](https://ko-fi.com/butchmayhew)。如果您想接收更多内容直接发送到您的收件箱,请在下方订阅。
