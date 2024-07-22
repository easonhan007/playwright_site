+++
date = 2024-07-22
title = "如何安装playwright 2024版本"
description = "先要装nodejs，在国内完整安装有难度"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础"]
[extra]
math = false
image = "banner.jpg"
+++

这几天录视频，在 windows 电脑上试着去安装了一下 javascript 版本的 playwright，发现有点难度，主要是网络联通性有挑战，这里简单记录一下。

## 安装 nodejs

首先我们需要安装 nodejs，这里略过。

## 打开命令行

很多同学不会打开命令行输入命令。这里我提供 2 个方法。

### win + R，然后输出 cmd

大部分的版本的 windows 都可以使用 win+r 快捷键，然后输入 cmd，打开命令行。

### 按 win 键，然后搜索 cmd

win11 系统可以直接搜索 cmd，然后点击命令行应用。

## 使用 npm 安装 playwrgiht

新建 1 个文件夹 `pw_demo`，然后从命令行里`cd`进去，再运行下面的命令。

```bash
npm init playwright@latest --registry=https://registry.npmmirror.com
```

我自己实验了一下，发现 2 个问题

- 晚上的时候这个命令执行速度会非常慢，可能会经常超时
- 我在网络正常的情况下完成安装总耗时**6-8 分钟**，所以要保持耐心

### 安装选项

命令运行时会出现 4 个问题，除了第 1 个问题要选择 TypeScript 之外，其他的都按 Enter 选择默认值

- ✔ Do you want to use TypeScript or JavaScript? · TypeScript
- ✔ Where to put your end-to-end tests? · tests
- ✔ Add a GitHub Actions workflow? (y/N) · false
- ✔ Install Playwright browsers (can be done manually via 'npx playwright install')? (Y/n) · true

## 安装 vscode 以及 playwright 插件

这一步不是必须的，但如果你不熟悉命令行的话，那么还是非常推荐的。

## 使用 vscode 打开 pw_demo 文件夹

打开`tests`文件夹下的`test-1.spec.ts`文件。

在 playwright 插件里设置`Show trace viewer`，然后点击`test`方法旁的三角形按钮，就可以运行用例了。
