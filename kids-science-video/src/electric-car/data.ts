import type { VoiceTiming } from "../lib/narration";
import { VIDEO } from "../style/theme";
import { buildEvDrive } from "./mechanics";
import { buildEvTimeline } from "./timeline";
import timing from "./voice-timing.json";

export const EV_TL = buildEvTimeline(timing as VoiceTiming, VIDEO.fps);
export const EV_DRIVE = buildEvDrive(EV_TL);
