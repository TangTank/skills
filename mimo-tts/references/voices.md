# 音色试听与固定选项

英文词库优先使用官方 Voice ID，不必提供音色描述或参考音频。定制音色仅在用户需要时采用 VoiceDesign 试音，再以选定音频作为 VoiceClone 参考。保存的选项位于 `%LOCALAPPDATA%/mimo-tts/voices.json`，参考文件位于同目录下的 `voices/`。Key 存储与音色配置分开。

## 官方英文音色

| Voice ID | 语言 | 性别 |
| --- | --- | --- |
| Mia | 英文 | 女 |
| Chloe | 英文 | 女 |
| Milo | 英文 | 男 |
| Dean | 英文 | 男 |

这四种音色均使用 `mimo-v2.5-tts`，通过 `audio.voice` 指定；官方没有将其进一步划分为英音或美音。`mimo_default` 因集群而异，中国集群为 `冰糖`，其他集群为 `Mia`，英文素材使用明确的 Voice ID。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" voices default Mia
python "SKILL_DIR/scripts/mimo_tts.py" generate --voice Mia --text "rectangle" --kind word --locale en-US --pace normal --compression original --output "OUTPUT_DIR/rectangle-mia.mp3"
python "SKILL_DIR/scripts/mimo_tts.py" generate --voice Chloe --text "rectangle" --kind word --locale en-US --pace normal --compression original --output "OUTPUT_DIR/rectangle-chloe.mp3"
```

默认 `faithful` 模式把场景和朗读要求写入 `user.content`，原始单词或例句单独写入 `assistant.content`。使用相同文本、请求口音及语速比较候选；只有音色是变化项。默认值更改会影响本机后续调用，仅在用户要求调整默认策略或选定音色时执行；单次对照只用 `--voice`。

官方依据：[预置音色与调用规则](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/speech-synthesis-v2.5)、[API 参数](https://mimo.mi.com/docs/zh-CN/api/audio/tts)。

## 需要定制时生成候选

将命令中的 `SKILL_DIR`、`OUTPUT_DIR` 替换为绝对路径。下列描述可作为海蒂英语的起点，按用户偏好调整，不把提示词当作已验证的口音事实。

| 候选名称 | 音色描述 |
| --- | --- |
| heidi-us-female | Adult female English teacher, clear General American accent, warm and calm, clean articulation, natural classroom pace, friendly without an exaggerated cartoon voice. |
| heidi-us-male | Adult male English teacher, clear General American accent, warm mid-range voice, precise consonants, natural classroom pace, relaxed and encouraging. |
| heidi-uk-female | Adult female English teacher, clear standard British English accent, warm and composed, clean articulation, natural classroom pace, friendly and expressive. |
| heidi-uk-male | Adult male English teacher, clear standard British English accent, warm mid-range voice, precise consonants, natural classroom pace, calm and encouraging. |

每个候选用同一份短试音文本，例如 `Apple. Banana. Water. Tomato. Schedule. Comfortable. The little girl reads a story after school. Can you put the water bottle on the table?`。让用户按口音、清晰度、亲和力、重音和自然度比较。候选命名不等于用户已接受或官方音色分类。

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" design --description "Adult female English teacher, clear General American accent, warm and calm, natural classroom pace." --locale en-US --text-file "OUTPUT_DIR/audition-text.txt" --output "OUTPUT_DIR/heidi-us-female.mp3"
```

`design` 固定使用 `mimo-v2.5-tts-voicedesign`，不发送 `audio.voice`，不启用自动润色。英文短词和英美差异词是检验项；不要用自动生成成功代替人工试听结果。

## 保存选定选项及默认值

```powershell
python "SKILL_DIR/scripts/mimo_tts.py" voices add heidi-us-female --reference "OUTPUT_DIR/heidi-us-female.mp3" --locale en-US --description "已选定的美音女教师样音"
python "SKILL_DIR/scripts/mimo_tts.py" voices default heidi-us-female
python "SKILL_DIR/scripts/mimo_tts.py" generate --voice heidi-us-female --text "beautiful" --kind word --output "OUTPUT_DIR/beautiful-us.mp3"
```

注册会复制完整 WAV / MP3 样音并保存哈希；新生成的试音与成品固定为 MP3，已有 WAV 参考可继续使用。该样音将随每次 VoiceClone 请求发送到官方 API；不是上传后取得持久 Voice ID。参考音频 Base64 编码后不得超过官方的 10 MB 上限。默认名称冲突时拒绝替换；用户要求更新该选项时才使用 `voices add ... --replace`。

已有预置音色也能设为默认，例如 `voices default Chloe`。默认值属于本机所有使用本技能的任务；一次生成用 `--voice` 不改变默认值。不要直接修改海蒂英语应用的配置、上传接口或词库数据。
