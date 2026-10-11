import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Stage, Layer} from '../fx/Stage';
import {GroundShadow, Sprite} from '../fx/Sprite';
import {PearlGlow, FireGlow} from '../fx/Light';
import {LampLight} from '../fx/LampLight';
import {VariantCtx, Variant} from '../fx/Variant';
import {Bg, PaperOverlay, at} from '../scenes/kit';
import {Houzi, Pair, KID_S} from '../scenes/cast';

// 绘本补充插图 plate/*（webapp/PLATES.md 的 16 个 key）：每个 key = 现成背景板 + 现成人物精灵拼出来的一个小场景。
// 世界坐标同影片：地面线 y=832；相机固定在 at(cx, cy)，只出 1920×1080 的一帧。
const GY = 832;

const P: React.FC<{n: string; x: number; s?: number; flip?: boolean; y?: number; f?: string; o?: number; rot?: number}> = ({n, x, s = 0.84, flip, y = GY + 4, f, o, rot}) => (
  <>
    <GroundShadow x={x} y={y + 2} rx={70 * (s / 0.84)} o={0.4 * (o ?? 1)} />
    <Sprite name={n} x={x} y={y} s={s} flip={flip} filter={f} opacity={o} rot={rot} breathe={0} sway={0} />
  </>
);
/** 灯：暖黄的圆点 + 光晕 */
const Lamp: React.FC<{x: number; y: number; r?: number; red?: boolean}> = ({x, y, r = 9, red}) => (
  <>
    <FireGlow x={x} y={y} r={r * 9} o={0.7} />
    <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', background: red ? '#B8382E' : '#f3d98a', boxShadow: `0 0 ${r * 2}px ${r}px rgba(243,217,138,0.6)`}} />
  </>
);
const Box: React.FC<{x: number; y: number; w: number; h: number; c: string; o?: number; r?: number; rot?: number}> = ({x, y, w, h, c, o = 1, r = 3, rot = 0}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, background: c, opacity: o, borderRadius: r, transform: `rotate(${rot}deg)`, border: '2px solid rgba(42,38,34,0.55)'}} />
);
/** 三层视差背景 + 前景内容；w/h 是背景板的尺寸，cx/cy 是相机中心（世界坐标） */
const Scene: React.FC<{cx: number; cy?: number; z?: number; far: string; mid?: string; near?: string; w?: number; h?: number; children?: React.ReactNode; behind?: React.ReactNode}> = ({cx, cy = 540, z = 1, far, mid, near, w = 2900, h = 1080, children, behind}) => (
  <Stage cam={at(cx, cy, z)}>
    <Layer p={0.3} w={w} h={h}><Bg name={far} /></Layer>
    {mid && <Layer p={0.62} w={w} h={h}><Bg name={mid} /></Layer>}
    <Layer p={1} w={w} h={h}>
      {near && <Bg name={near} />}
      {behind}
      {children}
    </Layer>
  </Stage>
);
const Sit: React.FC<{x: number; y: number; flip?: boolean}> = ({x, y, flip = true}) => (
  <>
    <Sprite name="shiwa_side_leg" x={x} y={y} s={KID_S} flip={flip} rot={-84} breathe={0} sway={0} />
    <Sprite name="shiwa_side_up" x={x} y={y} s={KID_S} flip={flip} breathe={0} sway={0} />
  </>
);

type Recipe = {v: Variant; mirror?: boolean; el: () => React.ReactNode};

const RECIPES: Record<string, Recipe> = {
  // 夜里的江边：小桥横在中景，石娃坐在岸边石头上，龟甲蹲在他膝头
  river_night: {v: 'night', el: () => (
    <Scene cx={1100} cy={760} far="river_far" mid="river_mid" near="river_near" h={1500}
      behind={<Bg name="river_bridge_low" />}>
      <GroundShadow x={640} y={GY} rx={110} o={0.45} />
      <Sit x={640} y={GY - 22} flip={false} />
      <Houzi view="side" kid={KID_S} x={700} y={GY - 22 - 44} flip sway={0} />
      <Box x={742} y={GY - 40} w={26} h={22} c="#c9bfa3" r={4} />
      <Box x={774} y={GY - 36} w={22} h={20} c="#c9bfa3" r={4} />
    </Scene>
  )},
  // 夜里山路上的老人：左边石娃走上山，右边砍木的老人举着一把老刀
  hill_night: {v: 'night', el: () => (
    <Scene cx={1250} far="hill_far" mid="hill_mid" near="hill_near">
      <P n="herder_front" x={1700} s={0.95} />
      <div style={{position: 'absolute', left: 1618, top: GY - 330, width: 12, height: 150, background: 'linear-gradient(90deg,#8d949b,#d3d7da,#8d949b)', border: '2px solid rgba(42,38,34,0.6)', borderRadius: 4, transform: 'rotate(-16deg)', transformOrigin: '50% 100%'}} />
      <Pair x={720} y={GY + 4} walk={0} />
    </Scene>
  )},
  // 地下的石城：黑暗、洞口、深色人影、守门老人的灯、小姑娘递来一颗小石子
  stone_city: {v: 'night', el: () => (
    <>
      <Scene cx={1450} far="gate_far" mid="gate_mid" near="gate_near">
        <P n="villager1" x={1180} s={0.88} f="brightness(0.28)" />
        <P n="villager3" x={1300} s={0.95} f="brightness(0.28)" />
        <P n="villager2" x={1420} s={0.85} f="brightness(0.28)" flip />
        <P n="villager4" x={1560} s={0.9} f="brightness(0.28)" />
        <P n="herder_front" x={2090} s={0.9} flip />
        <Lamp x={2020} y={GY - 210} r={11} />
        <P n="girl_front" x={2330} s={0.84} flip />
        <div style={{position: 'absolute', left: 2295, top: GY - 120, width: 12, height: 10, borderRadius: '50%', background: '#a7a29a'}} />
        <Pair x={820} y={GY + 4} />
        <PearlGlow x={880} y={GY - 120} r={90} o={0.7} />
      </Scene>
      <AbsoluteFill style={{background: 'rgba(8,12,24,0.38)', mixBlendMode: 'multiply'}} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}><path d="M40 0 L420 0 L450 40 L380 70 L420 130 L330 150 L270 120 L190 160 L120 100 L60 70 Z" fill="#05070d" /></svg>
    </>
  )},
  // 家家点灯的小村（夜）：整幅左右镜像一次，让奶奶的门在右边
  village_lamps: {v: 'night', mirror: true, el: () => (
    <>
      <Scene cx={1300} far="village_far" mid="village_mid" near="village_near">
        <P n="nainai_front_red" x={691} s={KID_S * 1.03} />
        <FireGlow x={691} y={GY - 150} r={150} o={0.6} />
        <P n="shiwa_side" x={1900} s={0.5} flip />
        {[760, 900, 1040, 1180, 1320, 1460, 1600, 1740, 1880].map((x, i) => <Lamp key={i} x={x} y={600 + 40 * Math.sin(i * 0.7)} r={7} />)}
        <P n="villager1" x={1180} s={0.88} /><Lamp x={1215} y={GY - 160} r={8} />
        <P n="villager3" x={1330} s={0.95} flip /><Lamp x={1290} y={GY - 130} r={8} />
        <P n="kid1" x={1470} s={0.84} /><Lamp x={1500} y={GY - 150} r={8} />
      </Scene>
    </>
  )},
  // 主城的街口、市集与擂台（夜）
  gate_night: {v: 'night', el: () => (
    <Scene cx={1450} far="gate_far" mid="gate_mid" near="gate_near">
      <div style={{position: 'absolute', left: 640, top: GY - 70, width: 110, height: 50, borderRadius: '50%', border: '6px solid #6b6f73', background: '#1b2433'}} />
      <Box x={690} y={GY - 120} w={26} h={34} c="#8a7c68" />
      <P n="kid1" x={820} s={0.84} />
      <P n="guard_front" x={1290} s={0.7} /><P n="guard_front" x={1710} s={0.7} flip />
      <Box x={1010} y={GY - 52} w={200} h={40} c="#8a7c68" /><Box x={1790} y={GY - 52} w={200} h={40} c="#8a7c68" />
      {[1040, 1090, 1140, 1830, 1880, 1930].map((x, i) => <div key={i} style={{position: 'absolute', left: x, top: GY - 76, width: 30, height: 24, borderRadius: '50%', background: '#b6a37d', border: '2px solid rgba(42,38,34,0.5)'}} />)}
      <P n="villager1" x={1100} s={0.88} y={GY - 40} /><P n="villager3" x={1880} s={0.95} y={GY - 40} flip />
      <Box x={2060} y={GY - 70} w={300} h={70} c="#7a6650" />
      <P n="guard_front" x={2210} s={0.9} y={GY - 66} />
      <div style={{position: 'absolute', left: 2250, top: GY - 520, width: 14, height: 250, background: '#7a6650', border: '2px solid rgba(42,38,34,0.6)', borderRadius: 6, transform: 'rotate(18deg)', transformOrigin: '50% 100%'}} />
      <P n="villager2" x={2120} s={0.85} flip /><P n="villager4" x={2400} s={0.9} />
      <Pair x={1480} y={GY + 4} />
    </Scene>
  )},
  // 王宫大殿：国王、官员、卫士，石娃在台阶下仰头；金鼓放右下
  hall_king: {v: 'night', el: () => (
    <Scene cx={1200} far="hall_king_far" near="hall_king_near" w={2400}>
      <P n="king_seated" x={1200} y={640} s={0.85} />
      <P n="official_front" x={820} s={0.8} /><P n="guard_front" x={560} s={0.7} /><P n="guard_front" x={1840} s={0.7} flip />
      <P n="official_front" x={1580} s={0.8} flip />
      <P n="shiwa_front" x={1200} y={GY + 160} s={0.7} />
      <Houzi view="front" kid={0.7} x={1200 + 28} y={GY + 160 - 255} glow={0.7} sway={0} />
      <P n="drum" x={1900} y={GY + 190} s={0.55} />
      {[820, 1200, 1580].map((x, i) => <P key={i} n="guard_front" x={x} y={GY + 255} s={0.62} />)}
    </Scene>
  )},
  // 农家灶间（室内）：灶台、小桌、火盆边围坐的孩子，右边一张小床
  kitchen: {v: 'lit', el: () => (
    <Scene cx={1200} far="kitchen_far" near="kitchen_near" w={2400}>
      <P n="nainai_front" x={620} s={KID_S * 1.03} />
      <FireGlow x={1850} y={GY - 20} r={250} o={0.7} />
      <Sprite name="fire" x={1850} y={GY + 4} s={0.42} breathe={0} sway={0} v="lit" />
      <P n="kid1" x={1700} s={0.78} /><P n="kid2" x={1990} s={0.8} flip /><P n="girl_front" x={1590} s={0.8} /><P n="shiwa_front" x={2100} s={0.84} flip />
      <Box x={2120} y={GY - 130} w={250} h={60} c="#8a7c68" r={6} /><Box x={2130} y={GY - 170} w={230} h={44} c="#9aa3b3" r={14} />
    </Scene>
  )},
  // 村子白天：水田、稻草人、先生和孩子、村口的怪石和老树
  village_day: {v: 'day', el: () => (
    <Scene cx={1450} far="village_far" mid="village_mid" near="village_near">
      <Box x={540} y={GY - 6} w={420} h={80} c="#a9c0c9" o={0.85} r={30} />
      <div style={{position: 'absolute', left: 1040, top: GY - 150, width: 6, height: 150, background: '#6d5a40', transform: 'rotate(6deg)'}} />
      <div style={{position: 'absolute', left: 1000, top: GY - 130, width: 86, height: 6, background: '#6d5a40'}} />
      <P n="villager2" x={760} s={0.85} y={GY + 20} />
      <P n="official_front" x={1280} s={0.8} /><Box x={1360} y={GY - 270} w={110} h={150} c="#efe8d8" r={6} />
      <P n="kid1" x={1180} s={0.8} /><P n="kid3" x={1420} s={0.8} flip /><P n="kid2" x={1500} s={0.78} />
      <P n="kid1" x={1880} s={0.8} flip /><P n="kid3" x={2030} s={0.8} />
      <Box x={1790} y={GY - 70} w={42} h={60} c="#a8a49a" r={4} />
    </Scene>
  )},
  // 老树下的老人：坐姿的石娃，孩子们围着听，远客对坐，枝上挂一盏灯，一弯月
  elder_tree: {v: 'dawn', el: () => (
    <>
      <Scene cx={1900} far="village_far" mid="village_mid" near="village_near">
        <Sit x={2040} y={GY - 22} />
        <Houzi view="front" kid={KID_S} x={2040 - 92} y={GY - 30} sway={0} />
        <P n="kid2" x={1790} s={0.8} /><P n="kid1" x={1660} s={0.78} /><P n="herder_front" x={2420} s={0.8} flip />
        <Box x={2190} y={GY - 40} w={34} h={30} c="#b6a37d" r={8} /><Box x={2250} y={GY - 24} w={14} h={14} c="#efe8d8" r={4} /><Box x={2160} y={GY - 24} w={14} h={14} c="#efe8d8" r={4} />
        <Lamp x={2330} y={430} r={13} />
      </Scene>
      <AbsoluteFill style={{background: 'rgba(30,42,68,0.62)', mixBlendMode: 'multiply'}} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <defs><mask id="moonm"><rect width={1920} height={1080} fill="white" /><circle cx={1708} cy={150} r={42} fill="black" /></mask></defs>
        <circle cx={1672} cy={166} r={46} fill="#efe8d8" mask="url(#moonm)" />
      </svg>
    </>
  )},
  // 大江上的桥：桥上过往的人，水里露出大鱼的背，左下渡船和老渔夫
  bridge_day: {v: 'lit', el: () => (
    <Scene cx={1450} cy={780} far="river_far" mid="river_mid" near="river_near" h={1500} behind={<Bg name="river_bridge_high" />}>
      <P n="villager1" x={1250} s={0.85} /><P n="villager3" x={1390} s={0.9} /><P n="kid1" x={1470} s={0.8} /><P n="villager2" x={1600} s={0.85} flip />
      <Sprite name="fish_side" x={1480} y={1340} s={1.1} breathe={0} sway={0} />
      <P n="girl_side" x={2020} s={0.84} flip /><P n="villager4" x={2120} s={0.9} flip /><P n="kid3" x={2190} s={0.8} flip />
      <div style={{position: 'absolute', left: 520, top: 1070, width: 300, height: 56, borderRadius: '0 0 150px 150px', background: '#8a7c68', border: '3px solid rgba(42,38,34,0.6)'}} />
      <Sprite name="herder_side" x={680} y={1080} s={0.6} breathe={0} sway={0} />
      <Sprite name="bird_up" x={790} y={1030} s={1.1} breathe={0} sway={0} v="day" />
    </Scene>
  )},
  // 城里街市：城门口的摊桌、摊主和买主，红裙姑娘和官员走过
  gate_day: {v: 'lit', el: () => (
    <Scene cx={1450} far="gate_far" mid="gate_mid" near="gate_near">
      <Box x={760} y={GY - 56} w={190} h={42} c="#a39371" /><Box x={1040} y={GY - 56} w={190} h={42} c="#a39371" />
      {[790, 840, 890, 1070, 1120, 1170].map((x, i) => <div key={i} style={{position: 'absolute', left: x, top: GY - 82, width: 32, height: 26, borderRadius: '50%', background: '#c4b48c', border: '2px solid rgba(42,38,34,0.5)'}} />)}
      <P n="villager1" x={850} s={0.88} y={GY - 30} /><P n="villager3" x={1130} s={0.95} y={GY - 30} flip /><P n="villager2" x={700} s={0.85} />
      <P n="girl_front" x={1780} s={0.84} /><P n="official_front" x={1930} s={0.8} flip /><P n="villager4" x={2150} s={0.9} flip /><P n="kid3" x={2260} s={0.8} />
    </Scene>
  )},
  // 山路（白天）：小姑娘牵着小马，货郎和被孩子牵着的老人
  hill_day: {v: 'lit', el: () => (
    <Scene cx={1400} far="hill_far" mid="hill_mid" near="hill_near">
      <P n="girl_side" x={640} s={0.84} /><P n="horse_side" x={900} s={0.55} />
      <P n="herder_front" x={1700} s={0.8} />
      <div style={{position: 'absolute', left: 1580, top: GY - 360, width: 250, height: 8, background: '#6d5a40', transform: 'rotate(-6deg)'}} />
      <Box x={1560} y={GY - 330} w={50} h={60} c="#a39371" /><Box x={1800} y={GY - 350} w={50} h={60} c="#a39371" />
      <P n="oldwoman_front" x={2020} s={0.95} /><P n="kid2" x={2130} s={0.8} flip />
    </Scene>
  )},
  // 出海的商船：木船、鼓起的白帆，石娃和龟甲、两个船员，远处小岛，海鸥
  shore_ship: {v: 'lit', el: () => (
    <Scene cx={1650} far="shore_far" mid="shore_mid">
      <div style={{position: 'absolute', left: 1030, top: 770, width: 480, height: 90, borderRadius: '0 0 240px 240px', background: '#8a7c68', border: '3px solid rgba(42,38,34,0.65)'}} />
      <div style={{position: 'absolute', left: 1264, top: 330, width: 8, height: 450, background: '#6d5a40'}} />
      <svg width={2900} height={1080} style={{position: 'absolute', left: 0, top: 0}}><path d="M1278 340 Q1470 520 1280 740 Z" fill="#efe8d8" stroke="#2a2622" strokeWidth={2.5} opacity={0.97} /></svg>
      <Sprite name="shiwa_side" x={1180} y={776} s={0.5} breathe={0} sway={0} />
      <Houzi view="side" kid={0.5} x={1180 + 7} y={776 - 124} flip sway={0} />
      <Sprite name="villager1" x={1360} y={776} s={0.5} breathe={0} sway={0} /><Sprite name="villager2" x={1430} y={776} s={0.5} flip breathe={0} sway={0} />
      <Sprite name="bird_up" x={1100} y={300} s={1.2} breathe={0} sway={0} /><Sprite name="bird_down" x={1540} y={240} s={1.2} breathe={0} sway={0} /><Sprite name="swallow_up" x={1760} y={330} s={1.1} breathe={0} sway={0} />
    </Scene>
  )},
  // 天上的灯：大半幅天空，天灯（太阳）在中上方，几只鸟飞过
  lamp_sky: {v: 'dawn', el: () => (
    <>
      <Scene cx={1450} far="lamp_sky_far">
        <div style={{position: 'absolute', left: 0, top: 0, width: 2900, height: 1080, WebkitMaskImage: 'linear-gradient(to bottom, transparent 62%, #000 82%)', maskImage: 'linear-gradient(to bottom, transparent 62%, #000 82%)'}}><VariantCtx.Provider value="day"><Bg name="village_far" /></VariantCtx.Provider></div>
        {[[800, 460, 'bird_up'], [980, 400, 'bird_down'], [1130, 500, 'bird_up'], [1790, 380, 'swallow_down'], [1950, 430, 'swallow_up'], [2090, 360, 'bird_down']].map(([x, y, n], i) => <Sprite key={i} name={n as string} x={x as number} y={y as number} s={1.3} breathe={0} sway={0} />)}
      </Scene>
      <LampLight x={960} y={250} k={0.92} t={0} w={1920} h={1080} />
    </>
  )},
  // 村里过节、灯会：戏台、提灯的孩子、红灯笼、系满红纸条的大树
  village_festival: {v: 'lit', el: () => (
    <Scene cx={1500} far="village_far" mid="village_mid" near="village_near">
      <Box x={800} y={GY - 120} w={320} h={120} c="#8a7c68" r={4} />
      <P n="villager2" x={900} s={0.7} y={GY - 120} /><P n="villager4" x={1030} s={0.7} y={GY - 120} flip />
      {[[1360, 'kid1'], [1500, 'kid3'], [1640, 'girl_flower'], [1780, 'kid2']].map(([x, n], i) => (
        <React.Fragment key={i}><P n={n as string} x={x as number} s={0.82} /><Lamp x={(x as number) + 38} y={GY - 150 + (i % 2) * 14} r={11} red={i % 2 === 0} /></React.Fragment>
      ))}
      <P n="villager1" x={1230} s={0.88} y={GY + 20} /><P n="villager3" x={1900} s={0.95} y={GY + 20} flip />
      {[680, 760, 1180].map((x, i) => <Lamp key={i} x={x} y={470} r={14} red />)}
      {Array.from({length: 26}, (_, i) => <Box key={i} x={2040 + (i * 53) % 260} y={360 + (i * 37) % 190} w={10} h={26} c="#B8382E" o={0.92} r={1} rot={(i * 11) % 30 - 15} />)}
      <P n="kid2" x={2230} s={0.8} flip />
    </Scene>
  )},
  // 暴雨与河堤：黑云、闪电、涨水，堤上的人扛沙袋、石娃搬石头
  storm_river: {v: 'lit', el: () => (
    <>
      <Scene cx={1450} cy={700} far="river_far" mid="river_mid" near="river_near" h={1500}>
        <P n="villager1" x={1180} s={0.88} flip /><P n="villager2" x={1330} s={0.85} flip /><P n="villager4" x={1480} s={0.9} flip />
        {[1160, 1320, 1470].map((x, i) => <div key={i} style={{position: 'absolute', left: x - 30, top: GY - 250 + i * 6, width: 60, height: 36, borderRadius: '50%', background: '#a39371', border: '2px solid rgba(42,38,34,0.55)'}} />)}
        <Pair x={1700} y={GY + 4} />
        <div style={{position: 'absolute', left: 1736, top: GY - 150, width: 70, height: 50, borderRadius: '45% 55% 40% 60%', background: '#7c8588', border: '2px solid rgba(42,38,34,0.6)'}} />
      </Scene>
      <AbsoluteFill style={{background: 'linear-gradient(to bottom, rgba(10,14,24,0.9) 0%, rgba(14,20,34,0.62) 40%, rgba(20,28,44,0.3) 100%)'}} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        <path d="M1180 0 L1120 170 L1190 190 L1090 380 L1210 330 L1150 470" fill="none" stroke="#f3ecd2" strokeWidth={6} strokeLinejoin="round" />
        <path d="M1180 0 L1120 170 L1190 190 L1090 380 L1210 330 L1150 470" fill="none" stroke="#fffdf0" strokeWidth={2.4} strokeLinejoin="round" />
        {Array.from({length: 70}, (_, i) => <line key={i} x1={(i * 97) % 1920} y1={(i * 53) % 700} x2={((i * 97) % 1920) - 12} y2={((i * 53) % 700) + 46} stroke="#cfd8e0" strokeWidth={1.4} opacity={0.4} />)}
      </svg>
    </>
  )},
};

export const PLATE_KEYS = Object.keys(RECIPES);

export const Plate: React.FC<{which: string}> = ({which}) => {
  const r = RECIPES[which];
  if (!r) return <AbsoluteFill style={{background: '#c00'}} />;
  return (
    <AbsoluteFill style={{background: '#0c1222'}}>
      <div style={{position: 'absolute', inset: 0, transform: r.mirror ? 'scaleX(-1)' : undefined}}>
        <VariantCtx.Provider value={r.v}>{r.el()}</VariantCtx.Provider>
      </div>
      <PaperOverlay />
    </AbsoluteFill>
  );
};
