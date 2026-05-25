# markdown-flowchart-writer Skill

这是一个用于编写 Markdown 流程图和业务流程文档的 Codex/Agent Skill。

## 主要能力

- 将 ASCII/制表符流程图改为 Mermaid。
- 编写标准 Markdown 业务流程文档。
- 规范中文流程图节点、箭头、子流程、条件分支。
- 避免中文字符宽度导致的预览错位。
- 附带检查脚本，检测 Tab 和 ASCII 盒线字符。

## 使用方式

将整个 `markdown-flowchart-skill` 目录放入你的 skills 目录中。

常用提示词：

```text
请使用 markdown-flowchart-writer skill，把下面的流程图改成 Mermaid，并整理成标准 Markdown 流程文档。
要求：不要使用 ASCII 图，不要使用制表符，节点中文换行用 <br/>。
```

## 检查脚本

```bash
bash scripts/check-markdown-flowchart.sh .
```
