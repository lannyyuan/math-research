export interface Cue {text: string; gap?: number; at?: number; d?: number}
export interface Scene {id: string; name?: string; len: number; lead?: number; cues: Cue[]}
export interface Timeline {title: string; fps: number; scenes: Scene[]}
export function norm(t: string): string;
export function words(t: string): number;
export function wrap(text: string, max?: number): string[];
export function minDur(t: string): number;
export function holdDur(t: string): number;
export function schedule(scene: Scene): (Cue & {t: number; d: number})[];
export function sceneStarts(tl: Timeline): number[];
