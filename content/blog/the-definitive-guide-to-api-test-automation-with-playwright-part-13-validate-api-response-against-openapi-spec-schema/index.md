+++
date = 2023-10-09
title = "The Definitive Guide to API Test Automation With Playwright: Part 13 - Validate API Response Against OpenAPI Spec Schema"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Welcome back, this week we'll look at how to validate the api response body from the schema against the OpenAPI spec schema. This is a more complex solution than we covered in the previous article below. In that article we walked through taking a snapshot of the response, converting it into a JSON schema and saving the results as a part of the repository. This article will take the downloaded OpenAPI spec files that we download when we calculate coverage, and use the spec to validate each field that is returned in the response body. I'll also go ahead and mention a lot of the  ideas were originally from [Sergei Gapanovich](https://playwrightsolutions.com/author/sergei/), and were implemented against our test repo at work.

[The Definitive Guide to API Test Automation With Playwright: Part 9](https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-9-validating-json-schema/)

If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. For our examples we will use the playwright-api-test-demo repository linked below.

[GitHub - playwrightsolutions/playwright-api-test-demo](https://github.com/playwrightsolutions/playwright-api-test-demo)

## Breaking Down validateAgainstSchema() Function

Before I show off the code, I wanted to walk through what type of checks we are doing through the function. I'll attempt to explain it with the diagram below. Let's start by observing the `body.bookings[0]` is an javascript object with `bookingDates` which includes a checkin string and a checkout string. The red line indicates the shape of the object. The blue line indicates the name `BookingDates` schema in the booking_spec3.json file. The green line indicates we need to look in the `booking` schema file, as we have multiple schema files with this project, for other proejcts that only have 1 OpenApi spec file the code would need to be tweaked. The orange lines indicate how the javascript object matches up with the OpenApi spec file `booking_spec3.json`.

![Image 5](https://playwrightsolutions.com/content/images/2023/09/image-16.png)

## validateAgainstSchema() code

The code is for this function is below

```javascript
// lib/helpers/validateAgainstSchema.ts

import * as fs from "fs";
import { expect, test } from "@playwright/test";
import { removeItemsFromArray } from "@helpers/arrayFunctions";
import { capitalizeString } from "@helpers/capitalizeString";
import { fail } from "assert";
import { addWarning } from "@helpers/warnings";
import { authSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Auth";
import { bookingSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Booking";
import { brandingSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Branding";
import { messageSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Message";
import { reportSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Report";
import { roomSchemaExpectedResponseParamsCount } from "@helpers/schemaData/Room";
import { stringDateByDays } from "@helpers/date";

/**
 * `Definition:` Validates an **object** against a specified **schema object**
 * @param object - The object to check schemaObject against.
 * @param schemaObject - The schema object name as documented in *_spec3.json.
 * @param docs - The type of docs (e.g. `branding`, `message`, `booking`, etc).
 * @param notReturnedButInSchema - Any defined properties in schema but not returned by Falcon.
 * @param extraParamsReturned - Any undefined properties returned by Falcon; **_create a bug if there are any._**
 */
export async function validateAgainstSchema(
  object: object,
  schemaObject: string,
  docs: string,
  notReturnedButInSchema = [],
  extraParamsReturned = []
) {
  // get keys from the object
  let responseObjectKeys = Object.keys(object);

  // get keys from the docs
  const schema = await schemaParameters(schemaObject, docs);
  let docsObjectKeys = Object.keys(schema);

  /*
    if used - workaround around a bug
    this should not be ok when we have more params in a response than in docs

    filter out extra params from the response params array if any
  */
  if (extraParamsReturned.length > 0) {
    responseObjectKeys = removeItemsFromArray(
      responseObjectKeys,
      extraParamsReturned
    );
  }

  // filter out hidden params from the schema params array if any
  if (notReturnedButInSchema.length > 0) {
    docsObjectKeys = removeItemsFromArray(
      docsObjectKeys,
      notReturnedButInSchema
    );
  }

  // compare object keys (need to be sorted since order differs)
  expect(docsObjectKeys.sort()).toEqual(responseObjectKeys.sort());

  // add a warning if schema object length has been changed based on doc types
  let recordedSchemaResponseParamsCount;
  if (docs === "auth") {
    recordedSchemaResponseParamsCount = authSchemaExpectedResponseParamsCount;
  } else if (docs === "booking") {
    recordedSchemaResponseParamsCount =
      bookingSchemaExpectedResponseParamsCount;
  } else if (docs === "branding") {
    recordedSchemaResponseParamsCount =
      brandingSchemaExpectedResponseParamsCount;
  } else if (docs === "message") {
    recordedSchemaResponseParamsCount =
      messageSchemaExpectedResponseParamsCount;
  } else if (docs === "report") {
    recordedSchemaResponseParamsCount = reportSchemaExpectedResponseParamsCount;
  } else if (docs === "room") {
    recordedSchemaResponseParamsCount = roomSchemaExpectedResponseParamsCount;
  }

  if (
    docsObjectKeys.length !==
    recordedSchemaResponseParamsCount[schemaObject] -
      notReturnedButInSchema.length
  ) {
    addWarning(
      `'${schemaObject}' schema object in '${docs}' docs has been updated. Please, do the following: \n` +
        `- Check if the change is expected \n` +
        `- Update "${test.info().title}" test with appropriate assertions \n` +
        `- Re-run the test from terminal with 'GENERATE_SCHEMA_TRACKING_DATA=true', commit and push generated files \n\n`
    );
  }
}

export async function schemaParameters(schema: string, docs: string) {
  try {
    const apiDocs = JSON.parse(
      fs.readFileSync(`./${docs}_spec3.json`).toString("utf-8")
    );

    return apiDocs.components.schemas[schema].properties;
  } catch (e) {
    fail(
      `The '${schema}' object you passed does not exist in '${docs}' documentation`
    );
  }
}

export async function updateDocsSchemasParamsCount() {
  const allDocs = ["auth", "booking", "branding", "message", "report", "room"];

  allDocs.forEach((docs) => {
    const apiDocs = JSON.parse(
      fs.readFileSync(`./${docs}_spec3.json`).toString("utf-8")
    );
    const schemas = apiDocs.components.schemas;
    const schemaObjects = Object.keys(schemas);

    let data = "";
    data += "// updated on " + stringDateByDays() + "\n\n";
    data += `export const ${docs}SchemaExpectedResponseParamsCount = {\n`;
    schemaObjects.forEach((schema) => {
      data += `  ${schema}: ${
        Object.keys(schemas[schema].properties).length
      },\n`;
    });
    data += "};\n";

    try {
      fs.writeFileSync(
        `./lib/helpers/schemaData/${capitalizeString(docs)}.ts`,
        data
      );
    } catch (err) {
      console.error(err);
    }
  });
}
```

I won't walk through all the code for this but the JSDoc for the main function walks through the inputs needed. One thing that is worth calling out here, is with this type of Schema Verification is that when new items are added to the response and schema, you won't have any way of knowing about this programmatically. So we've added `updateDocsSchemasParamsCount()` function along with some static files that keep track of the different counts for the different json objects. When new objects are added

```javascript
// ./lib/helpers/schemaData/Booking.ts

// updated on 2023-09-23

export const bookingSchemaExpectedResponseParamsCount = {
  Error: 4,
  Booking: 8,
  BookingDates: 2,
  CreatedBooking: 2,
};
```

## Updating ExpectedResponseCount

To update the above numbers programmatically I've built the code so you can run the test with the environment variable `GENERATE_SCHEMA_TRACKING_DATA=true` to update tracking files. It will overwrite existing files but it's you who have to commit and push them to our repo.

## Warning.log

With this tracking we now have a way to notify if new items are added to a response body, and is a trigger for me to go and update our checks to assert against the new field. With that I have a `warning.log` from the `addWarning()` function that can get output to warn me of things, but not fail the test.

```
// warning.log

WARNING: 'BookingDates' schema object in 'booking' docs has been updated. Please, do the following:
- Check if the change is expected
- Update "GET booking summary with specific room id" test with appropriate assertions
- Re-run the test from terminal with 'GENERATE_SCHEMA_TRACKING_DATA=true', commit and push generated files


WARNING: This test should be refactored: 'GET booking summary with specific room id' to use custom assertions
```

## validateAgainstSchema() failure

An example of a failure would be if the OpenApi booking_spec.json was updated to be `checkindate` and `checkoutdate` rather than just `checkin` and `checkout`, the failure would look like. As the response body of the API still had `checkin` and `checkout`, this would cause the test to fail. Note we aren't doing any type checking here we are just validating that the shape of the response body matches the OpenApi spec file.

![Image 6](https://playwrightsolutions.com/content/images/2023/09/image-18.png)

As long as there are good assertions that validate the content of the message is a string in our other expects we should have the type checks included as a part of our assertions.

## Why implement this functionality?

The main reason we did at our workplace is we are working with really large API response bodies, and the jsonSchema snapshot testing required a good bit of upkeep. For example we had some fields that would respond with null or a string, and if the original response body, had just a string, the snapshot would always look for a string. To record new snapshots we would have to get both null and string responses for the snapshot to pass for all scenarios.

We also found that we didn't have a way to keep up with "change-detection". If new fields were added to a response body, we wanted to add assertions around those new fields, it was not easy to know about them. Now as long as our Open Api spec file is updated this new code will add a warning for us.

The pull request with the code changes can be found below.

[Bm/validate against schema by BMayhew](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/14/files)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-13-validate-api-response-against-openapi-spec-schema/

Published Time: 2023-10-09T12:30:25.000Z
