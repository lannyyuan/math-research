# 课件生成脚本

`deliverables/汽油车vs电动车-小学科学.pptx` 由这里的脚本生成。

| 文件 | 作用 |
|---|---|
| `clips.tsv` | 每个零件页对应的视频片段：页面、来源（gas/ev）、起点秒、终点秒、封面帧秒。切点都落在两句旁白之间 |
| `free.py` | 在每张原稿页面图里找最大的 16:9 空白区 |
| `place.py` | 把片段缩到空白区的 90%，放在空白区正中 → `free.json` |
| `build.js` | pptxgenjs 生成整份课件（主题、版式、分节、讲稿） |
| `build-v3.js` | v3 儿童版（8 岁以下）：前 14 页相同，最后三页换成“谁的零件多 / 新能源车越来越多 / 帮地球种树” → `汽油车vs电动车-小学科学-v3.pptx` |
| `build-v3-nv.js` | v3 无解说版：同 v3，但全部视频换成 `*_subtitles-only.mp4`（去掉人声，保留字幕和音效），片段按同样的起止时间重切到 `clips-nv/` → `汽油车vs电动车-小学科学-v3-无解说.pptx` |
| `split.py` → `build-v4.js` | v4：封面标题“新能源车肚子里的秘密”；11 个零件页拆成插画 + 标题（原图像素）+ 对话框（可编辑文字，小学版说法），重新排版：插画占满高度，另一栏上放视频、下放对话框。`VARIANT=nv` 出无解说版，否则出有解说版 |
| `build-v4.1.js` | v4.1：同 v4，但去掉两段完整视频——“第一站 / 第二站”页改成车的静态图 + 三个问题，视频只留在各零件页（每份约 36MB）。同样用 `VARIANT=nv` 出无解说版 |
| `build-v4.2.js` | v4.2：同 v4.1，但零件页对话框改成关键词（第一行“这个是 X”，下面 2–4 行关键词 / 步骤 / 箭头）。同样用 `VARIANT=nv` 出无解说版 |
| `build-v4.3.js` + `speech-v4.3.json` | v4.3 无解说版：页面同 v4.2；每页备注开头换成“流畅上台版”演讲稿（演示者视图里可见），原来的老师参考放在“不用念”分隔线下面 |
| `icon-*.png` | 课件里的小汽车和小树图标（放进 `img/` 使用） |
| `fullscreen.py` | 给每个零件页的小视频加上“单击播放 + 全屏播放”的动画时序 |

运行时的工作目录还需要：`img/`（两份原稿 PPT 每页导出的 2560×1440 图片和备注，以及最后一页用的小汽车图标 `icon-ev.png` / `icon-grey.png`）、`clips/`（按 `clips.tsv` 用 ffmpeg 从 `deliverables/*_narrated.mp4` 切出的 1280×720 片段和封面），以及三段完整视频 `gas-car.mp4`、`electric-car.mp4`、`compare.mp4`。原稿图片不在仓库里。

```bash
python3 free.py car1 … ev7 && python3 place.py
NODE_PATH=node_modules SKILL=<pptx skill 目录> node build.js
python3 fullscreen.py 汽油车vs电动车-小学科学.pptx
```

切好的片段也单独放在 `deliverables/clips/`，可以直接插到别的课件里。
