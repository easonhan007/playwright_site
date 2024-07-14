+++
date = 2022-11-16
title = "如何在GitHub Actions中缓存 Playwright 浏览器二进制文件"
description = "可以节约时间和运行成本"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

我最近于 2022 年 11 月 16 日更新了这篇文章!

如果你发现自己每天多次在 GitHub Actions 中运行 Playwright 测试,你可以通过缓存下载的二进制文件来节省时间和成本。

要了解 Playwright 如何安装和管理浏览器,最好的方法是查看[官方文档](https://playwright.dev/docs/browsers#managing-browser-binaries)。

文档中提到,每种浏览器的默认安装位置如下:

---

Playwright 将 Chromium、WebKit 和 Firefox 浏览器下载到特定操作系统的缓存文件夹中:

- Windows: `%USERPROFILE%\AppData\Local\ms-playwright`
- MacOS: `~/Library/Caches/ms-playwright`
- Linux: `~/.cache/ms-playwright`

---

下面的 GitHub Actions YAML 文件包含了一个创建缓存并存储 Playwright 二进制文件的部分,这样 GitHub Actions 就不必每次运行时都重新下载。这里的关键是确保 'key' 部分(目前设置为 `Linux-playwright-1.27.1`)在每次更新 Playwright 版本时都要更新。这将使缓存失效和自动下载最新的 Playwright 版本,并在新的 key 下缓存它。

例如,如果发布了 Playwright 1.28.0 版本,当我更新 package.json 文件以获取 1.28.0 版本时,缓存 key 将自动更新为 `Linux-playwright-1.28.0`,这将下载最新版本的 Playwright 并在该 key 值下缓存它。

另外需要注意的是,以下代码行很重要,它用于检查缓存是否仍然有效,或者是否应该重建:

```yaml
if: steps.playwright-cache.outputs.cache-hit != 'true'
```

```yaml
name: Playwright Tests
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v2
        with:
          node-version: "16.x"

      - name: Get installed Playwright version
        id: playwright-version
        run: echo "PLAYWRIGHT_VERSION=$(node -e "console.log(require('./package-lock.json').dependencies['@playwright/test'].version)")" >> $GITHUB_ENV
      - name: Cache playwright binaries
        uses: actions/cache@v3
        id: playwright-cache
        with:
          path: |
            ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright-${{ env.PLAYWRIGHT_VERSION }}
      - run: npm ci
      - run: npx playwright install --with-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'
      - run: npx playwright install-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'

      - name: Run Playwright tests
        run: npx playwright test
      - uses: actions/upload-artifact@v2
        if: always()
        with:
          name: playwright-test-results
          path: test-results/
```

以下是 GitHub Actions 实际运行时的一些截图。示例仓库可以在[这里](https://github.com/BMayhew/new-playwright-init/actions)找到。

![图片1](https://playwrightsolutions.com/content/images/2022/11/image-6.png)

👆GitHub Actions 运行创建缓存的示例

![图片2](https://playwrightsolutions.com/content/images/2022/11/image-7.png)

GitHub Actions 运行使用缓存的示例 👆

![图片3](https://playwrightsolutions.com/content/images/2022/11/image-8.png)

GitHub Actions 页面中可见的缓存 ⬆️

根据我的测试,这可以为你的 Playwright 测试运行节省不少时间(至少 3 分钟)。不过我确实遇到过有几天 Playwright 安装过程耗时超过 8 分钟的情况。正是这个问题促使我深入研究这个方案。

如果你想出了任何创新的缓存使用方法,或者觉得这篇文章对你有帮助,欢迎在 Twitter 上联系我 [@butchmayhew](https://twitter.com/ButchMayhew),或者考虑给我买杯咖啡。

## 来源

URL 来源: https://playwrightsolutions.com/playwright-github-action-to-cache-the-browser-binaries/

发布时间: 2022-11-16T09:30:00.000Z
