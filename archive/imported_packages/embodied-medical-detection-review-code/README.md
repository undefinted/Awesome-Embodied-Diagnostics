# 此前实际使用的代码

这个小包只包含从现存工作区直接恢复的源码：

- 9 个 Python 检索、筛选、制图、审计和打包脚本；
- 2 个工作簿生成 `.mjs` 脚本；
- Python 依赖版本；
- 原始源码 SHA-256 校验值。

代码没有被改写成“看起来像当时用过”的版本。完整的文献元数据、筛选数据和图形结果位于配套的 `embodied-medical-detection-review-research` 研究快照中。

注意：现存工作区未找到此前 28 页 PPT 的独立生成代码，所以本包不包含 PowerPoint 生成脚本。两个工作簿脚本依赖原运行环境的 `@oai/artifact-tool`；Python 脚本的主要依赖见 `requirements.txt`。

