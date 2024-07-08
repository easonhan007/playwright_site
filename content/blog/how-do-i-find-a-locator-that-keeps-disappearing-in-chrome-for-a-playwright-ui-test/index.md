+++
date = 2024-07-07
title = "如何在Playwright UI测试中找到在Chrome中不断消失元素的定位器"
description = "需要有一点技巧"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我知道我之前遇到过很多次这个问题。感觉就像是在比赛中选择元素并快速查看控制台以实际获取元素名称。

这个简单的技巧可能会帮助你在交互时保持下拉菜单或弹出窗口的可见性。

我们将使用 Chrome 开发者工具的“模拟聚焦页面”功能。在 Mac 上打开 Chrome 开发者工具，使用\[⌘ 或 Ctrl\]+\[P\]命令菜单，搜索`>emulate a focused page`并按 Enter。

![Image 3](https://playwrightsolutions.com/content/images/2022/09/image.png)

这将使某些元素保持聚焦状态，以便它们可以被选择。

要亲自试试这个功能，你可以访问[MDN 文档](https://developer.mozilla.org/en-US/)并尝试检查搜索框中的一个搜索结果。

感谢[@sulco](https://twitter.com/sulco/status/1305841873945272321)提供的灵感。
