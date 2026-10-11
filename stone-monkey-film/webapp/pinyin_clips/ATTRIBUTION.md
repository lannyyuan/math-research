# 拼音发音录音库（846 条）

本目录是绘本网页“点字看拼音、听发音”用到的全部录音：**每个“音节+声调”一条，同音共用**（全书 17180 个汉字只用 847 种读音）。
文件名 = 读音 id：`{音节}{声调数字}.mp3`，轻声用 5，ü 写作 v，例如 `zhang3.mp3`、`de5.mp3`、`nv3.mp3`。

## 来源与署名

- 录音：Chen Wang 王琛（作者：Wang Chen, Lopez Hugo, Vion Nicolas），Copyright © 2013
- 来源：<https://github.com/hugolpz/audio-cmn>，revision `ff9ed3d0c631195bd2c06f39450f3264c7124040`
- 许可：[CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)。**本目录里的文件（含修改后的版本）同样以 CC-BY-SA 3.0 共享**，再分发时请保留这份署名。
- 取用路径：Pinyin_Drill_P0 的 `human-audio-downloads/audio/`（807 条）；其余 18 条由上游同一 revision 补齐。

## 做过的修改（CC-BY-SA 要求写明）

1. 裁掉首尾静音，转成单声道、22.05 kHz、32 kbps MP3（原文件是 64 kbps 的 `cmn-{id}.mp3`）。
2. 21 个轻声（`*5.mp3`）**不是真人录音**：取同音节另一声的录音，截短到 0.30 秒、尾部渐弱、音量乘 0.85，模拟轻声。底本见 `../pinyin_audio_manifest.json` 的 `neutral`。

这些是供识字参考的发音候选，不是教材认证录音。

## 校验与维护

- `../pinyin_audio_manifest.json` 记录每条的来源、原始 MP3 的 SHA-256、本目录文件的 SHA-256；构建时核对，文件被改动会报错。
- 缺 `ju4`（上游也没有，22 处用系统语音念，没有语音就只显示拼音）。
- 构建（`python3 -X utf8 webapp/build.py`）优先用本目录，**有库就不需要 ffmpeg、Pinyin_Drill 目录和网络**；库里缺的才按来源生成并写进这里。
- 想换掉某一条（比如换成真人录的轻声）：替换文件，并从清单里删掉那一条的记录。
