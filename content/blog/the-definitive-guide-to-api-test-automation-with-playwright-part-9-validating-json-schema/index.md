+++
date = 2023-08-28
title = "The Definitive Guide to API Test Automation With Playwright: Part 9 - Validating JSON Schema"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Welcome back! In this weeks guide I'm going walk you through the tooling I use to help me create JSON schema snapshots, and asserting on those snapshots within Playwright API tests.

If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. For our examples we will use the playwright-api-test-demo repository linked below.

## What is JSON Schema?

> **JSON Schema** is a declarative language that allows you to **annotate** and **validate** JSON documents. - [json-schema.org](https://json-schema.org/)

This is different than OpenAPI spec but shares some similarities. I like to take a hands on approach when learning new things so let's dive right in.

For our testing I will capture the response body in json from the `booking/summary?roomid=1` test.

```json
{
  "bookings": [
    {
      "bookingDates": {
        "checkin": "2022-02-01",
        "checkout": "2022-02-05"
      }
    }
  ]
}
```

As you can see this is very basic information, I took this body and took it over to [https://www.jsonschema.net/app/schemas/329125](https://www.jsonschema.net/app/schemas/329125) with the following settings.

![Image 2](https://playwrightsolutions.com/content/images/2023/08/image-19.png)

And generated the following JSON schema

```json
{
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "type": "object",
  "required": ["bookings"],
  "properties": {
    "bookings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["bookingDates"],
        "properties": {
          "bookingDates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
              "checkin": {
                "type": "string"
              },
              "checkout": {
                "type": "string"
              }
            }
          }
        }
      }
    }
  }
}
```

As you can see the JSON schema give us all the information about the body that was received. This is a very simple example, as these can get very complex, especially using large response body where some values may be null while others are strings. What we will be using JSON schema for is validating that the snapshot we create and save actually matches our response body that we will convert to schema and then compare. To learn more about JSON Schema, check out the article below.

[JSON Schema](https://testerops.com/2023/03/13/json-schema-validation/)

## validateJsonSchema.ts

I won't walk through each section of this code, but I do use the below libraries for different needs. `genson-js` for creating the schema we save to a file in the `.api/...` directory, and `ajv` for converting and comparing the live response from a test to the snapshot. We also use playwright `expect` in order to get feedback within the test report if the assertion fails.

[ajv Another JSON Schema Validator](https://www.npmjs.com/package/ajv)

[genson-js](https://www.npmjs.com/package/genson-js)

```javascript
// lib/helpers/validateJsonSchema.ts

import { createJsonSchema } from "@helpers/schemaHelperFunctions";
import { expect } from "@playwright/test";
import Ajv from "ajv";

/**
 * Validates an object against a JSON schema.
 *
 * @param {string} fileName - The first part of the name of the JSON schema file. The full name will be `${fileName}_schema.json`.
 * @param {string} filePath - The path to the directory containing the JSON schema file.
 * @param {object} body - The object to validate against the JSON schema.
 * @param {boolean} [createSchema=false] - Whether to create the JSON schema if it doesn't exist.
 *
 * @example
 *    const body = await response.json();
 *
 *    // This will run the assertion against the existing schema file
 *    await validateJsonSchema("POST_booking", "booking", body);
 *
 *    // This will create or overwrite the schema file
 *    await validateJsonSchema("POST_booking", "booking", body, true);
 */
export async function validateJsonSchema(
  fileName: string,
  filePath: string,
  body: object,
  createSchema = false
) {
  const jsonName = fileName;
  const path = filePath;

  if (createSchema) {
    await createJsonSchema(jsonName, path, body);
  }

  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const existingSchema = require(`../../.api/${path}/${jsonName}_schema.json`);

  const ajv = new Ajv({ allErrors: false });
  const validate = ajv.compile(existingSchema);
  const validRes = validate(body);

  if (!validRes) {
    console.log(
      "SCHEMA ERRORS:",
      JSON.stringify(validate.errors),
      "\nRESPONSE BODY:",
      JSON.stringify(body)
    );
  }

  expect(validRes).toBe(true);
}
```

```javascript
// lib/helpers/schemaHelperFunctions.ts

import { createSchema } from "genson-js";
import * as fs from "fs/promises";

export async function createJsonSchema(
  name: string,
  path: string,
  json: object
) {
  const filePath = `./.api/${path}`;

  try {
    await fs.mkdir(filePath, { recursive: true });

    const schema = createSchema(json);
    const schemaString = JSON.stringify(schema, null, 2);
    const schemaName = `.api/${path}/${name}_schema.json`;

    await writeJsonFile(schemaName, schemaString);

    console.log("JSON Schema created and saved.");
  } catch (err) {
    console.error(err);
  }
}

async function writeJsonFile(location: string, data: string) {
  try {
    await fs.writeFile(location, data);
  } catch (err) {
    console.error(err);
  }
}
```

To actually use this functionality in a test you will first need to create a schema file. For our example we will use the `booking.get.spec.ts` file. Before we start asserting on an existing JSON schema snapshot, we will need to generate one. By Importing the helper and adding this line after assigning the `body` variable in the test, you will be able to generate a JSON schema snapshot file.

```javascript
await validateJsonSchema("GET_booking_summary", "booking", body, true);
```

The full test can be seen here

```javascript
// tests/booking/booking.get.spec.ts

//COVERAGE_TAG: GET /booking/summary

import { test, expect } from "@playwright/test";
import { isValidDate } from "@helpers/date";
import { createHeaders, createInvalidHeaders } from "@helpers/createHeaders";
import { validateJsonSchema } from "@helpers/validateJsonSchema";
import { addWarning } from "@helpers/warnings";

test.describe("booking/ GET requests", async () => {
  let headers;
  let invalidHeader;

  test.beforeAll(async () => {
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

    await validateJsonSchema("GET_booking_summary", "booking", body, true);
  });
});
```

The JSON schema file that gets created is below. If you compare this to the file we received from the online tool you will notice it is very similar.

```json
// .api/booking/GET_booking_summary_schema.json

{
  "type": "object",
  "properties": {
    "bookings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "bookingDates": {
            "type": "object",
            "properties": {
              "checkin": {
                "type": "string"
              },
              "checkout": {
                "type": "string"
              }
            },
            "required": ["checkin", "checkout"]
          }
        },
        "required": ["bookingDates"]
      }
    }
  },
  "required": ["bookings"]
}
```

Now that we have the JSON schema snapshot we will need to update our function removing `true` as the last passed in parameter. The only time you should use that in the future is if you need to generate a new snapshot if the response body has changed.

```javascript
await validateJsonSchema("GET_booking_summary", "booking", body);
```

Now we should be able to run the test and validate things pass! One thing I like to do when writing automation is making the test fail when it should fail. How can we really trust our tests if we aren't testing them? So for this example I will save a new variable from the `body`, response and modify it and pass it into the validateJsonSchema function.

```javascript
// tests/booking/booking.get.spec.ts

//COVERAGE_TAG: GET /booking/summary

import { test, expect } from "@playwright/test";
import { isValidDate } from "@helpers/date";
import { createHeaders, createInvalidHeaders } from "@helpers/createHeaders";
import { validateJsonSchema } from "@helpers/validateJsonSchema";
import { addWarning } from "@helpers/warnings";

test.describe("booking/ GET requests", async () => {
  let headers;
  let invalidHeader;

  test.beforeAll(async () => {
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

    const badBody = body;
    badBody.bookings[0].bookingDates.checkin = 1234567890;

    await validateJsonSchema("GET_booking_summary", "booking", badBody);
  });
});
```

When running the test in this state this is the failure. The highest level error tells us that the validateJsonSchema failed. When viewing the test or the console.log() of the test run you can see the reasons why.

![Image 9](https://playwrightsolutions.com/content/images/2023/08/image-20.png)

![Image 10](https://playwrightsolutions.com/content/images/2023/08/image-22.png)

The full error message is below, you can see we overwrote the `checkin` property with a `number` instead of an expected string in our test above. The validateJsonSchema failed because a `number` != `string`.

\[{"instancePath":"/bookings/0/bookingDates/**checkin**","schemaPath":"#/properties/bookings/items/properties/bookingDates/properties/**checkin**/**type**","keyword":"type","params":{"**type**":"**string**"},"message":"must be string"}\]

Hopefully you can see with that example how this can be a a really quick way to add some checks in place around JSON schema.

## Things to Look out For

The JSON schema comparison isn't perfect, and won't solve all your problems, but it should help give you some guard rails. Here are a few things to consider as you add these assertions to your project.

- Depending on your API, if responses allow both values or `null` this can cause issues. for example let's say you create your schema for a GET all rooms, while only 1 room exists, but in reality there may be 10-15 rooms that have been created by your automation, that may have a null value (which may be allowed). Your snapshot doesn't match reality and your test will fail. If you create a new snapshot with the 10-15 rooms that had different data, that may be a workaround. That or updating the snapshot manually.
- When new properties are added to your API response body, the snapshot will still pass, and you don't have any kind of alert/notice to investigate the new property. This may be something that can be overcome by updating the logic, but this is a risk I didn't plan on solving with this tool.
- If you commit the `createSchema=true` to your repo, your test isn't checking against the recorded snapshot, and it's in a bad state.  Luckily there is a workaround for that!

## Add an ESLing rule

If you followed the previous article we configured our project with ESLint and Husky for pre-commit hooks, if any of the linting from ESLint fails it will block you committing the code on your local machine. Knowing this I wanted to create a safeguard to prevent me from committing the `createSchema=true`.

In the below code snippet I've added a new custom rule for `no-restricted-syntax`. If you attempt to commit `validateJsonSchema(*,*,*,true)` the linter will block your commit and alert you to your mistake. Now I won't make that same mistake twice!

```javascript
// .eslintrc.cjs

/* eslint-env node */
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/stylistic",
    "prettier",
  ],
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  root: true,
  rules: {
    "no-console": 0,
    "no-restricted-syntax": [
      "error",
      {
        selector: "CallExpression[callee.property.name='only']",
        message: "We don't want to leave .only on our tests😱",
      },
      {
        selector:
          "CallExpression[callee.name='validateJsonSchema'][arguments.length!=3]",
        message: "We don't want to commit validateJsonSchema(*,*,*,true)😎",
      },
    ],
  },
};
```

Now if I attempt to commit with a `true` in `validateJsonSchema()` I will get an error shown below. This should help prevent mistakes!

![Image 11](https://playwrightsolutions.com/content/images/2023/08/image-27.png)

## Update your README.md

Be a good steward, and document how you expect the function to be used within your repo. My readme example is below.

### Json Schema

We generate json schemas with a `POST, PUT, PATCH and GET` test but not with a delete. To generate a json schema. An example of a test that generates a schema is below. It's best to follow the similar naming conventions

```javascript
// Creates a snapshot of the schema and save to .api/booking/POST_booking_schema.json
await validateJsonSchema("POST_booking", "booking", body, true);

// Asserts that the body matches the snapshot found at .api/booking/POST_booking_schema.json
await validateJsonSchema("POST_booking", "booking", body);
```

Example of how this is used in a test:

```javascript
import { test, expect } from "@playwright/test";
import { validateJsonSchema } from "@helpers/validateJsonSchema";

test.describe("booking/ POST requests", async () => {
  test("POST new booking with full body", async ({ request }) => {
    const response = await request.post("booking/", {
      data: requestBody,
    });

    expect(response.status()).toBe(201);
    const body = await response.json();
    await validateJsonSchema("POST_booking", "booking", body);
  });
});
```

## Updating a test to not be flaky

The spec that was flaky was the `tests/booking/booking.put.spec.ts` specifically the first test. The main issue is we hard coded the `roomid` as 1, which is a room that is a part of the seed data. The problem with this is to be able to make a `PUT` request to a booking we have to create a booking. When using `roomid` as 1, there are other tests that use `roomid` 1 creating data, so when we attempt to get a future booking date, there is another tests getting a similar booking date, and I would get a `409` response letting me know there was a conflict, another booking was already booked for that time slot. With the built in retries in Playwright it would pass the 2nd time it ran most of the time, but we can easily refactor it to not be flaky at all.

```javascript
// tests/booking/booking.put.spec.ts

//COVERAGE_TAG: PUT /booking/{id}

import { test, expect } from "@playwright/test";
import {
  getBookingById,
  futureOpenCheckinDate,
  createFutureBooking,
} from "@datafactory/booking";
import { isValidDate, stringDateByDays } from "@helpers/date";
import { createHeaders, createInvalidHeaders } from "@helpers/createHeaders";
import { createRoom } from "@datafactory/room";
import { validateJsonSchema } from "@helpers/validateJsonSchema";

test.describe("booking/{id} PUT requests", async () => {
  let headers;
  let invalidHeader;
  let bookingId;
  let room;
  let roomId;
  const firstname = "Happy";
  const lastname = "McPathy";
  const depositpaid = false;
  const email = "testy@mcpathyson.com";
  const phone = "5555555555555";
  let futureBooking;
  let futureCheckinDate;

  test.beforeAll(async () => {
    headers = await createHeaders();
    invalidHeader = await createInvalidHeaders();
  });

  test.beforeEach(async () => {
    room = await createRoom("Flaky", 67);
    roomId = room.roomid;
    futureBooking = await createFutureBooking(roomId);
    bookingId = futureBooking.bookingid;
    futureCheckinDate = await futureOpenCheckinDate(roomId);
  });

  test(`PUT booking with specific room id`, async ({ request }) => {
    const putBody = {
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
      headers: headers,
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

    await validateJsonSchema("PUT_booking_id", "booking", body);

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
});
```

What was really nice about this change is I only had to add/update 4 lines of code.

- `import{createRoom}from"@datafactory/room"` importing the createRoom datafactory
- `let room;` and updated `let roomId;` within the describe block
- I updated the beforeEach block to have`room = await createRoom("Flaky", 67);` and then `roomId = room.roomid;`

Once this was updated, this spec is no longer flaky, because we are creating a room specifically for this tests, and not relying on static data, which was getting modified. Again, one of the hardest problems in test automation is TEST DATA!

## Warning Message Functionality

I won't cover this too much as there isn't quite a use case for this yet, but I did add the ability to create and send warning messages from within your tests, that can print out in the console after all your tests run.

![Image 12](https://playwrightsolutions.com/content/images/2023/08/image-23.png)

Below is an example how you could call this within a test. I've found this useful when you may want to notify your future self, without failing an actual test.

```
await addWarning("This test should be refactored: '" + test.info().title + "' to use custom assertions");
```

You can dig through the Pull Request and see the changes made with this article including the `addWarning()` function.

[Json schema by BMayhew](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/11)

## Final Notes

The way I a checking for JSON schema is 1 of many ways to accomplish this goal. The below article [Tim Deschryver](https://www.linkedin.com/in/tim-deschryver/) who has some great [Playwright content](https://timdeschryver.dev/blog?q=Playwright), walks us through how to validate using [zod](https://zod.dev/).

[Playwright API testing with zod](https://timdeschryver.dev/blog/playwright-api-testing-with-zod)

![Image 17](https://playwrightsolutions.com/content/images/2023/08/image-28.png)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-9-validating-json-schema/

Published Time: 2023-08-28T12:30:39.000Z
