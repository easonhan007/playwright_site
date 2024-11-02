
+++
date = 2024-09-04
title = "Timeouts Against Flaky Tests: True Cases with Playwright"
description = "https://adequatica.medium.com/timeouts-against-flaky-tests-true-cases-with-playwright-9f4f28d2c391"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++
Playwright is a highly reliable tool for UI testing, but there are cases when some tests can be flaky, and the timeout anti-pattern fixes this!
-----------------------------------------------------------------------------------------------------------------------------------------------

[![Image 1: Andrey Enin](https://miro.medium.com/v2/resize:fill:88:88/2*bQ4xmdoPtrdMchCQCia7iQ.png)](img/1727601491.753761)

Flaky tests are unreliable tests that occasionally fail, but the reason for the failures is unclear. These problems may be in the application, the environment, the testing tools used, or all of them together. Due to their complexity when interacting with the browser, UI testing tools have long been considered quite unreliable instruments among QA engineers.

However, when comparing tools based on [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/) and those based on [Crome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) ([Puppeteer](https://pptr.dev/) and [Playwright](https://playwright.dev/)), the last one turns out to be more accurate.

Automation engineers can write bad and good tests with both tools depending on their grades. But no matter how good the tool is, the application itself and the test environment significantly impact autotests.

Even adhering to [the best practices in writing autotests](https://adequatica.medium.com/principles-of-writing-automated-tests-a2b72218264c) **to prevent false falls, unreliable results, and unwanted errors** sometimes requires breaking established principles and setting exceptions in the code.

Below are a few cases that I encountered during the automation of several production services with Playwright (actually, these cases can be attributed to any other tool, too):

1.  [UI Animations](https://adequatica.medium.com/timeouts-against-flaky-tests-true-cases-with-playwright-9f4f28d2c391#d65c);
2.  [Drawing on Canvas](https://adequatica.medium.com/timeouts-against-flaky-tests-true-cases-with-playwright-9f4f28d2c391#41b5);
3.  [Sleep Timeouts in CI in the Cloud](https://adequatica.medium.com/timeouts-against-flaky-tests-true-cases-with-playwright-9f4f28d2c391#851d).

> **Disclaimer:** The following may be very controversial. If you want to adopt the suggestions in the text, you should be aware of what you are doing.

1\. UI Animations
-----------------

To prevent flakiness, Playwright has built-in auto-witing machinery inside appropriate actions/commands — it «[performs a range of actionability checks on the elements before making actions to ensure these actions behave as expected](https://playwright.dev/docs/actionability)».

But sometimes, **very rarely,** the Playwright may not click (or misclick) on truly visible and accessible elements.

The Playwright’s auto-waiting for actions is great and makes developing autotests easy. In 99%, it is absolutely accurate, but for the remaining percentages for highly customized interfaces, it may make a mistake — not because it is slow or unreliable but because it is fast and too precise.

This may suddenly appear during some animations of menus, [drawers](https://m2.material.io/components/navigation-drawer), popovers, overlays, and other pop-up elements with transitions and appearance animations. When the element is already on the screen, it is already interactable, but the animation is not over yet, and the click on the element has to go to another place. The difference in a few milliseconds/pixels makes the test flaky.

_The dropdown menu is already interactable, but clicking on the menu item may lead to a misclick_

**Solution:** Add unconditional timeout before or after (depending on a test scenario) flaky click.

Yes, this is an anti-pattern, and [you should avoid pauses inside tests](https://adequatica.medium.com/principles-of-writing-automated-tests-a2b72218264c#b9cd), but sometimes, you have to sacrifice a clear code in favor of reliability, especially in CI.

2\. Drawing on Canvas
---------------------

Interaction with `<[canvas](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas)>` element can also be tricky, especially if it is interactive and contains logic. In my example, I have a map (of course, as a canvas) from a third-party vendor and need to draw an object on it by making a certain number of clicks.

The problem is that the element is actionable for Playwright from the moment it appears on the page, but the actual actionable state of the element is indefinable by its locator.

That is a timeline for loading the element on a page:

1.  Canvas element is attached and visible on the page (the element is actionable for Playwright), but nothing is rendered inside:

`<canvas class="map-canvas" tabindex="0" aria-label="Map" role="region" width="1470" height="956" style="width: 1470px; height: 956px; cursor: crosshair;"></canvas>`

2\. Canvas element has rendered content but is not yet actionable for internal logic:

`<canvas class="map-canvas" tabindex="0" aria-label="Map" role="region" width="1470" height="956" style="width: 1470px; height: 956px; cursor: crosshair;"></canvas>`

3\. Canvas element is ready for action:

`<canvas class="map-canvas" tabindex="0" aria-label="Map" role="region" width="1470" height="956" style="width: 1470px; height: 956px; cursor: crosshair;"></canvas>`

As you can notice, **the HTML element is the same for all states**, but when Playwright is already getting ready to perform clicks, the element itself is not. The final state varies depending on the environment (local or CI run), machine (CI runner) performance, and network bandwidth.

**Solution:** Add unconditional timeout before the first click.

However, this test case does not imply having any mocks, and it is much easier to add a single timeout rather than develop a highly complicated (and potentially fragile) solution for determining a single element’s state. Here, a few seconds in one test is sacrificed in favor of _relative_ reliability.

3\. Sleep Timeouts in CI in the Cloud
-------------------------------------

If your frontend application has its own timeouts (actual business logic may require freaky periods of «sleep»), then your tests may be affected by it.

If you test UI with a logic that contains `[setTimeout()](https://developer.mozilla.org/en-US/docs/Web/API/setTimeout)` in the code like this:

async function sleep(customTimeout: number): Promise<void\> {  
  return new Promise(resolve =\> setTimeout(resolve, customTimeout));  
}

Then, you may encounter the problem that `setTimeout()` can be executed longer than the specified time. It sounds crazy, but this behavior is most pronounced in CI runners (from GitHub Actions to custom runners on dedicated servers) during testing and does not reproduce in production!

**Solution:** Add unconditional timeout that is at least three times longer than the logic under test.

If it waits for a timeout, it waits

Unfortunately, that is not a bug. I even consulted with DevOps and CI’s tech support, who confirmed this behavior:

> JavaScript does not guarantee that the setTimeout will work on time. Therefore, there may be many reasons…
> 
> This may be due to the different virtualization technologies. If GitHub has virtual machines, then processor time is distributed more justifiably than bare metal ones…
> 
> Perhaps the JavaScript runtime detects virtualization technology and cuts the minimum timeout to prevent exploits like [Spectre](https://en.wikipedia.org/wiki/Spectre_/(security_vulnerability) and [Meltdown](https://en.wikipedia.org/wiki/Meltdown_/(security_vulnerability/))…

Timeout Tips
------------

Here are a few principles of organizing timeouts inside test infrastructure:

*   **Make timeout’s value as constant.** In my experience, 300 ms is the optimal time waiting for something on the UI.

export const UNCONDITIONAL\_TIMEOUT = 300;

Eventually, you can divide or multiply the constant depending on the test’s context.

*   **Add a comment for each case of using timeout.** This shows for all developers that using such a method is an exception to the «autotesting rules» and names the reason.

// Wait for input to be applied in the select  
await page.waitForTimeout(UNCONDITIONAL\_TIMEOUT);

Official Playwright’s documentation recommends you «[never wait for timeout in production](https://playwright.dev/docs/api/class-page#page-wait-for-timeout)» and use it only for debugging because tests that wait for time are inherently flaky. But here, I use `waitForTimeout()` exactly for the opposite, despite the fact that **tests with unconditional waits are truthfully flaky.**

> But how often have I been allowed to do this in production? In a recent project, I had 50 tests with more than 200 test steps and more than 120 clicks. Two tests had seven waits for timeouts, and three page objects had six timeouts. Not so much, although, of course, I would like to have zero.

Read more:

*   [What is Flaky Test](https://www.browserstack.com/test-observability/features/test-reporting/what-is-flaky-test)?
*   [How to Avoid Flaky Tests in Playwright](https://semaphoreci.com/blog/flaky-tests-playwright).
