+++
date = 2023-09-18
title = "The Definitive Guide to API Test Automation With Playwright: Part 10 - Adding Unit Tests for Helpers"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Welcome back! In this weeks guide I'm going walk you through the a pull request that was made by a reader [Adam Pajda](https://www.linkedin.com/in/adam-pajda-b0ba03118/). He took some time and added unit tests around 4 different functions that I created through this series. For this article I will walk through the different code that was added and why.

If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. For our examples we will use the playwright-api-test-demo repository linked below.

All code that was added can be found in the pull request linked below.

[Add Unit Tests support for some helpers functions by pajdekPL](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/15)

## Installation and Docs

First off for unit testing [Jest](https://jestjs.io/) was the test framework of choice. A quote from the Jest documentation below.

> Jest is a delightful JavaScript Testing Framework with a focus on simplicity.

Jest is a very popular testing framework. In the early days of Playwright before there was a built in JS/TS test runner, Jest was a popular choice to implement.

[Jest](https://jestjs.io/)

To install Jest into your project use the command below to install jest, typescript, ts-jest, and @types/jest. this command will update your `package.json` file with the appopriate dependencies, so when you run install your dependencies `npm install` on other machines or in CI all the correct packages are installed.

```bash
npm i -D jest typescript ts-jest @types/jest
```

## Creating the Jest project

The command to initialize a `ts-jest` project is below.

```bash
npx ts-jest config:init
```

This command will create a file `jest.config.js`

```javascript
// What the init script creates

/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
};

// jest.config.ts

// Final edits to the config for our specific project

/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable no-undef */
const { pathsToModuleNameMapper } = require("ts-jest");
const { compilerOptions } = require("./tsconfig");

/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: "ts-jest",
  //Below lines are added to make it possible to use paths from the tsconfig.json file in UTs
  modulePaths: [compilerOptions.baseUrl],
  moduleNameMapper: pathsToModuleNameMapper(compilerOptions.paths),
  roots: ["lib"],
};
```

With the final config we add some ESLint disable sections, and we also make it possible to utilize the paths we setup in the `tsconfig.json` file.

## Writing the unit tests

The unit tests we will add are around the helper functions

- `createAssertions`
- `createHeaders`
- `schemaHelperFunctions`

I didn't write these unit tests, but I was able to follow through each one and understand what is being checked.

### Create Assertions Tests

Within this test, there is a single test case that checks if calling the `createAssertions` function has the proper output when passing in a complex json object (which would typically be a response body) into the function.

```javascript
// lib/helpers/tests/createAssertions.test.ts

import { createAssertions } from "@helpers/createAssertions";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const log = jest.spyOn(console, "log").mockImplementation(() => {});

describe("createAssertions", () => {
  test("createAssertions logs proper assertions to console", async () => {
    const input = {
      one: 1,
      two: "2",
      three: {
        four: ["4", "cuatro"],
        five: [
          {
            six: [],
          },
          {
            seven: null,
          },
        ],
      },
    };
    const expectedLogConsoleCalls = [
      ["expect(body.one).toBe(1);"],
      ['expect(body.two).toBe("2");'],
      ['expect(body.three.four).toEqual(["4","cuatro"]);'],
      ["expect(body.three.five[0].six).toEqual([]);"],
      ["expect(body.three.five[1].seven).toBeNull();"],
    ];

    await createAssertions(input);

    expect(log.mock.calls).toEqual(expectedLogConsoleCalls);
  });
});
```

The next set of tests is exercising the `createHeaders` and `createInvalidHeaders` functions. It also mocks external dependencies such as `Env` and `createCookies`.

The first test ensures that `createHeaders` returns the expected header when provided with a token. The second test verifies that `createHeaders` correctly calls `createCookies` with credentials from `Env` when no token is given. Lastly, there's a test to confirm that `createInvalidHeaders` generates a header with an invalid cookie. There is a heavy use of `jest.mock()`, which you can read more about in the [Jest Documentation](https://jestjs.io/docs/mock-functions#mocking-modules).

```javascript
// lib/helpers/tests/createHeaders.test.ts

import { createHeaders, createInvalidHeaders } from "@helpers/createHeaders";
import { createCookies } from "@datafactory/auth";
import Env from "@helpers/env";

jest.mock("@helpers/env", () => ({
  __esModule: true,
  default: {
    URL: "MockedUrl",
    ADMIN_NAME: "MockedAdminName",
    ADMIN_PASSWORD: "MockedAdminPassword",
    SECRET_API_KEY: "MockedSecretApiKey",
  },
  namedExport: jest.fn(),
}));
jest.mock("@datafactory/auth");

describe("createHeaders", () => {
  test("createHeaders return header with given token", async () => {
    const input = "mockedToken";
    const expected = {
      cookie: `token=${input}`,
    };

    const actual = await createHeaders(input);

    expect(actual).toEqual(expected);
  });
  test("createHeaders call createCookies with credentials from Env when token is not given", async () => {
    const createCookiesMock = jest.mocked(createCookies);
    createCookiesMock.mockResolvedValue("token=mockedToken");

    const expected = {
      cookie: `token=${"mockedToken"}`,
    };

    const actual = await createHeaders();

    expect(createCookies).toHaveBeenCalledWith(
      Env.ADMIN_NAME,
      Env.ADMIN_PASSWORD
    );
    expect(actual).toEqual(expected);
  });

  describe("createInvalidHeaders", () => {
    test("should return header with invalid cookie", async () => {
      const expected = {
        cookie: "cookie=invalid",
      };

      const actual = await createInvalidHeaders();

      expect(actual).toEqual(expected);
    });
  });
});
```

### Schema Helper Functions Tests

In this section we are actually creating 2 types of tests within two files. The first is an integration test, that tests more than one function. This test focuses on testing two functions: `writeJsonFile` and `createJsonSchema` from the `schemaHelperFunctions` module.

The `writeJsonFile` test ensures that the `writeJsonFile` function correctly writes data to the specified path, and it also cleans up the test file after the test.

The `createJsonSchema` test validates that the `createJsonSchema` function successfully creates and writes a new JSON schema file to a specific directory, verifying that the generated schema matches the expected schema structure. It also sets up and cleans up a test directory for this test.

```javascript
// lib/helpers/tests/schemaHelperFunctions.integration.test.ts

import {
  createJsonSchema,
  writeJsonFile,
} from "@helpers/schemaHelperFunctions";
import * as fs from "fs/promises";

describe("schemaHelperFunctions Integration Tests", () => {
  describe("writeJsonFile", () => {
    const inputFile = "lib/helpers/tests/fake.json";

    afterAll(() => {
      fs.unlink(inputFile);
    });

    test("writeJsonFile should write data properly to the given path", async () => {
      const mockedData = JSON.stringify({ some: "MockedField" });

      await writeJsonFile(inputFile, mockedData);

      const data = await fs.readFile(inputFile, { encoding: "utf8" });
      expect(data).toBe(mockedData);
    });
  });
  describe("createJsonSchema", () => {
    const endpointDir = "mocked_endpoint";
    const endpointFullPath = `.api/${endpointDir}`;
    const schemaName = "get_mocked";

    beforeAll(() => {
      fs.mkdir(endpointFullPath);
    });

    afterAll(() => {
      fs.rm(endpointFullPath, { recursive: true, force: true });
    });

    test("should create and write a new schema file to the endpoints directory", async () => {
      const endpointSchemaExpectedPath = `${endpointFullPath}/${schemaName}_schema.json`;
      const mockedData = { some: "MockedField" };
      const expected = {
        type: "object",
        properties: {
          some: {
            type: "string",
          },
        },
        required: ["some"],
      };

      await createJsonSchema(schemaName, endpointDir, mockedData);

      const data = await fs.readFile(endpointSchemaExpectedPath, {
        encoding: "utf8",
      });

      expect(JSON.parse(data)).toEqual(expected);
    });
  });
});
```

The second is test is a unit test that tests similar functions. In the first test the `writeJsonFile` function is exercised. The test ensures that `fs.writeFile` is called with the provided file path and data.

In the `createJsonSchema` test, it verifies that the `createJsonSchema` function utilizes the `createSchema` function from the "genson-js" library to create a schema based on provided data and then writes the resulting schema as JSON to a specified file path using `fs/promises`. Mocks are used to isolate these functions and capture their interactions.

```javascript
// lib/helpers/tests/schemaHelperFunctions.test.ts

import { createJsonSchema, writeJsonFile } from "@helpers/schemaHelperFunctions";
import * as fs from "fs/promises";
import { Schema, createSchema } from "genson-js";

jest.mock("fs/promises");
jest.mock("genson-js");

describe("schemaHelperFunctions", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe("writeJsonFile", () => {
    test("should call fs.writeFile with given filePath and Data", async () => {
      const inputFile = "mocked/input/path.json";
      const mockedData = JSON.stringify({ someMocked: "MockedField" });

      await writeJsonFile(inputFile, mockedData);

      expect(fs.writeFile).toBeCalledWith(inputFile, mockedData);
    });
  });
  describe("createJsonSchema", () => {
    const createSchemaMock = jest.mocked(createSchema);
    test("should create schema using createSchema from genson-js and write file using fs/promises", async () => {
      const endpointPath = "mocked_endpoint";
      const schemaFile = "get_mocked";
      const expectedFullPath = ".api/mocked_endpoint/get_mocked_schema.json";
      const mockedData = { someMocked: "MockedField" };
      const mockedSchema = {
        type: "object",
        properties: {
          someMocked: {
            type: "string",
          },
        },
        required: ["someMocked"],
      } as Schema;
      createSchemaMock.mockReturnValueOnce(mockedSchema);
      const expectedSchemaJsonContent = JSON.stringify(mockedSchema, null, 2);

      await createJsonSchema(schemaFile, endpointPath, mockedData);

      expect(createSchema).toBeCalledWith(mockedData);
      expect(fs.writeFile).toBeCalledWith(expectedFullPath, expectedSchemaJsonContent);
    });
  });
});
```

With the unit test additions [Adam Pajda](https://www.linkedin.com/in/adam-pajda-b0ba03118/) also refactored the `schemaHelperFunctions.ts` file with changes that can be found [here](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/15/files#diff-1d40a1077f0749978b82e2033fb3389bbca5703a748cf761e2084b68db110ef1). This included renaming one of my functions to make it more clear, and adding an export to one of the functions so the unit test could utilize the function in the test.

Running all the tests will give you the following output.

![Image 5](https://playwrightsolutions.com/content/images/2023/09/image-1.png)

## Updating your CI Pipeline

Don't forget to add a script in your `package.json` file so you can run `npm run ut` to run the jest tests.

```javascript
// package.json

...
  "scripts": {
    "ut": "jest --verbose",
    "test": "npx playwright test",
    "test:test": "test_env=test npx playwright test",
  ...
  },
...
```

Now you can go ahead and update your GitHub actions file so this command is run whenever we make a pull request as a part of our CI pipeline.

```yaml
// .github/workflows/run-playwright.yml
---
- name: Run lint
  run: npm run lint
- name: Run prettier
  run: npm run prettier
- name: Run UnitTests
  run: npm run ut
```

![Image 6](https://playwrightsolutions.com/content/images/2023/09/image.png)

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-10-adding-unit-tests-for-helpers/

Published Time: 2023-09-18T12:30:33.000Z
