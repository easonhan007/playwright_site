+++
date = 2023-08-14
title = "The Definitive Guide to API Test Automation With Playwright: Part 7 - Creating Helper Functions for Common tasks"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Welcome back as we continue our series on API Test Automation with Playwright! Today I'll walk through the changes made in the pull request, which include:

- Helper Functions
- Create Assertion Helper
- Update to Absolute paths instead of Relative paths
- branding, message, report, and room endpoint coverage to 100%

If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. The pull request with comments and code changes is listed below.

[adding additional coverage by BMayhew · Pull Request #9](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/9)

## Helper Functions

### Branding helper

There are two main helper functions that I created during my coding session. The first was `lib/helpers/branding.ts` which is just a variable export for a 2 different json objects to help with the branding api test. The below spec file found below handles both the GET and PUT api requests. The branding api handles what brand the website is using, for example name of the business, phone number, address, email, welcome photo, latitude, longitude, etc. Changing the branding will change the way the site renders, which is something to consider when it comes to the state of the website/api. If there are other tests that are expecting this branding information (which we will change with our `PUT` request) those tests will more than likely fail.

![Image 4](https://playwrightsolutions.com/content/images/2023/08/image-13.png)

With this context in mind, I made a choice to but both the `GET` and `PUT` tests within the same test file. With my current configuration, they will not run at the same time, even if I am running my tests in parallel. Notice I am importing `defaultBranding` and `updatedBranding` from the branding helper. One other thing to note with the `PUT` spec, I am utilizing an `afterEach` block where I update the branding to the default setting.

```javascript
// tests/branding/branding.spec.ts

//COVERAGE_TAG: GET /branding/
//COVERAGE_TAG: PUT /branding/

import { test, expect } from "@playwright/test";
import { defaultBranding, updatedBranding } from "@helpers/branding";
import { createHeaders } from "@helpers/createHeaders";

test.describe("branding/ GET requests", async () => {
  const defaultBody = defaultBranding;

  test("GET website branding", async ({ request }) => {
    const response = await request.get("branding");

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toEqual(defaultBody);
  });
});

// This test has the potential to cause other UI tests to fail as this branding endpoint is a critical part of the entire UI of the website
test.describe("branding/ PUT requests", async () => {
  const defaultBody = defaultBranding;
  const updatedBody = updatedBranding;
  let headers;

  test.beforeAll(async ({ request }) => {
    headers = await createHeaders();
  });

  test.afterEach(async ({ request }) => {
    await request.put("branding/", {
      headers: headers,
      data: defaultBody,
    });
  });

  test("PUT website branding", async ({ request }) => {
    const response = await request.put("branding/", {
      headers: headers,
      data: updatedBody,
    });

    expect(response.status()).toBe(202);
    const body = await response.json();
    expect(body).toEqual(updatedBody);
  });
});
```

For the helper file, I am keeping this very simple, I am exporting two variables as JSON objects that I can use for the api request body in my tests. I decided to hard code these values as there didn't seem like a lot of value to randomize the inputs here, as the branding information is likely not to change often once it's set.

```javascript
// lib/helpers/branding.ts

export const defaultBranding = {
  name: "Shady Meadows B&B",
  map: {
    latitude: 52.6351204,
    longitude: 1.2733774,
  },
  logoUrl: "https://www.mwtestconsultancy.co.uk/img/rbp-logo.png",
  description:
    "Welcome to Shady Meadows, a delightful Bed & Breakfast nestled in the hills on Newingtonfordburyshire. A place so beautiful you will never want to leave. All our rooms have comfortable beds and we provide breakfast from the locally sourced supermarket. It is a delightful place.",
  contact: {
    name: "Shady Meadows B&B",
    address: "The Old Farmhouse, Shady Street, Newfordburyshire, NE1 410S",
    phone: "012345678901",
    email: "fake@fakeemail.com",
  },
};

export const updatedBranding = {
  name: "Test Name",
  map: {
    latitude: 41.8781,
    longitude: 87.6298,
  },
  logoUrl: "https://media.tenor.com/KaCUHzQxVWcAAAAC/house.gif",
  description: "description",
  contact: {
    name: "Testy McTester",
    address: "100 Testing Way",
    phone: "5555555555",
    email: "testy@testymtesterface.com",
  },
};
```

### Room features helper

The rooms helper we have built has a bit more functionality. First off we do have a variable named `roomFeatures` which is an array of different types of features/test data that we will be using, a function that returns all room features, one that returns a random room feature, and one that will return X number of room features you pass into the function. Having these helpers makes it easy to quickly generate random data for our tests and allow me to simplify my datafactory methods.

```javascript
// lib/helpers/roomFeatures.ts

import { faker } from "@faker-js/faker";

const roomFeatures = [
  "TV",
  "WiFi",
  "Safe",
  "Mini Bar",
  "Tea/Coffee",
  "Balcony",
  "Bath",
  "Shower",
  "Sea View",
  "Mountain View",
  "City View",
  "River View",
  "Garden View",
  "Pool View",
  "Patio",
  "Terrace",
  "Air Conditioning",
  "Heating",
  "Kitchen",
  "Dining Area",
  "Sofa",
  "Fireplace",
  "Private Entrance",
  "Soundproofing",
  "Wardrobe",
  "Clothes Rack",
  "Ironing Facilities",
  "Desk",
  "Seating Area",
  "Sofa Bed",
];

export function allRoomFeatures() {
  return roomFeatures;
}

export function randomRoomFeatures() {
  return roomFeatures[
    faker.number.int({ min: 0, max: roomFeatures.length - 1 })
  ];
}

export function randomRoomFeaturesCount(count: number) {
  let features = [];

  for (let i = 0; i < count; i++) {
    features.push(randomRoomFeatures());
  }
  // This will remove all duplicates from the array
  return Array.from(new Set(features));
}
```

One of the specs that I've updated was the `room.put.spec.ts`, by adding a 2nd test utilizing the `randomRoomFeaturesCount()` function. Adding this spec was very easy, before I make a `PUT` call to the API endpoint, I create a variable `randomFeatures` with an array of 10 random room features, I then use the existing `updateRoomBody` (which gets set in the `beforeEach` block) and overwrite the values for the `features` with the 10 random room features. Then make the `PUT` api request, and validate the response of the features is the same as the `randomFeatures` variable we set earlier.

```javascript
// tests/room/room.put.spec.ts

//COVERAGE_TAG: PUT /room/{id}

import { createRoom, createRandomRoomBody } from "@datafactory/room";
import { createHeaders } from "@helpers/createHeaders";
import { randomRoomFeaturesCount } from "@helpers/roomFeatures";
import { test, expect } from "@playwright/test";

test.describe("room/ PUT requests", async () => {
  let room;
  let roomId;
  let authHeaders;
  let updateRoomBody;

  test.beforeEach(async ({}) => {
    room = await createRoom("PUT", 50);
    roomId = room.roomid;
    authHeaders = await createHeaders();
    updateRoomBody = await createRandomRoomBody();
  });

  test("PUT /room to update values", async ({ request }) => {
    const response = await request.put(`/room/${roomId}`, {
      headers: authHeaders,
      data: updateRoomBody,
    });

    expect(response.status()).toBe(202);
    const body = await response.json();

    expect(body.roomid).toEqual(roomId);
    expect(body.name).toEqual(updateRoomBody.name);
    expect(body.accessible).toEqual(updateRoomBody.accessible);
    expect(body.description).toEqual(updateRoomBody.description);
    expect(body.features).toEqual(updateRoomBody.features);
    expect(body.image).toEqual(updateRoomBody.image);
    expect(body.roomName).toEqual(updateRoomBody.roomName);
    expect(body.type).toEqual(updateRoomBody.type);
  });

  test("PUT /room to update features", async ({ request }) => {
    let randomFeatures = randomRoomFeaturesCount(10);

    // Overwrites the features array with random features
    updateRoomBody.features = randomFeatures;

    const response = await request.put(`/room/${roomId}`, {
      headers: authHeaders,
      data: updateRoomBody,
    });

    expect(response.status()).toBe(202);
    const body = await response.json();

    expect(body.roomid).toEqual(roomId);
    expect(body.name).toEqual(updateRoomBody.name);
    expect(body.accessible).toEqual(updateRoomBody.accessible);
    expect(body.description).toEqual(updateRoomBody.description);
    expect(body.features).toEqual(randomFeatures);
    expect(body.image).toEqual(updateRoomBody.image);
    expect(body.roomName).toEqual(updateRoomBody.roomName);
    expect(body.type).toEqual(updateRoomBody.type);
  });
});
```

I also simplified our `room` datafactory utilizing `randomRoomFeaturesCount()` function to create random room features. Now anytime a new room is created using `createRandomRoomBody()` there will be random features returned. If you follow along with the code you will see that I am actually setting a variable named `features` to `randomRoomFeaturesCount(6)`, and replace my hardcoded features list.

![Image 5](https://playwrightsolutions.com/content/images/2023/08/image-14.png)

```javascript
// lib/datafactory/room.ts

import { expect, request } from "@playwright/test";
import { faker } from "@faker-js/faker";
import { createHeaders } from "../helpers/createHeaders";
import { randomRoomFeaturesCount } from "@helpers/roomFeatures";

let url = process.env.URL || "https://automationintesting.online/";

export async function createRandomRoomBody(
  roomName?: string,
  roomPrice?: number
) {
  let roomType = ["Single", "Double", "Twin"];
  let features = randomRoomFeaturesCount(6);

  let roomBody = {
    roomName: roomName || faker.string.numeric(3),
    type: roomType[Math.floor(Math.random() * roomType.length)], // returns a random value from the array
    accessible: Math.random() < 0.5, //returns true or false
    image: faker.image.urlLoremFlickr({
      category: "cat",
      width: 500,
      height: 500,
    }),
    description: faker.hacker.phrase(),
    features: features.sort(() => 0.5 - Math.random()).slice(0, 3), // returns 3 random values from the array
    roomPrice: roomPrice || faker.string.numeric(3),
  };

  return roomBody;
}
```

## createAssertions()

The next helper to be discussed is `createAssertions()`. All the credit for this goes to [Sergei Gapanovich](https://www.linkedin.com/in/sgapanovich/) for the JS/TS implementation, and [Joel Black](https://www.linkedin.com/in/joel-black-1344a267/), for the O.G. Ruby implementation which I discussed in a [Ministry of Testing Test.Bash() talk](https://www.ministryoftesting.com/testbash-talks/1f8d5688?s_id=15535642).

![Image 6](https://playwrightsolutions.com/content/images/2023/08/image-15.png)

The helper code is below for our Playwright repo as an async function, that requires 2 parameters to be passed, first the body object and second a name for the object, typically "body" that the assertion builder will use.

🌮

Big thanks to [Dmitry Pakhilov](https://www.linkedin.com/in/pakhilov/) for a suggestion to simply the createAssertions.ts file by removing the index loop and using a for loop!

```javascript
// lib/helper/createAssertions.ts

/* eslint-disable @typescript-eslint/prefer-for-of */

/*
  this function logs in console ready to use expects
  example: passing the following object (body) to the function
  {
    "one": 1,
    "two": "2",
    "three": {
      "four": ["4", "cuatro"],
      "five": [
        {
          "six": []
        },
        {
          "seven": null
        }
      ]
    }
  }

  would generate the following ready to use assertions:

  expect(body.one).toBe(1);
  expect(body.two).toBe("2");
  expect(body.three.four).toEqual(["4","cuatro"]);
  expect(body.three.five[0].six).toEqual([]);
  expect(body.three.five[1].seven).toBe(null);
*/
export async function createAssertions(object: object, paramName = "body"): Promise<void> {
  for (const key in object) {
    const value = object[key];

    if (typeof value === "string") {
      console.log(`expect(${paramName}.${key}).toBe("${value}");`);
    } else if (value === null) {
      console.log(`expect(${paramName}.${key}).toBeNull();`);
    } else if (typeof value === "number") {
      console.log(`expect(${paramName}.${key}).toBe(${value});`);
    } else if (typeof value === "object") {
      if (Array.isArray(value)) {
        if (value.length === 0) {
          console.log(`expect(${paramName}.${key}).toEqual([]);`);
        } else if (typeof value[0] === "object") {
          createAssertions(value, `${paramName}.${key}`);
        } else {
          const newArray = value.map((item: string | number | null) =>
            typeof item === "string" ? `"${item}"` : (item as number)
          );
          console.log(`expect(${paramName}.${key}).toEqual([${newArray}]);`);
        }
      } else if (Object.keys(value).length === 0) {
        console.log(`expect(${paramName}.${key}).toEqual({});`);
      } else if (parseInt(key) >= 0) {
        createAssertions(value, `${paramName}[${key}]`);
      } else {
        createAssertions(value, `${paramName}.${key}`);
      }
    }
  }
}
```

So let's see this in action. I use the reports get spec to demonstrate how this works, the code is below the video walk through. When adding `await createAssertions(body, "body")` after we make an API call, we get a console.log message with our assertions. It is not a good idea to copy, paste, commit these assertions blindly, you will need to think through how best to modify the assertions to work for what you want to test for. For the spec below I used the expects to build out a for loop to do basic date validations and string validations as the data returned from this endpoint will never be consistent.

```javascript
// tests/reports/reports.get.spec.ts

//COVERAGE_TAG: GET /report/
//COVERAGE_TAG: GET /report/room/{id}

import { createFutureBooking } from "@datafactory/booking";
import { createRoom } from "@datafactory/room";
import { createAssertions } from "@helpers/createAssertions";
import { createHeaders } from "@helpers/createHeaders";
import { isValidDate } from "@helpers/date";
import { test, expect } from "@playwright/test";

test.describe("report/ GET requests", async () => {
  let headers;
  let room;

  test.beforeEach(async ({}) => {
    headers = await createHeaders();
    room = await createRoom();
    await createFutureBooking(room.roomid);
  });

  test("GET a report", async ({ request }) => {
    const response = await request.get("/report/", {
      headers: headers,
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.report.length).toBeGreaterThanOrEqual(1);

    // Leaving this here for demo purposes
    await createAssertions(body, "body");

    // I am asserting on each booking in the report array
    body.report.forEach((booking) => {
      expect(isValidDate(booking.start)).toBe(true);
      expect(isValidDate(booking.end)).toBe(true);
      expect(typeof booking.title).toBe("string");
    });
  });

  test("GET room report by id", async ({ request }) => {
    const response = await request.get(`/report/room/${room.roomid}`);

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.report.length).toBeGreaterThan(0);
    expect(isValidDate(body.report[0].start)).toBe(true);
    expect(isValidDate(body.report[0].end)).toBe(true);
    expect(body.report[0].title).toBe("Unavailable");
  });
});
```

This is a really useful tool and gets even more useful the larger the Body that is returned.

## Updating to Absolute paths

One quality of life change that I made with this pull request was update my imports to use Absolute paths. This is a feature that Typescript offers, and really makes the code look a lot cleaner.

![Image 7](https://playwrightsolutions.com/content/images/2023/08/image-16.png)

To enable this functionality I had to create a `tsconfig.json` file at my root directory, and use the compilerOptions > paths to allow absolute paths.  More details about path mapping can be found within the [docs](https://www.typescriptlang.org/docs/handbook/module-resolution.html#path-mapping).

```javascript
// tsconfig.json

{
  "compilerOptions": {
    "baseUrl": ".", // This must be specified if "paths" is.
    "paths": {
      "@datafactory/*": ["lib/datafactory/*"],
      "@helpers/*": ["lib/helpers/*"],
    }
  }
}
```

## Endpoint coverage to 100%

I was able to add coverage for all the rest of the endpoints. This did include branding, message, report, and room endpoints. The message endpoint also had a datafactory for `message` as well that is worth checking out on the [Pull Request](https://github.com/playwrightsolutions/playwright-api-test-demo/pulls).

![Image 8](https://playwrightsolutions.com/content/images/2023/08/image-17.png)

What's nice is if new endpoints get added to the existing areas our coverage percentage will drop and we can take action. If you need a refresher on how we built the endpoint coverage check out [Part 5 of the series](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-5-calculating-endpoint-coverage/). Also keep in mind, the 100% means we have at least 1 test per endpoint, not scenario that should be tested 😁.

The pull request can be found below with all the changes that were made this round.

[adding additional coverage by BMayhew · Pull Request #9 · playwrightsolutions/playwright-api-test-demo Summary by CodeRabbitNew Features: Added new modules for managing messages, room configurations, branding data, and room features.Enhanced booking.ts with updated faker methods for more realisti... ![Image 9](https://github.com/fluidicon.png)GitHubplaywrightsolutions ![Image 10](https://opengraph.githubassets.com/e92d1ed099daeb413e715cc56c0a7fd79bdaddd010666b77e0b0a5e382746859/playwrightsolutions/playwright-api-test-demo/pull/9)](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/9)

## Challenge for you!

One thing that I realize as I run my suite, there is 1 flaky test that will pass after a single retry, that can be refactored. If you are following along or want to test your skills, pull down the repo in its current state, and see if you can find a way to make the spec less flakey.

In light of reaching 100% coverage!

![Image 11](https://playwrightsolutions.com/content/images/2023/08/image-18.png)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-7-creating-helper-functions-for-common-tasks/

Published Time: 2023-08-14T12:30:25.000Z
