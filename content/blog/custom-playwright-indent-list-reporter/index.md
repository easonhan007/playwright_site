+++
date = 2024-01-08
title = "Playwright 自定义缩进列表测试报告 📖"
description = "CLI版本的缩进报告"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

你是否曾想要让你的命令行界面更加 🌶️ 呢？好消息是，[Syzana Bicaj](https://www.linkedin.com/in/syzanakajtazaj/)发布了一个 npm 包，不仅允许你自定义颜色，还可以在终端中缩进显示 spec 文件，便于阅读！

![图片1](https://playwrightsolutions.com/content/images/2024/01/image-2.png)

要使用默认设置安装该包，你需要在 Playwright 目录下运行以下命令：

```bash
npm install indent-list-reporter --save-dev
```

这将安装该库，之后你只需要在`playwright.config.ts`文件中更新`["indent-list-reporter"]`。我下面的例子使用了三元运算符，首先检查环境变量 CI 是否为 true 或 undefined/false。如果为 true，则运行带有"?"的顶行；如果为 false（从本地机器运行 playwright 命令），则使用"html"和"indent-list-reporter"报告。

```javascript
import { defineConfig } from "@playwright/test";
export default defineConfig<APIRequestOptions & TestOptions>({
  ...
  reporter: process.env.CI
    ? [["list"], ["html"], ["@currents/playwright"]]
    : [["html"], ["indent-list-reporter"]],
});
```

设置完成后，你可以运行测试，在测试运行完成后看到漂亮的结果。是的，这有一个缺点，原始的测试报告的好处: 是它会在每个测试完成时显示结果，而使用`indent-list-reporter`，除非用例全部执行完，否则你将无法看到测试结果（除非你同时保留自带的测试报告)。单独使用这个测试报告模版时，这是一个小小的权衡。

你还可以选择更改配色方案，在报告配置的数组中，你可以添加一个包含新基础颜色的对象。查看[文档](https://www.npmjs.com/package/indent-list-reporter)了解提供的不同颜色。

```javascript
import { defineConfig } from "@playwright/test";
export default defineConfig<APIRequestOptions & TestOptions>({
  ...
  reporter: process.env.CI
    ? [["list"], ["html"], ["@currents/playwright"]]
    : [
        ["html"],
        [
          "indent-list-reporter",
          {
            baseColors: {
              specFileNameColor: "white",
              suiteDescriptionColor: "blue",
              testCaseTitleColor: "magenta",
            },
          },
        ],
      ],
  ...
});
```

![图片2](https://playwrightsolutions.com/content/images/2024/01/image-1.png)

npm 包可以在这里找到：[indent-list-reporter](https://www.npmjs.com/package/indent-list-reporter)

## 来源

URL 来源: https://playwrightsolutions.com/custom-playwright-indent-list-reporter/

发布时间: 2024-01-08T13:30:14.000Z
