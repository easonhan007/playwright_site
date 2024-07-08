+++
date = 2024-07-08
title = "playwright里如何快速确定该使用多少个worker运行用例"
description = "默认情况下playwright会自动指定workder的数量"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

好消息是，默认情况下，Playwright 根据您的计算机规格尝试并行运行测试。更好的消息是，通过增加或减少工作线程数，您可以在运行 Playwright 测试时获得更快的反馈。

您可以通过阅读[并行和分片](https://playwright.dev/docs/test-parallel)的文档来了解更多信息，但如果您想快速简便地查看哪种工作线程数量对您的计算机或云中的计算机最优，只需运行以下命令即可。

```
for i in `seq <min> <max>`; do time npx playwright test --reporter=line --workers=$i; done
```

将 `<min>` 修改为您的 CPU 数量除以 2，将 `<max>` 修改为 CPU 数量乘以 2。这个命令将使用不同的工作线程数启动 Playwright 测试套件（通过最小和最大值进行迭代）。输出将通过命令行返回。请注意，根据您的最小和最大输入以及测试数量，此过程可能需要一些时间。因此，请启动并冲泡一些 ☕️ 或 🫖。运行完成后，您应该会得到类似以下的输出。

![Image 1](https://playwrightsolutions.com/content/images/2022/03/image-2.png)

3、5 和 6 次运行的测试都是最短的运行时间。关键是找到最快的运行方式，而不会引入任何不稳定的测试。我的默认值是 `4`，看了结果后，我可能会继续使用这个值。

当尝试在 AWS EC2 实例或云中的其他服务器上运行 Playwright 测试时，我可以看到这个脚本非常实用。

## 来源

**来源链接**: [What's an easy way to tell how many workers?](https://playwrightsolutions.com/whats-an-easy-way-to-tell-how-many-workers/)

**发布时间**: 2022-03-13
