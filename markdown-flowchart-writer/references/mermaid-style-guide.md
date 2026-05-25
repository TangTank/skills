# Mermaid Style Guide for Chinese Markdown Documents

## General Principles

- Prefer `flowchart TD` for business processes.
- Use `flowchart LR` for short serial chains.
- Keep node IDs in English and labels in Chinese.
- Keep labels short.
- Use `<br/>` for line breaks in nodes.
- Use `subgraph` for grouped process chains.
- Use dashed arrows for triggered or optional relationships.

## Node Naming

Good:

```mermaid
flowchart TD
    Contract[SALES-006<br/>销售合同签订<br/>管理流程]
```

Avoid:

```mermaid
flowchart TD
    销售合同签订流程[SALES-006 销售合同签订管理流程]
```

## Arrow Types

```mermaid
flowchart TD
    A[开始] --> B[下一步]
    B -. 条件触发 .-> C[可选流程]
    C -- 是 --> D[通过]
    C -- 否 --> E[退回]
```

## Subgraph Example

```mermaid
flowchart TD
    A[成交] --> Check[对账]

    subgraph Finance[财务结算链路：严格串行]
        Check[SALES-003<br/>对账流程] --> Invoice[SALES-004<br/>发票管理]
        Invoice --> Payback[SALES-005<br/>回款跟进]
    end
```

## Avoid

- ASCII art.
- Tabs for alignment.
- Long paragraphs inside nodes.
- Too many crossing arrows.
- More than 20 nodes in one diagram.
