+++
date = 2025-06-27
title = "Playwright v1.52 和 v1.53 有哪些新功能：AI 自动修复、可描述的定位器等！"
description = "实现了将近20前QTP画下的大饼：脚本自动修复功能"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

来快速了解一下 Playwright v1.52 和 v1.53 的新特性吧！本次更新带来了一些强大的功能，特别是在调试和报告方面，大大提升了测试体验：

---

🧠 **VS Code 中的 AI 自动修复功能**

Playwright 现在可以与 GitHub Copilot 深度集成，帮助你在 VS Code 中直接修复测试失败。当测试失败时，只需点击错误信息旁边的 ✨ 图标，或在测试资源管理器中悬停测试名称时点击图标。Playwright 会将足够的上下文信息提供给 Copilot，Copilot 会生成有针对性的修复建议。你可以查看、接受并重新运行，整个流程快速、高效，而且非常实用。

![](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2Fg8shs35tp2e33mtmejkm.png)

> 想尝试这个功能？确保你已经安装并启用了 Playwright 的 VS Code 插件。

---

🔎 **locator.describe()：增强 Trace 和报告可读性**

现在你可以通过 `.describe()` 为任何定位器添加更具可读性的描述：

```javascript
const newTodo = page
  .getByPlaceholder("What needs to be done?")
  .describe("新待办输入框");
await newTodo.fill("买牛奶");
```

这些描述会出现在：

- Trace Viewer 中
- UI 模式下
- HTML 测试报告中

![](https://media2.dev.to/dynamic/image/width=800%2Cheight=%2Cfit=scale-down%2Cgravity=auto%2Cformat=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2Fzjsqapaixb7b0s7r6jdj.png)

这一小改动在调试复杂 UI 或团队协作时可以带来巨大的帮助。

---

📊 **HTML 报告支持自定义标题**

你可以为测试报告添加更清晰的标题，配置如下：

```javascript
import { defineConfig } from "@playwright/test";

export default defineConfig({
  reporter: [["html", { title: "自定义测试运行 #1028" }]],
});
```

非常适合用于团队仪表板、CI 输出，或用于区分多个测试运行。

---

✅ **新增断言：`toContainClass`**

想验证某个元素是否包含特定 class？现在可以使用：

```javascript
await expect(page.getByRole("listitem", { name: "Ship v1.52" })).toContainClass(
  "done"
);
```

这种方式语法简洁、表达精准，尤其适用于基于 class 的 UI 状态检查。

---

🧪 **快照增强：支持 `children` 和 `url`**

ARIA 快照（通过 `toMatchAriaSnapshot`）现在支持：

- `/children: equal` —— 确保子元素被包含在快照中
- `/url: "https://playwright.dev"` —— 匹配特定 URL

示例：

```javascript
await expect(locator).toMatchAriaSnapshot(`
  - list
    - /children: equal
    - listitem: Feature A
    - listitem:
      - link "Feature B":
        - /url: "https://playwright.dev"
`);
```

这让 UI 快照测试在处理复杂或动态组件时更加可靠。

---

⚙️ **测试运行器更新**

新增了以下便捷功能：

- `testProject.workers` —— 每个测试项目可自定义并发数
- `failOnFlaky` —— 一旦检测到测试不稳定，可自动判定为失败

---

🆙 **如何升级？**

安装最新版本：

```bash
npm i -D @playwright/test@latest
```

同时别忘了将 VS Code 插件更新到最新版本，以便启用 AI 修复等新功能。
