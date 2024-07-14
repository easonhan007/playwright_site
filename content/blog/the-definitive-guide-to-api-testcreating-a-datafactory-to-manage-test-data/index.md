+++
date = 2023-07-10
title = "The Definitive Guide to API Test Automation With Playwright: Part 6 - Creating a DataFactory to Manage Test Data"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

I believe the hardest thing about Test Automation is creating and managing test data and system state. Today's guide we are going to walk through how I typically tackle the test data problem in my test automation projects. Keep in mind there are multiple ways to solve this problem. If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. For our examples we will use the playwright-api-test-demo repository linked below.

[GitHub](https://github.com/playwrightsolutions/playwright-api-test-demo)

While working through this article I posted this online to get feedback from others. Most of the responses were around solving the problem. The answers included using faker library, using SQL or graphQL to create the data you need in your data storage within your tests, and using scrambled production data. Another response was 'State' being the hardest problem in automation. I think that is the most correct answer, as data makes up what state the application is in, though you could argue that some applications use data to store the state of the application. (If you're not following [@FriendlyTester](https://twitter.com/FriendlyTester) on twitter you should be)

> I would say State. But test data makes up a big part of that
>
> — Richard Bradshaw 🇺🇦 (@FriendlyTester) [July 1, 2023](https://twitter.com/FriendlyTester/status/1675281540496912389?ref_src=twsrc%5Etfw)

## Defining Static Test Data

For the application we are testing (specifically the API), there are a few things to know before we get into my implementation. First the application defaults deletes any test data and re-seeds the database with a minimal amount of test data. For test data that I always expect to exist, I like to refer to this as static test data. This is data that I may hard code in a specific test or set of tests, and always rely it will be there. The rules I put around this data are, automation tests shouldn't modify this data and users of the system shouldn't modify the data. Enforcing this can be very difficult, which leads me to relying on this strategy for all my data. I typically only use static data when I am doing a POC proof of concept examples, at the beginning of an automation project with the goal of refactor to use generated data, or for high level objects that may only be created once (think highest level account or api keys).

I won't be covering creating test data in xlsx, csv, or json files. I really look at this as a form of static test data, that may live within your automation repo that you create or assert with from existing files.

## Creating a Fake Random Data

The other option you have rather than creating static data is to create random data while the tests run for your testing needs. The tool I tend to use for this is `@faker-js/faker`. This library has been useful for all my needs!

[@faker-js](https://www.npmjs.com/package/@faker-js/faker)

The usage guide can be found here

[Usage | Faker Generate massive amounts of fake (but reasonable) data for testing and development.](https://fakerjs.dev/guide/usage.html)

```javascript
import { faker } from "@faker-js/faker";

const randomName = faker.person.fullName(); // Rowan Nikolaus
const randomEmail = faker.internet.email(); // Kassandra.Haley@erich.biz
```

## Creating a Datafactory

Now that we have a way to create random data, we need to find a way to structure this within our Playwright project. For this I will start by creating a `/lib` folder within that folder we'll create a `/datafactory` folder. I'll use this folder for any files that directly interact with the system either via `SQL` or `API` request in order to create test data. I use the `/helpers` folder to store any helper functions that help arrange test data, or may even call a data factory method to create test data. An example of that would be the `createHeaders.ts` file which was covered in [part 4](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-4-handling-headers-and-authentication/) of the series.

![Image 8](https://playwrightsolutions.com/content/images/2023/07/image-4.png)

## Auth Datafactory

The `createHeaders.ts` helper file imports the `createCookies` function from the auth data factory file.

```javascript
// lib/helpers/createHeaders.ts

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
```

The `auth.ts` file uses playwright request method to make an api call to either `createCookies` or `createToken`. I created both of these based off of needs within the tests. In these examples I am using JSDoc to provide documentation that is easy to read while working within the codebase. One thing to note, when working with exported functions I don't have access to `baseURL` that Playwright provides within the test fixture, so I do have to set the URL. Another approach would be to create fixtures that could be used within a playwright test step, but I found this is easier for me to wrap my head around, and for new joiners within the team to comprehend. I'll leave creating fixtures for areas where I need to extend my framework rather than managing test data.

```javascript
// lib/datafactory/auth.ts

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

## Bookings Datafactory

Where this gets really interesting is when we start to solve harder `state` problems within our tests. For example, let's say I want to utilize static data, the room id 1 which exists as a part of the seeded data, and I want to write a test that exercises the `DELETE` `booking/{id}` endpoint. For this I first want to create a booking, and then use that id to delete the booking, and have some assertions on the response, which includes getting the booking summary to assert against. The spec can be seen below.

```javascript
// tests/booking/booking.delete.spec.ts

//COVERAGE_TAG: DELETE /booking/{id}

import { test, expect } from "@playwright/test";
import {
  getBookingSummary,
  createFutureBooking,
} from "../../lib/datafactory/booking";
import { createHeaders } from "../../lib/helpers/createHeaders";

test.describe("booking/{id} DELETE requests", async () => {
  let headers;
  let bookingId;
  let roomId = 1;

  test.beforeAll(async () => {
    headers = await createHeaders();
  });

  test.beforeEach(async () => {
    let futureBooking = await createFutureBooking(roomId);
    bookingId = futureBooking.bookingid;
  });

  test("DELETE booking with specific room id:", async ({ request }) => {
    const response = await request.delete(`booking/${bookingId}`, {
      headers: headers,
    });

    expect(response.status()).toBe(202);

    const body = await response.text();
    expect(body).toBe("");

    const getBooking = await getBookingSummary(bookingId);
    expect(getBooking.bookings.length).toBe(0);
  });
});
```

The two datafactory methods `getBookingSummary` and `createFutureBooking` both interact with the underlying api to either get or create test data. Let's first look at `getBookingSummary`.

```javascript
// lib/datafactory/bookings.ts

import { expect, request } from "@playwright/test";

let url = process.env.URL || "https://automationintesting.online/";

/**
 *
 * @param bookingId: number for the booking you want to see the summary of
 * @returns the body of the booking/summary?roomid=${bookingId} endpoint
 */
export async function getBookingSummary(bookingId: number) {
  const createRequestContext = await request.newContext();
  const response = await createRequestContext.get(
    url + `booking/summary?roomid=${bookingId}`
  );

  expect(response.status()).toBe(200);
  const body = await response.json();
  return body;
}
```

As you can see this exported function accepts a bookingId as an input, and makes a unauthenticated `GET` call to `booking/summary?roomid=${bookingId}`. It then makes a check to ensure the response code is 200 (success), and returns the body as a  json object. We can then use this in the assertion to ensure the length of the returned object which is a bookings array has a length of 0.  I abstracted this api call in the datafactory function that can be used for other similar needs. This was a simple example lets look at the `createFutureBooking` function.

```javascript
// lib/datafactory/bookings.ts

import { expect, request } from "@playwright/test";
import { stringDateByDays } from "../helpers/date";
import { faker } from "@faker-js/faker";
import { createHeaders } from "../helpers/createHeaders";

let url = process.env.URL || "https://automationintesting.online/";

/**
 * This function will create a booking with provided roomId and a checkinDate
 * A checkout date will be randomly generated between 1 and 4 days after the checkinDate
 *
 * @param roomId: number for the room to create a booking for
 * @returns the body of the booking just created
 *
 * This code is wrapped in an assert retry details can be found
 * https://playwright.dev/docs/test-assertions#retrying
 */
export async function createFutureBooking(roomId: number) {
  let body;
  await expect(async () => {
    let headers = await createHeaders();

    let futureCheckinDate = await futureOpenCheckinDate(roomId);
    let randBookingLength = faker.datatype.number({ min: 1, max: 4 });

    let checkInString = futureCheckinDate.toISOString().split("T")[0];
    let checkOutString = stringDateByDays(futureCheckinDate, randBookingLength);

    // console.log("booking length: " + randBookingLength);
    // console.log("checkin string: " + checkInString);
    // console.log("checkout string: " + checkOutString);

    bookingBody = {
      roomid: roomId,
      firstname: faker.name.firstName(),
      lastname: faker.name.lastName(),
      depositpaid: Math.random() < 0.5, //returns true or false
      email: faker.internet.email(),
      phone: faker.phone.number("###########"),
      bookingdates: {
        checkin: checkInString,
        checkout: checkOutString,
      },
    };

    const createRequestContext = await request.newContext();
    const response = await createRequestContext.post(url + "booking/", {
      headers: headers,
      data: bookingBody,
    });

    expect(response.status()).toBe(201);
    body = await response.json();
  }).toPass({
    intervals: [1_000, 2_000, 5_000],
    timeout: 20_000,
  });

  return body;
}
```

This function as you can see is a bit more complicated. When walking through the logic we see you first need to pass in a roomid and the function then:

- Creates valid headers via datafactory to make authenticated api calls
- Gets a valid available future checkin date from another datafactory method `futureOpenCheckinDate` that will be shown below in the whole booking.ts file
- Creates a random amount of days between 1-4 to create a booking length
- Sets checkin and checkout date string calculated from the previous two steps
- Then use the faker library to build a booking body with fake data and checkin dates from previous steps
- Then make an `POST` call with the body we built above to `booking/` endpoint
- Then validate the response code is 200
- Then sets `body` variable to the response body in json format
- All the above steps are wrapped in a `[toPass()](https://playwright.dev/docs/test-assertions#expecttopass)` method which is a newer method built into Playwright that allows you to retry the block of code if any of the assertions failed. This is here because if I run my tests in parallel it's possible that the future date gets booked before the booking code runs resulting in `409` response codes.
- Finally the body is returned for the newly created booking.

This datafactory function allows me to quickly create booking to use in my checks. I've built them in a way that they are flexible and re-usable, abstracting away a lot of the heavy logic from my tests. The full `booking.ts` file can be found below, there are some other methods we won't be specifically covering in this article but are used within my test suite.

```javascript
// lib/datafactory/booking.ts

import { expect, request } from "@playwright/test";
import { stringDateByDays } from "../helpers/date";
import { faker } from "@faker-js/faker";
import { createHeaders } from "../helpers/createHeaders";

let url = process.env.URL || "https://automationintesting.online/";
let bookingBody;
let checkOutArray;

export async function createRandomBookingBody(
  roomId: number,
  checkInString: string,
  checkOutString: string
) {
  let bookingBody = {
    roomid: roomId,
    firstname: faker.name.firstName(),
    lastname: faker.name.lastName(),
    depositpaid: Math.random() < 0.5, //returns true or false
    email: faker.internet.email(),
    phone: faker.phone.number("###########"),
    bookingdates: {
      checkin: checkInString,
      checkout: checkOutString,
    },
  };
  return bookingBody;
}

/**
 * This function will create a booking with provided roomId and a checkinDate
 * A checkout date will be randomly generated between 1 and 4 days after the checkinDate
 *
 * @param roomId: number for the room to create a booking for
 * @returns the body of the booking just created
 *
 * This code is wrapped in an assert retry details can be found
 * https://playwright.dev/docs/test-assertions#retrying
 */
export async function createFutureBooking(roomId: number) {
  let body;
  await expect(async () => {
    let headers = await createHeaders();

    let futureCheckinDate = await futureOpenCheckinDate(roomId);
    let randBookingLength = faker.datatype.number({ min: 1, max: 4 });

    let checkInString = futureCheckinDate.toISOString().split("T")[0];
    let checkOutString = stringDateByDays(futureCheckinDate, randBookingLength);

    // console.log("booking length: " + randBookingLength);
    // console.log("checkin string: " + checkInString);
    // console.log("checkout string: " + checkOutString);

    bookingBody = {
      roomid: roomId,
      firstname: faker.name.firstName(),
      lastname: faker.name.lastName(),
      depositpaid: Math.random() < 0.5, //returns true or false
      email: faker.internet.email(),
      phone: faker.phone.number("###########"),
      bookingdates: {
        checkin: checkInString,
        checkout: checkOutString,
      },
    };

    const createRequestContext = await request.newContext();
    const response = await createRequestContext.post(url + "booking/", {
      headers: headers,
      data: bookingBody,
    });

    expect(response.status()).toBe(201);
    body = await response.json();
  }).toPass({
    intervals: [1_000, 2_000, 5_000],
    timeout: 20_000,
  });

  return body;
}

/**
 * This function will return all the bookings for a roomId
 *
 * @param roomId: number for the room you want to get the bookings for
 * @returns the body of the bookings for the room
 */
export async function getBookings(roomId: number) {
  let headers = await createHeaders();

  const createRequestContext = await request.newContext();
  const response = await createRequestContext.get(
    url + "booking/?roomid=" + roomId,
    {
      headers: headers,
    }
  );

  expect(response.status()).toBe(200);
  const body = await response.json();
  // console.log(JSON.stringify(body));
  return body;
}

/**
 *
 * @param bookingId: number for the booking you want to see the summary of
 * @returns the body of the booking/summary?roomid=${bookingId} endpoint
 */
export async function getBookingSummary(bookingId: number) {
  const createRequestContext = await request.newContext();
  const response = await createRequestContext.get(
    url + `booking/summary?roomid=${bookingId}`
  );

  expect(response.status()).toBe(200);
  const body = await response.json();
  return body;
}

/**
 *
 * @param bookingId number for the booking you want to see the details of
 * @returns the body of the booking/${bookingId} endpoint
 */
export async function getBookingById(bookingId: number) {
  let headers = await createHeaders();

  const createRequestContext = await request.newContext();
  const response = await createRequestContext.get(
    url + `booking/${bookingId}`,
    {
      headers: headers,
    }
  );

  expect(response.status()).toBe(200);
  const body = await response.json();
  return body;
}

/**
 *
 * @param roomId
 * @returns the most future checkout date for a room
 * @example
 *
 *  let futureCheckinDate = await futureOpenCheckinDate(roomId);        // "2023-03-31T00:00:00.000Z"
 *  let checkInString = futureCheckinDate.toISOString().split("T")[0];  // "2023-03-31"
 *  let checkOutString = stringDateByDays(futureCheckinDate, 2);        // "2023-04-02"
 */
export async function futureOpenCheckinDate(roomId: number) {
  let currentBookings = await getBookings(roomId);

  checkOutArray = new Array();

  // Iterate through current bookings and get checkout dates
  for (let i = 0; i < (await currentBookings.bookings.length); i++) {
    let today = new Date();
    let checkOut = new Date(currentBookings.bookings[i].bookingdates.checkout);

    if (today < checkOut) {
      // pushing the checkout date into an array
      checkOutArray.push(checkOut);
    }
  }

  // Find the most future checkout date and return it if no future dates exist return today
  let mostFutureDate =
    checkOutArray
      .sort(function (a, b) {
        return a - b;
      })
      .pop() || new Date();

  // console.log("Last Checkout Date: " + mostFutureDate);
  return mostFutureDate;
}
```

## Adding a Room Datafactory

Now that we have a way to quickly create bookings for any room, we still have a data problem in one of our earlier tests. `POST new booking with full body` from the `POST` `booking/` endpoint. This test would sometimes pass and sometimes fail due to an error trying to book the hardcoded roomid=1. Let's go ahead and build a datafactory function that will create a new room for this test and implement it.

The first thing I did was use the `POST` `room/` endpoint in the VS Code Thunder API client, while using the [swagger page](https://automationintesting.online/room/swagger-ui/index.html#/) to understand more about how the endpoint requirements. The first thing I noticed is we do need a valid cookie, so this will be an authenticated request. The 2nd thing after making a `POST` request is that the example `POST` body that was given as an example includes roomid, but it looks like that is a value set by the application, not something that can be set from the api request. This seems like a bug in the application is any value I add to roomid it never gets used, and always gets overwritten to a new unused sequential value from the system under test.

```javascript
{
  "roomid": 0,
  "roomName": "string",
  "type": "Suite",
  "accessible": true,
  "image": "string",
  "description": "string",
  "features": [
    "string"
  ],
  "roomPrice": 999
}
```

![Image 9](https://playwrightsolutions.com/content/images/2023/07/image-5.png)

Example of request body | response

Knowing this I decided to leave out the `roomid` as a field that I pass in via the `POST` body. Below is the full `room.ts` datafactory file. It includes 2 exported functions. The first to `createRandomRoomBody()`, with two optional parameters, `roomName` and `roomPrice`. This is used by the 2nd function `createRoom()`. With these datafactory functions we can now implement them within the `POST new booking spec`

```javascript
// lib/datafactory/room.ts

import { expect, request } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { createHeaders } from "../helpers/createHeaders";

let url = process.env.URL || "https://automationintesting.online/";

export async function createRandomRoomBody(
  roomName?: string,
  roomPrice?: number
) {
  let roomType = ["Single", "Double", "Twin"];
  let features = ["TV", "WiFi", "Safe", "Mini Bar", "Tea/Coffee", "Balcony"];

  let roomBody = {
    roomName: roomName || faker.random.numeric(3),
    type: roomType[Math.floor(Math.random() * roomType.length)], // returns a random value from the array
    accessible: Math.random() < 0.5, //returns true or false
    image: faker.image.imageUrl(500, 500, "cat", true),
    description: faker.hacker.phrase(),
    features: features.sort(() => 0.5 - Math.random()).slice(0, 3), // returns 3 random values from the array
    roomPrice: roomPrice || faker.random.numeric(3),
  };

  return roomBody;
}

/**
 * This function will create a room with provided name and a price
 *
 * @param roomName: string for the room to create
 * @param roomPrice: number for the price of the room
 * @returns the body of the room just created with a unique roomid in the response
 *
 * @example
 * let room = await createRoom("My Room", 100);
 * let roomId = room.roomid;
 */
export async function createRoom(roomName?: string, roomPrice?: number) {
  let body;
  let headers = await createHeaders();

  let roomBody = await createRandomRoomBody(roomName, roomPrice);

  const createRequestContext = await request.newContext();
  const response = await createRequestContext.post(url + "room/", {
    headers: headers,
    data: roomBody,
  });

  expect(response.status()).toBe(201);
  body = await response.json();

  return body;
}
```

Using the image below you can see the refactor to the test with the datafactory already built only took 4 lines of code to be modified. We removed the hardcoded value and then set the roomId to the newly created `roomid` that was created by the datafactory.

![Image 10](https://playwrightsolutions.com/content/images/2023/07/image-6.png)

Now that I have the room datafactory I could refactor all of my tests very quickly to always create it's own data.

## Abstractions are Fun!

Really all we've done through the datafactory is added a layer of [abstraction](https://stackify.com/oop-concept-abstraction/), making are tests more readable, and building functions that can be used over and over again throughout our API tests. An abstractions is a core principle of [Object Oriented Programming](<https://www.techtarget.com/searchapparchitecture/definition/object-oriented-programming-OOP#:~:text=Object%2Doriented%20programming%20(OOP)%20is%20a%20computer%20programming%20model,has%20unique%20attributes%20and%20behavior.>).

![Image 11](https://playwrightsolutions.com/content/images/2023/07/ezgif.com-optimize.gif)

The pull request for these changes can be found below

[adding a rooms datafactory and updating booking post spec by BMayhew · Pull Request #7](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/7)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-testcreating-a-datafactory-to-manage-test-data/

Published Time: 2023-07-10T12:30:12.000Z
