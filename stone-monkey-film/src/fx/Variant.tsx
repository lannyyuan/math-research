import {createContext, useContext} from 'react';

/** 画面的“光照版本”：night 夜色（靛蓝）；lit 被光照到的地方（柔和的自然色）；day 灯还亮着的白天；dawn 灯亮之后的晨光 */
export type Variant = 'night' | 'lit' | 'day' | 'dawn';
export const VariantCtx = createContext<Variant>('night');
export const useVariant = () => useContext(VariantCtx);

/** 审计用：chars=false 时不画角色、道具和一切“会动的东西”（只留背景和光），用来检查暖色和字幕带 */
export const CharsCtx = createContext(true);
