+++
date = 2023-05-08
title = "The Definitive Guide to API Test Automation With Playwright: Part 4 - Handling Headers and Authentication"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

One of the first areas your likely to run into issues while writing automation for apis is around headers and authentication. I hope to share a few ways I've handled authentication and header management from my experiences, though there are many solutions to this problem. If you missed the [Introduction](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/), [Part 1](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-1-basics-of-api-testing-get/), [Part 2](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-2-adding-more-in-depth-checks/), or [Part 3](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-3-debugging-api-tests-with-vs-code/) I encourage you to check those out to get the context of where we are jumping in.

## Creating an auth.ts datafactory

My approach for the application we are testing [https://automationintesting.online/](https://automationintesting.online/) will likely differ from other sites, as they are all different. When dealing with the [auth endpoints](https://automationintesting.online/auth/swagger-ui/index.html), there are only 3 endpoints, an auth where you pass username and password, a validate where you pass in a token to ensure you are still logged in, and a logout endpoint to invalidate your session. With this site only having 1 login UN `admin` PW `password` we will take a simple approach.

I will start by creating an `auth.ts` datafactory file. I previously had created the `auth` async function that would return cookies to that would be added to the headers on each test. I've updates the functions name to `createCookies` and added jsdoc so that when using the function you can hover with some nice helper text of what the function does along with an example of how to use it. I've found that super helpful when working within the context of a team.

![Image 1](https://playwrightsolutions.com/content/images/2023/05/image-1.png)

As I also added a new async function named `createToken`. This function is very similar to create cookies in that it makes the same POST auth/login call but rather than returning all the cookies I only return the token. I needed this for some of the auth tests I've added during this round of updates.

```javascript
import { expect, request } from "@playwright/test";

let url = process.env.URL || "https://automationintesting.online/";
let cookies;

/**
   * Returns valid cookies for the given username and password.
   * If a username and password aren't provided "admin" and "password" will be used
   *
   * @example
   * import { createCookies } from "../datafactory/auth";
   *
   * const cookies = createCookies("Happy", "Mcpassword")
   *
   * const response = await request.put(`booking/${bookingId}`, {
      headers: { cookie: cookies },
      data: body,
    });
   */
export async function createCookies(username?: string, password?: string) {
  if (!username) {
    username = "admin";
  }
  if (!password) {
    password = "password";
  }

  const contextRequest = await request.newContext();
  const response = await contextRequest.post(url + "auth/login", {
    data: {
      username: username,
      password: password,
    },
  });

  expect(response.status()).toBe(200);
  const headers = response.headers();
  cookies = headers["set-cookie"];
  return cookies;
}

/**
   * Returns valid token for the given username and password.
   * If a username and password aren't provided "admin" and "password" will be used
   *
   * @example
   * import { createToken } from "../datafactory/auth";
   *
   * const token = createToken("Happy", "Mcpassword")
   *
   * const response = await request.post("auth/validate", {
      data: { token: token },
    });
   */
export async function createToken(username?: string, password?: string) {
  if (!username) {
    username = "admin";
  }
  if (!password) {
    password = "password";
  }

  const contextRequest = await request.newContext();
  const response = await contextRequest.post(url + "auth/login", {
    data: {
      username: username,
      password: password,
    },
  });

  expect(response.status()).toBe(200);
  const headers = response.headers();
  let tokenString = headers["set-cookie"].split(";")[0];
  let token = tokenString.split("=")[1];
  return token;
}
```

With the easy way to create cookies or a valid token we can start on abstracting away how we create headers. For this I created a `createHeaders.ts` helper. I chose to keep this as a helper as I am not interacting with the API directly within this file. Within this helper file I have 2 async functions `createHeaders()` and `createInvalidHeaders()`. These are basic examples, but this pattern can be used to create different types of headers based on what your system needs. For example if you needed to include an account id or api key in your headers you could build logic out in this file keeping your code [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).

```javascript
import { createCookies } from "../datafactory/auth";

let username = process.env.ADMIN_NAME;
let password = process.env.ADMIN_PASSWORD;

/**
 *
 * @param token a valid token to be used in the request if one is not provided cookies will be created from default username and password
 * @returns a header object with the token set as a cookie
 *
 * @example
 * import { createHeaders } from "../lib/helpers/createHeaders";
 *
 * const headers = await createHeaders(token);
 *     const response = await request.delete(`booking/${bookingId}`, {
      headers: headers,
    });
 *
 */
export async function createHeaders(token?) {
  let requestHeaders;

  if (token) {
    requestHeaders = {
      cookie: `token=${token}`,
    };
  } else {
    // Authenticate and get cookies
    let cookies = await createCookies(username, password);
    requestHeaders = {
      cookie: cookies,
    };
  }

  return requestHeaders;
}

/**
 *
 * @returns a header object with an invalid cookie used to test negative scenarios
 *
 * @example
 * import { createInvalidHeaders } from "../lib/helpers/createHeaders";
 *
 * const invalidHeader = await createInvalidHeaders();
 *     const response = await request.delete(`booking/${bookingId}`, {
      headers: invalidHeader,
    });
 *
 */
export async function createInvalidHeaders() {
  let requestHeaders = {
    cookie: "cookie=invalid",
  };

  return requestHeaders;
}
```

I've refactored all the areas in the spec files to include these methods in order to create the headers. To see the refactored files take a look at [the pull request](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/5/files).  Below is the GET examples that were updated. One thing to note is in may different tests creating the headers in the beforeAll() is typically ok, but it may make sense to create them in a beforeEach(). This will be determined by your tests, so don't blindly copy me, think through your needs.

```javascript
//COVERAGE_TAG: GET /booking/
//COVERAGE_TAG: GET /booking/{id}
//COVERAGE_TAG: GET /booking/summary

import { test, expect } from "@playwright/test";
import { isValidDate } from "../../lib/helpers/date";
import {
  createHeaders,
  createInvalidHeaders,
} from "../../lib/helpers/createHeaders";

test.describe("booking/ GET requests", async () => {
  let headers;
  let invalidHeader;

  test.beforeAll(async ({ request }) => {
    headers = await createHeaders();
    invalidHeader = await createInvalidHeaders();
  });

  test("GET booking summary with specific room id", async ({ request }) => {
    const response = await request.get("booking/summary?roomid=1");

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.bookings.length).toBeGreaterThanOrEqual(1);
    expect(isValidDate(body.bookings[0].bookingDates.checkin)).toBe(true);
    expect(isValidDate(body.bookings[0].bookingDates.checkout)).toBe(true);
  });

  test("GET booking summary with specific room id that doesn't exist", async ({
    request,
  }) => {
    const response = await request.get("booking/summary?roomid=999999");

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.bookings.length).toBe(0);
  });

  test("GET booking summary with specific room id that is empty", async ({
    request,
  }) => {
    const response = await request.get("booking/summary?roomid=");

    expect(response.status()).toBe(500);

    const body = await response.json();
    expect(isValidDate(body.timestamp)).toBe(true);
    expect(body.status).toBe(500);
    expect(body.error).toBe("Internal Server Error");
    expect(body.path).toBe("/booking/summary");
  });

  test("GET all bookings with details", async ({ request }) => {
    const response = await request.get("booking/", {
      headers: headers,
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

  test("GET all bookings with details with no authentication", async ({
    request,
  }) => {
    const response = await request.get("booking/", {
      headers: invalidHeader,
    });

    expect(response.status()).toBe(403);

    const body = await response.text();
    expect(body).toBe("");
  });

  test("GET booking by id with details", async ({ request }) => {
    const response = await request.get("booking/1", {
      headers: headers,
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

  test("GET booking by id that doesn't exist", async ({ request }) => {
    const response = await request.get("booking/999999", {
      headers: headers,
    });

    expect(response.status()).toBe(404);

    const body = await response.text();
    expect(body).toBe("");
  });

  test("GET booking by id without authentication", async ({ request }) => {
    const response = await request.get("booking/1");

    expect(response.status()).toBe(403);

    const body = await response.text();
    expect(body).toBe("");
  });
});
```

## Using storageState

One thing I didn't implement is the built in [storageState](https://playwright.dev/docs/auth#basic-shared-account-in-all-tests). I did create an [auth.setup.ts](https://github.com/playwrightsolutions/playwright-api-test-demo/blob/ced7d621f05a02b5cff4c9e1a31e1da7a405866f/tests/auth.setup.ts) file that utilized this but found that it didn't suite my needs. I left the file in there, and just commented out using this as the setup project. The reason it didn't work for me was because I include tests with invalid headers, and the storageState when setting up via `playwright.config.ts` makes all requests authenticated. This could be used with a bit more complexity importing different storageStates for each file/test, but I decided since I am creating headers just to handle that logic on my own.

Playwright also has the option to pass default http headers with every request using the extraHTTPHeaders within the `playwright.config.ts` file. An example below shows passing in `"playwright-solutions": "true"` as a header on every request. This can be really useful if you have a test header or default header you can pass in to bypass security rules in services as an example a CloudFlare WAF.

```javascript
import { defineConfig, devices } from "@playwright/test";
import { config } from "dotenv";

config();

export default defineConfig({
  projects: [
    { name: "setup", testMatch: /.*\overage.setup\.ts/ },
    {
      name: "api-checks",
      dependencies: ["setup"],
    },
  ],

  use: {
    extraHTTPHeaders: {
      "playwright-solutions": "true",
    },
    baseURL: process.env.URL,
    ignoreHTTPSErrors: true,
    trace: "on",
  },
  retries: 0,
  reporter: [["list"], ["html"]],
});
```

---

## Creating /auth API checks

With the creation of these new helpers I've gone ahead and added api test coverage for the [auth endpoints](https://automationintesting.online/auth/swagger-ui/index.html#/). The checks can be found in the [main repo under the tests/auth/](https://github.com/playwrightsolutions/playwright-api-test-demo/tree/main/tests/auth) directory. With this area of the system covered I now have high confidence as things change, logging in, logging out, and validating a token are working as expected. One thing to note with these examples, there was only 1 valid login I was testing with, typically when it comes to authorization I would also want to try test any different types of logins that are provided. For a more complex system I would recommend more checks.

Please do check out the repo below with all the code examples

[GitHub - playwrightsolutions/playwright-api-test-demo](https://github.com/playwrightsolutions/playwright-api-test-demo)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-4-handling-headers-and-authentication/

Published Time: 2023-05-08T04:22:16.000Z
