# 课件生成脚本

`deliverables/汽油车vs电动车-小学科学.pptx` 由这里的脚本生成。

| 文件 | 作用 |
|---|---|
| `clips.tsv` | 每个零件页对应的视频片段：页面、来源（gas/ev）、起点秒、终点秒、封面帧秒。切点都落在两句旁白之间 |
| `free.py` | 在每张原稿页面图里找最大的 16:9 空白区 |
| `place.py` | 把片段缩到空白区的 90%，放在空白区正中 → `free.json` |
| `build.js` | pptxgenjs 生成整份课件（主题、版式、分节、讲稿） |
| `fullscreen.py` | 给每个零件页的小视频加上“单击播放 + 全屏播放”的动画时序 |

运行时的工作目录还需要：`img/`（两份原稿 PPT 每页导出的 2560×1440 图片和备注，以及最后一页用的小汽车图标 `icon-ev.png` / `icon-grey.png`）、`clips/`（按 `clips.tsv` 用 ffmpeg 从 `deliverables/*_narrated.mp4` 切出的 1280×720 片段和封面），以及三段完整视频 `gas-car.mp4`、`electric-car.mp4`、`compare.mp4`。原稿图片不在仓库里。

```bash
python3 free.py car1 … ev7 && python3 place.py
NODE_PATH=node_modules SKILL=<pptx skill 目录> node build.js
python3 fullscreen.py 汽油车vs电动车-小学科学.pptx
```

切好的片段也单独放在 `deliverables/clips/`，可以直接插到别的课件里。
