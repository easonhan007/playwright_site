+++
date = 2023-03-27
title = "Playwright API 测试权威指南：第2部分 - 更多用例"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

让我们来测试 post 请求。我不会在这组测试中深入太多细节,因为本文还有 PUT 和 DELETE 请求要讨论。下面的断言要花一些时间来重构,因为需要创建一些辅助函数和数据工厂函数,以使 POST spec 更简单。我不会详细介绍这些函数,但简单概括如下:

- `createRandomBookingBody` - 需要房间 ID、入住日期和退房日期,并创建一个可用于 POST 到 `booking/` api 接口的请求体。💡 我们也可以用它来断言响应体!!!
- `futureOpenCheckinDate` - 需要一个房间 ID,并返回一个日期字符串 `2023-03-31T00:00:00.000Z` (这使用了获取预订 API 并进行一些快速计算)
- `stringDateByDays` - 需要一个日期字符串和一个可选的数字。它会根据今天的日期添加或减去天数,并返回一个日期字符串 `2023-03-24`

```javascript
import { test, expect } from "@playwright/test";
import {
  createRandomBookingBody,
  futureOpenCheckinDate,
} from "../../lib/datafactory/booking";
import { stringDateByDays } from "../../lib/helpers/date";

test.describe("booking/ POST requests", async () => {
  let requestBody;
  let roomId = 1;

  test.beforeEach(async ({ request }) => {
    let futureCheckinDate = await futureOpenCheckinDate(roomId);
    let checkInString = futureCheckinDate.toISOString().split("T")[0];
    let checkOutString = stringDateByDays(futureCheckinDate, 2);

    requestBody = await createRandomBookingBody(
      roomId,
      checkInString,
      checkOutString
    );
  });

  test("POST new booking with full body", async ({ request }) => {
    const response = await request.post("booking/", {
      data: requestBody,
    });

    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body.bookingid).toBeGreaterThan(1);

    const booking = body.booking;
    expect(booking.bookingid).toBe(body.bookingid);
    expect(booking.roomid).toBe(requestBody.roomid);
    expect(booking.firstname).toBe(requestBody.firstname);
    expect(booking.lastname).toBe(requestBody.lastname);
    expect(booking.depositpaid).toBe(requestBody.depositpaid);

    const bookingdates = booking.bookingdates;
    expect(bookingdates.checkin).toBe(requestBody.bookingdates.checkin);
    expect(bookingdates.checkout).toBe(requestBody.bookingdates.checkout);
  });
});
```

通过在 beforeEach 块中使用这些函数,我能够添加额外的测试并为每个想要编写的测试获得新的请求体数据和可用的入住日期。实际的 POST 请求测试将使用完整的请求体创建一个新预订(包括必需和可选参数),注意这个 API 调用不需要身份验证,所以没有传递头部信息,我传入了通过 `createRandomDataBody()` 函数生成的 `requestBody`。

我们以这种方式创建请求体的好处是(不是硬编码),现在我可以使用我们为 postBody 设置的变量和数据,并在我们的断言中使用它。

```javascript
// POST booking 响应体
{
  "bookingid": 2,
  "booking": {
    "bookingid": 2,
    "roomid": 1,
    "firstname": "Testy",
    "lastname": "McTesterSon",
    "depositpaid": true,
    "bookingdates": {
      "checkin": "2023-05-10",
      "checkout": "2023-05-11"
    }
  }
}
```

下面的断言顺序也与响应体相同,这是故意的,目的是保持组织性!注意在这个场景中,我取了 `body`,也就是完整的 JSON 响应,创建了一个新变量 `booking` 并用它进行断言。我喜欢这样做,因为它帮助我快速可视化我正在对预订对象进行断言,在那之下是 `bookingdates` 对象。对于小型 API 响应来说可能不是那么重要,但当你有一个包含 20-50 个项目的 JSON 对象的响应体,或者你想遍历对象数组时,你会非常高兴你遵循了这种模式。

```javascript
const body = await response.json();
expect(body.bookingid).toBeGreaterThan(1);

const booking = body.booking;
expect(booking.bookingid).toBe(body.bookingid);
expect(booking.roomid).toBe(requestBody.roomid);
expect(booking.firstname).toBe(requestBody.firstname);
expect(booking.lastname).toBe(requestBody.lastname);
expect(booking.depositpaid).toBe(requestBody.depositpaid);

const bookingdates = booking.bookingdates;
expect(bookingdates.checkin).toBe(requestBody.bookingdates.checkin);
expect(bookingdates.checkout).toBe(requestBody.bookingdates.checkout);
```

我们可以进一步添加测试,比如:

- 只使用必需输入的 POST 预订
- 缺少必需输入的 POST 预订
- 使用错误类型的 POST 预订("true" 而不是 true 或 "1" 而不是 1)
- 使用身份验证的 POST 预订,尽管不需要
- 与现有预订日期重叠的 POST 预订
- 使用过去日期的 POST 预订
- 等等...

但我们已经验证了具有这组参数的 api 正在按预期工作,所以让我们继续前进!

### DELETE 请求检查

对于这组检查,我再次使用了我创建的数据工厂函数 `createFutureBooking` 和 `auth` 来设置测试。注意我在 describe 块中创建了 let 变量,有些已经设置了值,有些将在 beforeAll (如果不改变)或 beforeEach 块中获得它们的值,beforeEach 块将在每次测试运行前为变量分配一个新值。我在这个测试中将 roomId 硬编码为 1,因为我知道系统会有它可用,但这是一个风险,因为有人可能会删除 roomId 1,在这种情况下,我需要创建一个房间,并为该房间创建一个预订来执行我们的删除预订测试。我包含的 3 个测试是:

- DELETE 特定房间 ID 的预订
- DELETE 不存在 ID 的预订
- 无身份验证的 DELETE 预订 ID

```javascript
import { test, expect } from "@playwright/test";
import { auth } from "../../lib/datafactory/auth";
import {
  getBookingSummary,
  createFutureBooking,
} from "../../lib/datafactory/booking";

test.describe("booking/{id} DELETE requests", async () => {
  let cookies;
  let bookingId;
  let roomId = 1;

  test.beforeAll(async () => {
    cookies = await auth("admin", "password");
  });

  test.beforeEach(async () => {
    let futureBooking = await createFutureBooking(roomId);
    bookingId = futureBooking.bookingid;
  });

  test("DELETE booking with specific room id:", async ({ request }) => {
    const response = await request.delete(`booking/${bookingId}`, {
      headers: { cookie: cookies },
    });

    expect(response.status()).toBe(202);

    const body = await response.text();
    expect(body).toBe("");

    const getBooking = await getBookingSummary(bookingId);
    expect(getBooking.bookings.length).toBe(0);
  });

  test("DELETE booking with an id that doesn't exist", async ({ request }) => {
    const response = await request.delete("booking/999999", {
      headers: { cookie: cookies },
    });

    expect(response.status()).toBe(404);

    const body = await response.text();
    expect(body).toBe("");
  });

  test("DELETE booking id without authentication", async ({ request }) => {
    const response = await request.delete(`booking/${bookingId}`);

    expect(response.status()).toBe(403);

    const body = await response.text();
    expect(body).toBe("");
  });
});
```

在第一个测试中,你可以看到我们首先在 beforeEach 块中创建一个预订,我们将传入删除方法的预订 ID 与头部一起使用,因为我们需要授权。这是我一直使用的另一种模式,我计划进行主要断言的任何 api 接口,总是将 `response` 变量分配给它。这为我们将来继续构建测试提供了优势。

```
const response = await request.delete(`booking/${bookingId}`, {
      headers: { cookie: cookies },
    });
```

对于这第一个测试,我进行了两个断言,一个是对 response.status() 的断言,另一个是期望 response.text() 为空字符串 ""。对我来说,我想进一步验证预订是否真的被删除了,所以我没有使用测试中的 playwright `request` 方法,而是创建了另一个数据工厂 `getBookingSummary(bookingId)`，它返回 GET booking/summary?roomid=${bookingId} 的响应体,我可以对其进行断言。在这种情况下,我想确保 bookings.length 为 0。

### PUT 请求检查

在下一节中,我保留了一些冗长的内容,即在每个测试部分中创建一个新的 putBody,有很多方法可以组织代码。我本可以像在发布新预订 api 接口上创建请求体那样将其抽象出来。在这种情况下,我希望非常清楚地传递了哪些信息,因为在我的一个测试中,我尝试在没有名字的情况下进行 PUT 请求。

我遵循的一个模式是,我在 describe 块中创建所有变量。这允许我在测试和测试步骤中访问这些变量以进行断言。目前我也硬编码了一些变量。我可以使用像 faker 这样的工具来使数据唯一,如果我这样做,我会在 beforeEach() 中设置变量,这样每个测试都会得到一个新名字。它看起来像这样:

```javascript

test.describe("booking/{id} PUT requests", async () => {
  let firstname;

  test.beforeEach(async ({ request }) => {
    firstname = faker.name.firstName()
    ...
  });
```

我正在进行的检查是:

- PUT 特定房间 ID 的预订 + 验证预订已更新
- 在 putBody 中没有 firstname 的 PUT 预订
- PUT 不存在 ID 的预订
- PUT ID 为文本的预订
- 使用无效身份验证的 PUT 预订 ID
- 无身份验证的 PUT 预订 ID
- 没有 put body 的 PUT 预订 ID

在我看来,这是一个更有趣的 api 接口,因为有很多不同的组合可以测试。

我想特别指出的一个地方是在第一个测试 `PUT booking with specific room id` 中,我使用 [test.step()](https://playwright.dev/docs/api/class-test#test-step) 方法来帮助拆分测试。在我的 test.step 中,我实际上使用了 `getBookingById()`,这是我创建的一个数据工厂方法,用于返回发送的预订 ID 的当前主体。💡 重要提示:如果你使用 test.step,确保在 test.step 前面使用 `await`,如果你像我第一次编写测试时那样错过了这一点,你会在试图弄清楚发生了什么时敲键盘。

对我来说,我发现我错过了 await 是因为我试图让 test.step 中的一个断言失败...我在测试中做不到,回到 Playwright 文档中发现了这个问题。

```javascript
await test.step("Verify booking was updated", async () => {
  const getBookingBody = await getBookingById(bookingId);
  expect(getBookingBody.bookingid).toBeGreaterThan(1);
  expect(getBookingBody.bookingid).toBe(bookingId);
  expect(getBookingBody.roomid).toBe(putBody.roomid);
  expect(getBookingBody.firstname).toBe(putBody.firstname);
  expect(getBookingBody.lastname).toBe(putBody.lastname);
  expect(getBookingBody.depositpaid).toBe(putBody.depositpaid);

  const getBookingDates = getBookingBody.bookingdates;
  expect(getBookingDates.checkin).toBe(putBody.bookingdates.checkin);
  expect(getBookingDates.checkout).toBe(putBody.bookingdates.checkout);
});
```

当我第一次为这些测试编写自动化时,我遇到了很多来自被测应用程序的 [409 错误消息](https://http.cat/409)。代码代表冲突。具体的冲突是围绕已经在使用的入住和退房日期,这导致我创建了使我们编写这些测试更容易的数据工厂方法。没有这些函数,我会在故障排除时花费大量时间手动更新日期,我们会有硬编码的数据,这最终会导致更多的 409 错误和测试的不一致性。

这些数据工厂方法允许我让测试独立于任何其他测试数据或测试创建它需要的数据。

> 你不应该依赖测试 1 来设置测试 2 的数据。这是一个陷阱!!

我特别为 `futureOpenCheckinDate()` 和 `createFutureBooking()` 感到自豪。我在下面包含了我为每个创建的 [js
doc](https://jsdoc.app/) 描述。(我刚刚了解到 jsdoc,我非常喜欢它!!!)

![图片 5](https://playwrightsolutions.com/content/images/2023/03/image-11.png)

futureOpenCheckinDate() jsdoc

![图片 6](https://playwrightsolutions.com/content/images/2023/03/image-12.png)

createFutureBooking() jsdoc

所有的 PUT 请求测试可以在下面找到。

```javascript
import { test, expect } from "@playwright/test";
import { auth } from "../../lib/datafactory/auth";
import {
  getBookingById,
  futureOpenCheckinDate,
  createFutureBooking,
} from "../../lib/datafactory/booking";
import { isValidDate, stringDateByDays } from "../../lib/helpers/date";

test.describe("booking/{id} PUT requests", async () => {
  let cookies;
  let bookingId;
  let roomId = 1;
  let firstname = "Happy";
  let lastname = "McPathy";
  let depositpaid = false;
  let email = "testy@mcpathyson.com";
  let phone = "5555555555555";
  let futureBooking;
  let futureCheckinDate;

  test.beforeAll(async () => {
    cookies = await auth("admin", "password");
  });

  test.beforeEach(async ({ request }) => {
    futureBooking = await createFutureBooking(roomId);
    bookingId = futureBooking.bookingid;
    futureCheckinDate = await futureOpenCheckinDate(roomId);
  });

  test(`PUT booking with specific room id`, async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      firstname: firstname,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };
    const response = await request.put(`booking/${bookingId}`, {
      headers: { cookie: cookies },
      data: putBody,
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.bookingid).toBeGreaterThan(1);

    const booking = body.booking;
    expect(booking.bookingid).toBe(bookingId);
    expect(booking.roomid).toBe(putBody.roomid);
    expect(booking.firstname).toBe(putBody.firstname);
    expect(booking.lastname).toBe(putBody.lastname);
    expect(booking.depositpaid).toBe(putBody.depositpaid);

    const bookingdates = booking.bookingdates;
    expect(bookingdates.checkin).toBe(putBody.bookingdates.checkin);
    expect(bookingdates.checkout).toBe(putBody.bookingdates.checkout);

    await test.step("Verify booking was updated", async () => {
      const getBookingBody = await getBookingById(bookingId);
      expect(getBookingBody.bookingid).toBeGreaterThan(1);
      expect(getBookingBody.bookingid).toBe(bookingId);
      expect(getBookingBody.roomid).toBe(putBody.roomid);
      expect(getBookingBody.firstname).toBe(putBody.firstname);
      expect(getBookingBody.lastname).toBe(putBody.lastname);
      expect(getBookingBody.depositpaid).toBe(putBody.depositpaid);

      const getBookingDates = getBookingBody.bookingdates;
      expect(getBookingDates.checkin).toBe(putBody.bookingdates.checkin);
      expect(getBookingDates.checkout).toBe(putBody.bookingdates.checkout);
    });
  });

  test("PUT booking without firstname in putBody", async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };
    const response = await request.put(`booking/${bookingId}`, {
      headers: { cookie: cookies },
      data: putBody,
    });

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.error).toBe("BAD_REQUEST");
    expect(body.errorCode).toBe(400);
    expect(body.errorMessage).toContain(
      "Validation failed for argument [0] in public org.springframework.http.ResponseEntity"
    );
    expect(body.fieldErrors[0]).toBe("Firstname should not be blank");
  });

  test("PUT booking with an id that doesn't exist", async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      firstname: firstname,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };

    const response = await request.delete("booking/999999", {
      headers: { cookie: cookies },
      data: putBody,
    });

    expect(response.status()).toBe(404);

    const body = await response.text();
    expect(body).toBe("");
  });

  test(`PUT booking id that is text`, async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      firstname: firstname,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };

    const response = await request.put(`booking/asdf`, {
      headers: { cookie: cookies },
      data: putBody,
    });

    expect(response.status()).toBe(404);

    const body = await response.json();
    expect(isValidDate(body.timestamp)).toBe(true);
    expect(body.status).toBe(404);
    expect(body.error).toBe("Not Found");
    expect(body.path).toBe("/booking/asdf");
  });

  test("PUT booking id with invalid authentication", async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      firstname: firstname,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };

    const response = await request.put(`booking/${bookingId}`, {
      headers: { cookie: "test" },
      data: putBody,
    });

    expect(response.status()).toBe(403);

    const body = await response.text();
    expect(body).toBe("");
  });

  test("PUT booking id without authentication", async ({ request }) => {
    let putBody = {
      bookingid: bookingId,
      roomid: roomId,
      firstname: firstname,
      lastname: lastname,
      depositpaid: depositpaid,
      email: email,
      phone: phone,
      bookingdates: {
        checkin: stringDateByDays(futureCheckinDate, 0),
        checkout: stringDateByDays(futureCheckinDate, 1),
      },
    };

    const response = await request.put(`booking/${bookingId}`, {
      data: putBody,
    });

    expect(response.status()).toBe(403);

    const body = await response.text();
    expect(body).toBe("");
  });

  test("PUT booking id without put body", async ({ request }) => {
    const response = await request.put(`booking/${bookingId}`, {
      headers: { cookie: cookies },
    });

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(isValidDate(body.timestamp)).toBe(true);
    expect(body.status).toBe(400);
    expect(body.error).toBe("Bad Request");
    expect(body.path).toBe(`/booking/${bookingId}`);
  });
});
```

我们总是可以添加更多的断言和检查,但现在我的信心已经提高,我觉得如果预订 api 接口引入任何重大变化,我们的自动化应该会提醒我们,这样我们就可以进行调查并探索更大的系统会受到怎样的影响。

总的来说,我们有 19 个检查,在我的本地机器上使用 4 个工作线程运行了 15.9 秒

![图片 7](https://playwrightsolutions.com/content/images/2023/03/image-13.png)

如果你读到这里,给自己一个 ⭐️,你应得的!

---

感谢阅读!如果你觉得这很有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我并让我知道,或考虑 [给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下面订阅。

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-2-adding-more-in-depth-checks/

Published Time: 2023-03-27T12:30:37.000Z
