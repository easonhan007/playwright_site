+++
date = 2023-01-23
title = "如何获取 Playwright 测试运行后所有通过或失败测试的详细信息"
description = "用playwright-json-summary-reporter库"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在我刚开始使用 Playwright 时,我曾尝试回答这个问题,但一直找不到合适的解决方案。幸运的是,Playwright 团队开发了 reporter 功能,让我们可以轻松创建[自定义报告](https://playwright.dev/docs/test-reporters#custom-reporters)。

这促使我开发了一个自定义 reporter, 它可以输出我需要的特定信息,并以可在测试运行后用 json 展示，json 文件是可以解析的，这为其他系统的集成提供了便利。我的目标是创建一个 JSON 文件,包含运行时长、最终状态(通过/失败),以及通过、失败和跳过的测试列表。有了这些信息,我就可以轻松地以编程方式重试任何失败的测试,并将失败的测试列表作为 Slack 通知集成的一部分。

这让我兴奋地宣布:我创建了一个 NPM 包,可以为你完成这项工作!

[playwright-json-summary-reporter](https://www.npmjs.com/package/playwright-json-summary-reporter)

在你的 Playwright 项目中使用这个包非常简单。

## 安装

在你的 Playwright 目录下运行以下命令来安装这个包。这会将依赖项添加到你的 `package.json` 文件中。

```bash
$ npm install playwright-json-summary-reporter --save-dev
```

## 使用方法

现在修改你的 `playwright.config.ts` 文件,加入这个自定义报告器:

```javascript
  reporter: [
    ['playwright-json-summary-reporter'],
    ['html'], // 其他reporter
    ['dot']
  ],
```

现在当你运行测试时,应该会在目录根目录下生成一个新的 `summary.json` 文件。下面是该文件的一个示例。

```json
// summary.json

{
  "durationInMS": 41565,
  "passed": [
    "api/create-user-account.spec.ts:34:3",
    "api/create-user-account.spec.ts:55:3",
    "api/delete-user-account.spec.ts:47:3",
    "api/login.spec.ts:12:3",
    "api/login.spec.ts:37:3",
    "api/login.spec.ts:61:3",
    "api/login.spec.ts:84:3",
    "ui/codepen/copyToClipboard.spec.ts:5:1",
    "ui/codepen/copyToClipboard.spec.ts:17:1",
    "ui/internet.app/selectPresentElement.spec.ts:10:1",
    "ui/internet.app/selectPresentElement.spec.ts:35:1",
    "ui/grep.spec.ts:4:3",
    "ui/grep.spec.ts:9:3",
    "ui/loginUser.spec.ts:22:3",
    "ui/loginUserNoImages.spec.ts:23:3",
    "ui/loginUser.spec.ts:37:3",
    "ui/loginUserNoImages.spec.ts:40:3",
    "ui/registerUser.spec.ts:17:1"
  ],
  "skipped": [],
  "failed": [],
  "warned": [],
  "timedOut": [],
  "status": "passed",
  "startedAt": 1674431153277
}
```

有了这个文件,我现在可以使用命令行工具如 `cat` 和 `jq` 来解析文件并从命令行获取数据。下面的命令会获取失败数组中的所有值,并将换行符替换为空格,这样你就有了一个可以用来重新运行失败测试的文件列表。

```bash
failed=`cat summary.json | jq -r '.failed[]' |  tr '\n' ' '`
```

这也让我们可以把 Playwright 的执行结果集成道其他应用，比如 slack 通知!

如果我提供的方法不够有用,你只是想要一个包含测试运行详情的纯文本文件,你可以看看 [Stephen Kilbourn](https://www.linkedin.com/in/stephenkilbourn/) 的报告摘要包。

[@skilbourn/playwright-report-summary](https://www.npmjs.com/package/@skilbourn/playwright-report-summary)

---

感谢阅读!如果你觉得这篇文章有帮助,可以在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或者考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想获得更多内容直接发送到你的收件箱,请在下方订阅。

## 来源

URL 来源: https://playwrightsolutions.com/is-it-possible-to-get-a-list-of-all-passed-or-failed-tests-after-a-playwright-test-run/

发布时间: 2023-01-23T13:30:50.000Z
