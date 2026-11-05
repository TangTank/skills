# 可选 MP3 压缩

输出格式始终为 MP3，压缩选项用于本地后处理，不是 MiMo 服务端参数。

| `--compression` | 处理方式 |
| --- | --- |
| `original` | 原样保存 MiMo 返回的 MP3，初始默认值 |
| `32k` | FFmpeg / libmp3lame，32 kbps、24 kHz、单声道 |
| `24k` | FFmpeg / libmp3lame，24 kbps、24 kHz、单声道 |

单次选项不改变默认值。用户明确选择长期默认压缩后，执行：

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" config set-compression 32k
python "SKILL_DIR/scripts/mimo_tts.py" config status
```

恢复原始质量使用 `config set-compression original`。设置保存在本地 `settings.json`，保留音色与语速选择。批量条目的 `compression` 优先于命令的 `--compression`，其次才是本地默认值。`--dry-run` 不调用 API、不编码或写文件，也不要求安装 FFmpeg。

## 默认采用先生成、后压缩

用户计划批量生成英文单词和例句，然后单独批量压缩。使用两个独立阶段，原音和成品分别存放：

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" batch --input "INPUT_DIR/items.json" --output-dir "OUTPUT_DIR/original" --compression original
python "SKILL_DIR/scripts/mimo_tts.py" batch-compress --input-dir "OUTPUT_DIR/original" --output-dir "OUTPUT_DIR/mp3-32k" --compression 32k --dry-run
python "SKILL_DIR/scripts/mimo_tts.py" batch-compress --input-dir "OUTPUT_DIR/original" --output-dir "OUTPUT_DIR/mp3-32k" --compression 32k
```

第一阶段输入条目的 `compression` 省略或统一为 `original`；等生成命令报告 `complete` 后再执行第二阶段。`batch --compression 32k` 仍然是每生成一条就压缩一条，不用于这个两阶段计划。

`batch-compress` 默认扫描输入目录直属的 MP3；需要包括子目录时加 `--recursive`，输出保留相同的相对目录和文件名。输出目录必须位于输入目录之外，避免覆盖原音或再次压缩上次输出。

批量压缩先校验所有输入和目标路径，再依次处理。只在内存中保留文件清单和元数据，逐个读取、编码和写出音频。每个压缩文件保存独立 `.mp3.json`，批次另有 `compression-manifest.jsonl`。失败即停止，已完成文件保留；重跑同一命令时校验哈希后跳过。全流程不读取 Key、不调用 MiMo，压缩重试不产生新的语音生成请求。

## 同一原音对比

用户想比较压缩听感时，先以 `original` 保存原音，再对这一个文件调用 `compress`，不用重新生成两段语音，以免语调和停顿变化影响判断。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "I eat an apple every day." --kind sentence --compression original --output "OUTPUT_DIR/example.mp3"
python "SKILL_DIR/scripts/mimo_tts.py" compress --input "OUTPUT_DIR/example.mp3" --output "OUTPUT_DIR/example-32k.mp3" --compression 32k
```

`compress` 默认使用 `32k`，输入和输出必须是不同的 MP3 路径；即使用 `--overwrite`，也不允许覆盖输入。新的输出文件会完整解码检查，保存来源路径、来源音频哈希、最终哈希和编码配置。已生成且哈希匹配的压缩结果会跳过。比较时播放原音与压缩版，并检查词尾、辅音和整体清晰度；不把成功解码当成发音质量验收。

生成任务启用压缩时只保存最终选定版本；若需要同时保留原音，采用上面的“生成 original，再 compress”流程。已经压过的文件尽量不要反复转码。压缩有损，低码率源文件也不保证重新编码后更小。

压缩生成前会检查 FFmpeg 与编码器是否可用；缺失时在发起 MiMo 请求前停止。普通 `original` 生成不需要 FFmpeg。不要静默回退为另一种质量，也不要为重试压缩重新调用 TTS。

协议与编码参考：[MiMo TTS 参数](https://mimo.mi.com/docs/zh-CN/api/audio/tts)、[FFmpeg libmp3lame](https://ffmpeg.org/ffmpeg-codecs.html#libmp3lame-1)。
