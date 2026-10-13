# 种子录音库（846 条）

本目录是 skill `web-pinyin-audio` 自带的**种子库**：`clips.zip` 里是 846 个 mp3（打成一个文件，省得 skill 目录里躺几百个文件），每个“音节+声调”一条，已经裁剪转码好；`pinyin_clips.py` 会把用到的那些解出来放进项目的录音库，不需要 ffmpeg。
（想听某一条：`unzip clips.zip zhang3.mp3`。想把项目库的新录音并回种子库：`pinyin_clips.py --pack-seed <项目库目录>`。）
zip 里的文件名 = 读音 id：`{音节}{声调数字}.mp3`，轻声用 5，ü 写作 v，例如 `zhang3.mp3`、`de5.mp3`、`nv3.mp3`。覆盖约 850 个常用读音；缺的音节由 `pinyin_clips.py` 按 Pinyin_Drill → 上游的顺序现做。

## 来源与署名

- 录音：Chen Wang 王琛（作者：Wang Chen, Lopez Hugo, Vion Nicolas），Copyright © 2013
- 来源：<https://github.com/hugolpz/audio-cmn>，revision `ff9ed3d0c631195bd2c06f39450f3264c7124040`
- 许可：[CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)。**本目录里的文件（含修改后的版本）同样以 CC-BY-SA 3.0 共享**；用它们做的网页发布时必须署名并说明修改。

## 做过的修改（CC-BY-SA 要求写明）

1. 裁掉首尾静音，转成单声道、22.05 kHz、32 kbps MP3（原文件是 64 kbps 的 `cmn-{id}.mp3`）。
2. 21 个轻声（`*5.mp3`）**不是真人录音**：取同音节另一声的录音，截短到 0.30 秒、尾部渐弱、音量乘 0.85，模拟轻声。底本见 `manifest.json` 的 `neutral`。

这些是供识字参考的发音候选，不是教材认证录音。

## 校验

`manifest.json` 记录每条的来源（drill = Pinyin_Drill_P0，upstream = 上游同一 revision）、原始 MP3 的 SHA-256、本目录文件的 SHA-256；`unavailable` 是上游也没有的音节（`ju4`）。复制进项目时会核对，文件损坏会报错。
