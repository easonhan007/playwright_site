+++
date = 2023-11-13
title = "The Definitive Guide to API Test Automation With Playwright: Part 15 - Adding Test Tags to Get Targeted Feedback"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

In this guide I'll cover how tags work, link to other articles where I discuss some tips on how to use tags, and show some code examples of the tags I like to use.

If you are just now joining us for the first time feel free to check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) and the [playwright-api-test-demo repository](https://github.com/playwrightsolutions/playwright-api-test-demo) which in which all code examples are included.

The main tags I typically add to a a project include:

- endpoints: `@auth`, `@booking`, `@branding`, `@message`, `@report`, `@room`
- happy path tests: `@happy`
- flaky tests:  `@unsatisfactory`

Of course you can add any type of tag you'd but these are typically the tags I've found useful for api automation suites. The official docs for tags can be found below.

[Annotations](https://playwright.dev/docs/test-annotations#tag-tests)

Here is an example of a spec with tags implemented. Note I have add the `@auth` tag in the describe block which is at the highest level. This will ensure that all specs within the describe block are run when running with the command `npx playwright tests --grep @auth`. As you see in the tests below I've also included the `@happy` tag in only 1 of the specs below. My thought around this decision is to ensure the happy path from the `auth/login` endpoint I really only want to make sure that I can log in successfully as it is a critical path when I run my happy path tests. The other checks though useful are less critical.

```javascript
// tests/auth/login.post.spec.ts

//COVERAGE_TAG: POST /auth/login

import { test, expect } from "@fixtures/fixtures";
import Env from "@helpers/env";

test.describe("auth/login POST requests @auth", async () => {
  ...
  test("POST with valid credentials @happy", async ({ request }) => {
    ...
  });

  test("POST with invalid username and password", async ({ request }) => {
    ...
  });

  test("POST with valid username and invalid password", async ({ request }) => {
    ...
  });

  test("POST with invalid username and valid password", async ({ request }) => {
    ...
  });

  test("POST with no username and valid password", async ({ request }) => {
    ...
  });

  test("POST with empty body", async ({ request }) => {
    ...
  });

  test("POST with no body", async ({ request }) => {
    ...
  });

  test("POST with valid credentials then validate with token @happy", async ({ request }) => {
    ...
  });
});
```

As a part of this exercise I went ahead and added a flakey test to my repository. Now I know there is lots of debate on what you should do with your flakey tests, but if you find some sort of value in them whatsoever sometimes it doesn't make sense to completely remove them from your repo, but rather put them in a bucket of tests that don't run as often. In this scenario and in my workplace, we decided on the tag `@unsatisfactory`. To me this tells me the test doesn't meet the standard expectations I have to live as a part of the repository and run on a frequent basis, but it allows me to be able to run say once a week or some other cadence, where I can dive into the results of the test and assess if the test(s) flaked out or actually uncovered an issue.

```javascript
// tests/test.spec.ts

...
  test("flakey test @unsatisfactory", async () => {
    const randomBoolean = Math.random() > 0.5;
    expect(randomBoolean).toBe(true);
  });
...
```

To run all tests except for the `@unsatisfactory` tag we'll run our suite using the command `npx playwright test --grep-invert @unsatisfactory` which will run all the tests EXCEPT the @unsatisfactory tag. This can also be combined with the `--grep` command which we'll look at next.

The [command line documentation](https://playwright.dev/docs/test-cli) provides us with insights on how to run the playwright tests from the command line. Both commands below will work

- `-g @ tag`
- `--grep @tag`

It's also worth noting that you can also pass in multiple tags such as if I wanted to run all the tests with the `@happy` tag and/or `@room` tag.

`--grep "@happy|@room"`

This article covers additional details and strategies that can be used with tags

[How do I run a subset of tests with Playwright Test Runner using grep functionality?](https://playwrightsolutions.com/run-a-subset-of-tests-with-grep-and-grep-invert-in-package-json/)

## Running Tagged Tests From UI Mode

You are also able to run tagged tests from Playwright's UI mode. To enter ui mode run the command `npx playwright test --ui`. This will bring up a UI in which you can access all your tests along with a plethora of developer tools to help build and debug tests. In the below example I added `@happy` within the search box and pressed the`Enter` key, this will filter the tests down and then run the tests.

![Image 5](https://playwrightsolutions.com/content/images/2023/10/image-4.png)

## Updating package.json With npm Scripts

As you can see below I've added some new npm run scripts most of which include the `--grep-invert @unsatisfactory` which we covered before and will prevent any tests that have this tagged to not run. This is useful for tagging tests that may be flaky or items you don't want running on every run, but you do want to keep the spec for documentation or to run and get feedback on an ad-hoc basis.

```json
// package.json

{
  ...
  "scripts": {
    ...
    "test": "npx playwright test --grep-invert @unsatisfactory",
    "test:generate:schema": "GENERATE_SCHEMA_TRACKING_DATA=true npx playwright test --grep-invert @unsatisfactory",
    "test:staging": "test_env=staging npx playwright test --grep-invert @unsatisfactory",
    "test:local": "test_env=local npx playwright test --grep-invert @unsatisfactory",
    "test:happy": "npx playwright test --grep @happy --grep-invert @unsatisfactory",
    "test:unsatisfactory": "npx playwright test --grep @unsatisfactory",
    "ui": "npx playwright test --ui",
    ...
  },
...
}
```

## Updating Playwright Config with proper teardown

A few guides back we added a setup  projects within our repository in order to create valid auth sessions and to calculate coverage and a teardown project to run after all tests were complete in order to report on any warnings within our automation suite. When implementing this, there was an error, which wasn't evident until now we try and introduce an `@unsatisfactory` tag using the `--grep-invert` command to run all tests except these. Our first implementation I was missing `teardown` within the setup project. Below you can see I've now included that, and no longer have a decency listed under teardown. The playwright docs can be found [here](https://playwright.dev/docs/test-global-setup-teardown#teardown-example).

```javascript
// playwright.config.ts

...
  projects: [
    { name: "setup", testMatch: /coverage.setup.ts/, teardown: "teardown" },
    {
      name: "api-checks",
      dependencies: ["setup"],
    },
    {
      name: "teardown",
      testMatch: /completion.teardown.ts/,
    },
  ],
...
```

## Introducing Bruno for Exploring the API

During this round of work I took some time and removed the Thunder client files and introduced the `bruno` folder for managing examples of API calls for exploratory testing. [Bruno](https://docs.usebruno.com/) is an open source IDE for exploring and testing APIs. You can read the [Bruno Manifesto](https://docs.usebruno.com/manifesto.html) to get a better idea of why I am swapping.

![Image 6](https://playwrightsolutions.com/content/images/2023/10/image-3.png)

What's really nice about this is the entire collection and environment files are all stored within the `./bruno/` directory on the root level. Each request is easily readable and available whenever you clone the repository.

All the changes discussed in this article can be found in the pull request below. There were a lot of updates where I touched each spec file and added tags appropriately.

[adding tags to suite by BMayhew](https://github.com/playwrightsolutions/playwright-api-test-demo/pull/18/files)

## Wrapping up

Using tags within your tests allows you to manage running different tests based on your needs. I've found the flexibility with this approach has been able to solve any problem I've faced when building out automation suites.

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-15-adding-test-tags-to-get-targeted-feedback/

Published Time: 2023-11-13T13:30:17.000Z
