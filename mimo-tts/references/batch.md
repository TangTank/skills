# 批量输入和续跑

脚本：`SKILL_DIR/scripts/mimo_tts.py`。输入采用 UTF-8，兼容 BOM。

- TXT：每个非空行一条待朗读文本，类别由命令的 `--kind` 指定。
- CSV：第一行为表头，必需 `text` 列。
- JSON：对象数组。
- JSONL：每个非空行一个对象。

对象字段：`text` 必需；`id`、`filename`、`kind`、`voice`、`locale`、`style`、`pace`、`compression`、`instruction_mode` 可选。类别为 `word` / `sentence` / `text`。`voice` 必须是 `voices list` 中的固定选项名称，英文素材优先显式使用官方 `Mia`、`Chloe`、`Milo` 或 `Dean`。`pace` 为 `slow` / `normal` / `brisk` / `fast`，优先级为条目、命令的 `--pace`、本地默认语速。`compression` 为 `original` / `32k` / `24k`，同样按条目、命令、本地默认值的顺序取值。`instruction_mode` 为 `faithful` / `educational` / `neutral`，默认 `faithful`，按类别提供词库、例句或普通文本的只读一次上下文；后两者保留旧请求兼容，复现或续跑旧批次时应显式指定原模式。条目模式优先于命令选项。其他条目的非空值也覆盖命令选项；没有指定音色和口音时使用本地默认音色及该音色配置的 locale。

```json
[
  {"id":"apple-us","text":"apple","kind":"word","locale":"en-US","filename":"apple-us.mp3"},
  {"id":"apple-example","text":"I eat an apple every day.","kind":"sentence","pace":"brisk","filename":"apple-example.mp3"}
]
```

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" batch --input "INPUT_DIR/items.json" --output-dir "OUTPUT_DIR" --dry-run
python "SKILL_DIR/scripts/mimo_tts.py" batch --input "INPUT_DIR/items.json" --output-dir "OUTPUT_DIR"
```

输出固定为 MP3。先验证全部条目及重复路径，然后才发起请求。指定文件名仅允许单一文件名；不允许目录、绝对路径或 `.mp3` 之外的扩展名。不指定时使用 `id/文本摘要 + 请求哈希` 生成名称。同一输入导致相同输出路径时，去除重复条目或分配不同文件名。

本用户采用两阶段批量流程：本阶段以 `--compression original` 生成原音，条目里不设置其他压缩值；全部生成完成后，使用 `batch-compress` 统一压缩到另一个目录。具体命令见 [compression.md](compression.md)。

每个音频有独立 JSON 元数据，批次另有追加式 `manifest.jsonl`。成功文件的请求哈希及音频 SHA-256 均一致时才跳过。中断后使用同一命令续跑；损坏文件或缺失元数据不会被当作成功。用户确实要求重新生成或替换时使用 `--overwrite`。

Windows 本地文件发布和临时文件清理遇到占用时最多等待 5 秒。文件已发布后若临时文件仍被占用，保留临时文件并输出警告，继续保存元数据；这不会重试 TTS 请求。若旧版本在这个位置中断，先核对保留音频、临时文件、请求哈希及派发记录，不能直接重复合成或把缺失元数据的文件当作成功。恢复元数据时记录依据，丢失的响应 ID、用量等保持未知。

脚本顺序请求，默认间隔 0.7 秒，支持 `--interval` 调整。任何 API 错误即停止，不自动重试；超时可能已在服务端完成生成，手动重试可能产生额外用量。`--timeout` 默认 120 秒。不要对同一输出目录同时启动多个写入进程。

`--dry-run` 仅输出计划，不读取 Key，不调用 API，不创建输出文件。生成成功只说明接口返回且文件结构可读取；口音和发音质量仍需试听。脚本检查 MP3 文件头，交付前可用 `ffprobe` / 播放器进一步确认。导入的 WAV 音色参考会检查可读性及完整性。
