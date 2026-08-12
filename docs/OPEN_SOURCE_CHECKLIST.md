# Open-source release checklist / 开源前检查表

- [ ] 确定代码许可证（例如 MIT、Apache-2.0 或 GPL-3.0）。
- [ ] 单独确认数据、文摘、API 缓存和第三方图片的再分发条件。
- [ ] 添加作者、单位、ORCID、项目主页和推荐引用格式。
- [ ] 决定 raw API cache 的发布方式：Git LFS、GitHub Release、Zenodo/OSF 或 DVC。
- [ ] 对自动纳入/排除结果进行人工复核，并记录复核者和冲突解决流程。
- [ ] 按 PRISMA-S 要求补充每个数据库的完整检索式、检索日期和平台版本。
- [ ] 给数据表增加字段字典和缺失值定义。
- [ ] 在干净环境运行全部可复现命令并记录日志。
- [ ] 将最终论文/PPT中的每张数字图关联到对应源数据和脚本版本。
- [ ] 不公开 `data/incomplete_workspace_files/`，或仅作为带警告的取证附件发布。

大型 PDF/TIFF/XLSX 已在 `.gitattributes` 中配置为 Git LFS 类型；正式提交前需先安装并初始化 Git LFS。

