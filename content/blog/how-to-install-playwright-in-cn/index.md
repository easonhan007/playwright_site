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

首先我们需要安装 [nodejs](https://nodejs.org/zh-cn)，这里略过。

我的安装的版本是`Node.js v20.15.1`。

## 最重要的步骤：设置 npm 源

**对于国内用户来说，这一步至关重要，是解决网络联通性的关键。**

打开命令行，输入下面的命令。

如果你对命令行不熟悉，那么 win 11 系统里，随便打开 1 个文件夹，鼠标右键打开系统菜单，选择`在终端中打开`就可以了。

```bash
npm config set registry https://registry.npmmirror.com
```

## 使用 npm 安装 playwrgiht

如果你对命令行熟悉的话，可以新建 1 个文件夹 `demo`，然后从命令行里`cd`进去，再运行下面的命令。

如果你对命令行不熟悉，那么 win 11 系统里，我们可以新建 1 个文件夹 `demo`，进入 demo 文件夹，鼠标右键打开系统菜单，选择`在终端中打开`就可以了。

```bash
npm init playwright@latest
```

### 安装选项

命令运行时会出现 4 个问题，全部按 Enter 选择默认值

- ✔ Do you want to use TypeScript or JavaScript? · TypeScript
- ✔ Where to put your end-to-end tests? · tests
- ✔ Add a GitHub Actions workflow? (y/N) · false
- ✔ Install Playwright browsers (can be done manually via 'npx playwright install')? (Y/n) · true

## 安装 vscode 以及 playwright 插件

这一步不是必须的，但如果你不熟悉命令行的话，那么还是非常推荐的。

## 使用 vscode 打开 pw_demo 文件夹

打开`tests`文件夹下的`test-1.spec.ts`文件。

在 playwright 插件里设置`Show trace viewer`，然后点击`test`方法旁的三角形按钮，就可以运行用例了。
