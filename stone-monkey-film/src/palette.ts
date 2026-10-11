export const W = 1920;
export const H = 1080;
// 夜色色板（第一部到灯亮之前）：深夜 / 靛蓝 / 灰蓝 / 纸白 / 墨
export const C = {night: '#121A2E', indigo: '#1E2A44', mid: '#5A6B86', paper: '#EFE8D8', ink: '#2A2622'};
// 暖色只出现在：宝珠的光、龟甲的眼睛、篝火和火种、奶奶的红头绳/红布包、小姑娘的红裙；其余一律灰金/土黄/降饱和
export const WARM = {pearl: '#F3D98A', fire: '#E8873A', red: '#B8382E', dawnRed: '#E9A38C', dawnPurple: '#9C86B8', greyGold: '#cfc29a'};
/** 字幕带的上沿（画面 y）：任何角色、关键动作都不许越过这条线（两行字幕的带最高，约 y≥850） */
export const BAND_TOP = 845;
/** 龟甲（手掌大的石猴）相对于石娃的身高比例：三寸 ≈ 手掌，约 1/8 ~ 1/7 */
export const HOUZI_RATIO = 0.135;
