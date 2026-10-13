// 全片色板。规则：整幅画面几乎全是冷色；暖色只允许出现在三处——
//   1. 那盏灯   2. 火堆   3. 小石头的红围巾
// 其他角色（含皮肤、衣服、兔子的鼻子）全部用冷色或纸白，不得使用暖色。
export const C = {
  // 墨线
  ink: '#1a1f3f',
  inkSoft: '#2d3763',
  graphite: '#5a6794', // 起稿辅助线

  // 夜空 / 水彩
  skyTop: '#0b1537',
  skyMid: '#172a5e',
  skyLow: '#2c4887',
  skyHaze: '#5a77b3',
  dawnTop: '#8fb2d6',
  dawnLow: '#dbe9f2',

  // 雪地
  snow: '#f3f6fd',
  snowLit: '#fbfdff',
  snowShade: '#bccae6',
  snowDeep: '#8da3cf',

  // 树林剪影
  treeFar: '#33487f',
  treeMid: '#1f2f66',
  treeNear: '#111a42',

  // 角色（冷色）
  paper: '#f7f9ff', // 皮肤 / 白色毛 = 纸白
  fur: '#fbfcff',
  shade: '#6b80b4', // 阴影：一层淡淡的蓝灰
  jacket: '#4d5a9a', // 小石头的棉衣：冷色（见 README：与“暖色只有三处”冲突时取后者）
  jacketShade: '#35407a',
  pants: '#2b3560',
  hair: '#1f2547',
  bag: '#5f7fa6',
  bagShade: '#3f5a85',
  nosePink: '#cfa6cf', // 偏紫的冷粉，只在兔子鼻尖一点点
  shellA: '#5d8a8f', // 乌龟壳：青灰
  shellB: '#7aa6a3',
  shellMap: '#2f5c6b',
  antlerWash: '#c9d6ef',
  wolf: '#8e9bb8',
  wolfShade: '#5d6a8d',
  coatTeal: '#3d6a78',
  coatSlate: '#44527f',
  coatBlue: '#7d96c4',
  moss: '#5f9a8c',
  grass: '#6fb39a',
  grassDeep: '#3f7f78',
  water: '#9fc3e4',
  waterDeep: '#6a96cc',
  ice: '#d6e8f7',
  iceDeep: '#8fb5d8',
  stone: '#6c7aa3',
  stoneDark: '#3c4772',
  cave: '#2a3563',
  caveLight: '#47568f',

  // —— 暖色（只给灯、火、红围巾）——
  lampCore: '#fff0b8',
  lampMid: '#ffcb62',
  lampOuter: '#ff9d3a',
  fireCore: '#ffe07a',
  fireMid: '#ff9f40',
  fireOuter: '#e8602b',
  scarf: '#c8323e',
  scarfShade: '#8f1f33',
};

export const W = 1920;
export const H = 1080;
