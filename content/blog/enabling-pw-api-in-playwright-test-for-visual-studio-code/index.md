+++
date = 2023-04-03
title = "在 VSCode 中启用 pw:api 以增强playwright的调试功能"
description = "从vscode里运行playwright也可能看到详细的调试信息了"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

刚开始使用 Playwright 时，你可能运行了你的第一个测试命令，`npx playwright test`。真棒！用已故绝地大师欧比-旺-克诺比的话来说，"**你已经迈出了进入更大世界的第一步。**"

深入挖掘，你可能已经学会了通过传递环境变量来在运行测试时在控制台中显示调试信息。`DEBUG=pw:api npx playwright test` 你甚至可能已经将其永久设置为系统环境变量，这本身就很酷！

![图 1: DEBUG=pw:api npx playwright test 输出](https://playwrightsolutions.com/content/images/2023/03/pw-api.png)

看看这些美丽、详细的调试信息！

### 现在，时间过去了一段。

你探索了更多的 Playwright 生态系统，设置了 Visual Studio Code 并安装了 Playwright Test for VSCode 插件！现在你手中有了如此强大的工具！你打开了测试资源管理器，启动了一个测试，当你查看测试输出时，现在你看到的只是...

![图 2](https://playwrightsolutions.com/content/images/2023/03/vscode-no-debug.png)

所有优雅的调试信息去哪了？:(

如果你喜欢优雅的调试信息，并通过 Playwright Test for VSCode 运行测试，请继续阅读！

## 让我们快速修复这个问题！

1.  在 VS Code 中打开 `扩展`。
2.  找到 Playwright Test for VS Code 并点击 `齿轮`图标

![图 3](https://playwrightsolutions.com/content/images/2023/03/vscode-click-the-gear.png)

3. 然后点击 `扩展设置`。

4. 现在，一个名为 `设置` 的窗口会出现在你打开的文件的主选项卡中。注意 `Playwright: Env` 部分。在这里，我们可以保存 Playwright 测试在通过 VS Code 执行时使用的环境变量。
   点击 `在 settings.json 中编辑`

![图 4](https://playwrightsolutions.com/content/images/2023/03/vscode-edit-in-settingsjson.png)

5. 一个名为 `settings.json` 的文件现在将在你的编辑器中打开，光标位于 `"playwright.env"` 部分内。

仔细在 `"playwright.env"` 的花括号内添加 `"DEBUG": "pw:api"`

![图 5](https://playwrightsolutions.com/content/images/2023/03/vscode-add-env.png)

6. 保存并关闭 `settings.json`

7. 运行你的测试并打开 `查看测试输出`。

### 它又出现了！

![图 6](https://playwrightsolutions.com/content/images/2023/03/vscode-api-debugging-to-vscode-pw-1.png)

哦，优雅的调试信息，我多么想念你。

---

感谢阅读！如果你觉得这篇文章有帮助，请通过 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 联系我，或者考虑 [请我喝一杯咖啡](https://ko-fi.com/butchmayhew)。如果你想要更多内容发送到你的收件箱，请在下方订阅。

## 来源

[网址来源](https://playwrightsolutions.com/enabling-pw-api-in-playwright-test-for-visual-studio-code/)

发布时间: 2023-04-03
