import { VIDEO } from "../style/theme";
import { buildDrive } from "./mechanics";
import { buildTimeline, type VoiceTiming } from "./timeline";
import timing from "./voice-timing.json";

/** Built once per bundle; pure data derived from the narration timing. */
export const GAS_TL = buildTimeline(timing as VoiceTiming, VIDEO.fps);
export const GAS_DRIVE = buildDrive(GAS_TL);
