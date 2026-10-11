import {createContext, useContext} from 'react';

/** 画面的“光照版本”：night 夜色（靛蓝）；lit 被光照到的地方（柔和的自然色）；day 灯还亮着的白天；dawn 灯亮之后的晨光 */
export type Variant = 'night' | 'lit' | 'day' | 'dawn';
export const VariantCtx = createContext<Variant>('night');
export const useVariant = () => useContext(VariantCtx);

/** 审计用：2 = 全画；1 = 不画角色（只留背景、光和发光的道具：宝珠、篝火、红布包），用来检查暖色；0 = 角色、道具、动作一概不画（只留背景和光），用来检查“字幕带里没有压角色” */
export const CharsCtx = createContext<number>(2);
