---
name: mimo-tts
description: 使用小米 MiMo TTS 2.5 官方预置音色和词句专用上下文生成本地 MP3，支持语速、可选压缩、音色切换和批量续跑。适用于海蒂英语等英语学习素材制作、错音重生成及 MiMo API Key 的本地配置；需要时也可设计或克隆音色。
---

# MiMo TTS 2.5

通过随附的 Python 标准库脚本生成真实 MP3 文件。用户已确定成品固定为 MP3，脚本直接请求 `audio.format: mp3`；单条、批量及新试音都遵循此设置。音色参考文件可保留已有 WAV / MP3。技能目录内不保存 API Key、用户音色或生成音频；这些状态独立存放，更新技能不会覆盖用户选择。

## 入口

将 `SKILL_DIR` 替换为当前技能目录的绝对路径。脚本不依赖 OpenAI SDK 或第三方 Python 包；使用本地压缩选项时额外需要 PATH 上的 FFmpeg，且包含 `libmp3lame` 编码器。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" config status
python "SKILL_DIR/scripts/mimo_tts.py" voices list
```

Key 优先读取 `MIMO_API_KEY`，其次读取本地配置。按用户要求明文保存在 Windows 的 `%LOCALAPPDATA%/mimo-tts/api-key`，`MIMO_TTS_HOME` 可指定独立配置目录。其他系统保存到 `~/.config/mimo-tts/api-key`，文件权限为 `0600`。不额外引入加密或上传流程。

用户已授权提供 Key 时直接保存，不再次询问权限。使用隐藏输入 `config set-key`，或通过标准输入送入 `config set-key --stdin`。不要把 Key 放在命令行参数、技能文件、项目源码或音频清单里；不要回显 Key。未收到 Key 时先完成离线准备，明确区分本地校验与真实 API 成功。

普通 Key 使用 `https://api.xiaomimimo.com/v1`；`tp-` / `ttp-` 套餐 Key 自动使用官方 `https://token-plan-cn.xiaomimimo.com/v1`，不可混用。其他集群可通过 `MIMO_TTS_API_BASE` 指定官方新加坡或欧洲 Token Plan 地址。配置不改变套餐的使用范围；正式应用后端与脱离编程工具的自动化任务使用普通 API Key，具体范围见 [官方 Token Plan 说明](https://mimo.mi.com/docs/zh-CN/tokenplan/Token%20Plan/subscription)。

## 生成单词或例句

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "apple" --kind word --voice Mia --locale en-US --output "OUTPUT_DIR/apple-us.mp3"
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "She reads a book every evening." --kind sentence --voice Mia --locale en-US --output "OUTPUT_DIR/example.mp3"
```

英文词库优先使用官方预置音色及 `mimo-v2.5-tts`：`Mia`、`Chloe` 为英文女声，`Milo`、`Dean` 为英文男声。默认起点为 `Mia`，用 `--voice` 可单次切换；省略时遵循 `voices list` 返回的本地默认值，不覆盖用户后续选择。中文可显式选择 `冰糖`、`茉莉`、`苏打`、`白桦`，并指定 `--locale zh-CN`。不要把音色名称推断成官方英音/美音分类，也不要依赖 `mimo_default`：中国集群默认是 `冰糖`，其他集群默认是 `Mia`。已有 `heidi-*` 克隆选项保留，只在用户选择定制音色时使用。

默认 `--instruction-mode faithful`，按 `--kind` 设置 `user.content` 上下文：`word` 使用词库场景、词典式中性朗读和正确词重音，明确要求按原顺序每个单词只读一次；`sentence` 使用例句场景及自然断句；`text` 使用忠实原文的中性朗读。英文 locale 额外明确 `Use English pronunciation only. Do not switch languages.`。三类均要求只朗读 `assistant` 中的原始文本，不追加任何非传入内容，不重复、翻译、扩展或解释，不朗读指令，读完立即停止；单词不套用句子的连读要求。`assistant.content` 始终只放原始待朗读文本，不混入场景说明或音标。`--kind` 不指定时为 `text`，生成单词或例句应显式指定。

需要比较四种官方英文音色时，同一词分别生成 `Mia`、`Chloe`、`Milo`、`Dean` 的独立 MP3；四者使用相同的 `user.content` 限制、原文、口音和语速，只改变 `audio.voice`。修改上下文后，应在新目录生成完整一组，避免混用不同指令的样音。限制是合成指令，不能把设置了限制等同于实际内容已验收。

`--locale en-US` / `en-GB`、`--style` 都通过自然语言指令控制发音，不是服务端严格的口音或语速参数；质量须试听确认。保留用户给定文本，不擅自加入释义、拼读或重复。生成例句文本本身需有用户授权；已有例句不擅自润色。

生成时直接提交英文单词或英文例句，不需要提供音标，也不把补齐音标、词性或义项作为批量生成的前置条件。音标不写入待朗读文本；遇到实际错读或多音词歧义时，再针对该条核对读法。

输出包含 MP3 音频及同名 `.mp3.json` 元数据，记录文本、所选音色、请求口音、模型、指令、用量和哈希。现有文件只有在请求与音频哈希均匹配时跳过；更换设置时选择新路径，或在用户要求替换后用 `--overwrite`。

## 正确性优先与重新生成

用户反馈错读、重复或追加内容，或要求逐条正确时，先阅读 [references/quality.md](references/quality.md)。文件生成成功、哈希一致、时长正常和 ASR 转写匹配都不能单独证明发音正确；未经内容验收的音频不得标为已验收成品。

重新生成少量问题词时，优先显式指定 `--voice Mia` 或 `--voice Chloe`、`--kind word --instruction-mode faithful --pace normal`，保存到独立目录。`normal` 用于本轮对照，不改变用户已保存的语速；音色效果须试听确认。条目 `instruction_mode` 优先于命令选项。旧的 `educational` 和 `neutral` 保留原始请求及哈希兼容，可用于复现旧批次；续跑旧批次时显式指定原模式。模式或上下文变化会改变请求哈希，不将旧音频当作新结果。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "apple" --kind word --voice Mia --locale en-US --pace normal --instruction-mode faithful --compression original --output "NEW_OUTPUT_DIR/apple-mia.mp3"
```

直接使用原英文文本生成，重点检查音频是否忠实朗读原文；发现读法歧义时再单独复核，不能用识别器猜测结果作为标准答案。小批问题词试音不代表授权恢复已停止的全量任务；候选保留为待试听，不自动替换原音或宣称已纠正。

## 语速选项

单条、批量和新试音支持 `--pace`，不指定时使用本地默认档位，初始值为 `normal`。

| 选项 | 含义 |
| --- | --- |
| `slow` | 慢速、清晰 |
| `normal` | 自然日常语速，连贯朗读 |
| `brisk` | 稍快，减少词间停顿 |
| `fast` | 快速、流畅，保留清晰发音 |

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "I eat an apple every day." --kind sentence --pace brisk --output "OUTPUT_DIR/example-brisk.mp3"
python "SKILL_DIR/scripts/mimo_tts.py" config set-pace brisk
```

`config set-pace` 把默认语速保存到本地 `settings.json`，独立于音色选择；单次 `--pace` 不改变默认值。批量条目的 `pace` 优先于命令选项，其次才是本地默认值。元数据记录请求档位，语速变化参与请求哈希。

MiMo 使用自然语言指令控制节奏，档位不等同于精确播放倍速，也不能保证每次总时长严格递减。分别重新合成的样音，即使用同一参考音色，也可能改变语调和停顿，不能当作只改变速度的严格对比。调整时保留已选音色、口音和原文本，用少量同句样音试听并测量时长，用户选定后保存默认档位。若用户要排除语调差异，使用同一段已确认音频做保持音高的后期变速，并明确标注来源及处理方式。避免 `--style` 中再加入与 `--pace` 矛盾的语速要求。精确倍速播放或后期变速属于另外的处理，不伪称为服务端参数。

## 可选压缩

单条、批量和新试音支持 `--compression original|32k|24k`：`original` 保留 MiMo 返回的原始 MP3，`32k` / `24k` 在本地编码成对应码率、24 kHz、单声道的 MP3。初始默认值为 `original`，不因用户试听压缩样例而自动修改默认质量。

本用户计划先批量生成英文单词和例句，再统一批量压缩，默认按两个独立阶段执行：第一阶段 `batch --compression original` 保存全部原音，成功完成后再运行 `batch-compress --compression 32k`，压缩输出放到原音目录之外。输入条目的 `compression` 省略或设为 `original`，避免覆盖第一阶段的原音选项。压缩失败或重试只处理本地原音，不重新生成语音。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" generate --text "I eat an apple every day." --kind sentence --compression 32k --output "OUTPUT_DIR/example-32k.mp3"
python "SKILL_DIR/scripts/mimo_tts.py" compress --input "OUTPUT_DIR/example.mp3" --output "OUTPUT_DIR/example-32k.mp3" --compression 32k
```

`compress` 处理单个已有 MP3，`batch-compress` 处理一个目录；两者仅在本地执行，并保留输入文件。生成时的压缩属于逐条后处理，只有用户明确选择这种方式时才采用。压缩设置参与续跑校验；元数据区分原始响应和最终文件的字节数及哈希。两阶段命令、默认保存、批量条目优先级及对比试听见 [references/compression.md](references/compression.md)。

## 试听并固定音色

普通英文素材先比较官方预置音色，不需要设计音色或提供参考音频。只有用户希望定制音色时，才使用 `design` 调用 `mimo-v2.5-tts-voicedesign` 生成少量候选；使用相同的代表性单词和例句，明确标出男女声、请求口音及风格。具体操作见 [references/voices.md](references/voices.md)。

官方 VoiceDesign 接口返回音频，没有可复用的自定义 Voice ID。选定后用 `voices add` 把样音复制到本地，再以 `mimo-v2.5-tts-voiceclone` 复用该参考音频，形成固定名称选项。注册选项和设置默认值本身不调用 API。后续可通过 `--voice 选项名` 临时切换，或 `voices default 选项名` 持久切换。

候选未试听选定时保持为候选，不替用户决定音色满意度或覆盖现有默认值。选定后再生成少量独立单词和例句验证复用表现；同一参考样音提高可复用性，但不能承诺每次结果完全一致。

## 批量生成

支持 TXT、CSV、JSON、JSONL；字段、示例和续跑方式见 [references/batch.md](references/batch.md)。先用 `--dry-run` 校验整个输入和输出路径，不读 Key、不调用 API、不写文件。默认顺序调用，失败即停，不自动重试；修复原因后重跑同一命令，已完成文件会校验后跳过。

首次大批量任务先做有代表性的少量样音，试听口音、重音、短词、句子自然度和音色一致性。用户已批准的素材范围可继续执行，不将一次试音扩大成全词库生成。仅交付本地文件，上传云存储、写海蒂英语数据库或改项目代码需要相应明确需求。

## 官方协议依据

- [语音合成使用指南](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5)
- [TTS API 参数](https://mimo.mi.com/docs/zh-CN/api/audio/tts)

协议核对日期：2026-10-29。脚本采用非流式 `POST {对应凭证的官方 Base URL}/chat/completions`：目标文本放 `assistant`，音色描述/朗读指令放 `user`，从 `choices[0].message.audio.data` 解码音频。不要替换成 `/audio/speech`，不要添加文档未支持的 SSML、数值 `speed` 或任意 Voice ID。官方示例的 `Chloe` 是预置音色，使用 `mimo-v2.5-tts`；参考样音复刻使用另一个模型 `mimo-v2.5-tts-voiceclone`。二者均不能因接口成功就认定内容正确。不要启用会润色文本的 `optimize_text_preview` 来制作要求忠实原文的词库素材。
