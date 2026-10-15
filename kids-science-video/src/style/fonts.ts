import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

/**
 * Bundled, subsetted (GB2312) fonts — built by scripts/build_fonts.py.
 * Loaded once at module import; Remotion waits for them before rendering.
 */
export const fontsReady = Promise.all([
  loadFont({ family: "Noto Sans SC", url: staticFile("fonts/NotoSansSC-500.woff2"), weight: "500" }),
  loadFont({ family: "Noto Sans SC", url: staticFile("fonts/NotoSansSC-700.woff2"), weight: "700" }),
  loadFont({ family: "Noto Sans SC", url: staticFile("fonts/NotoSansSC-900.woff2"), weight: "900" }),
  loadFont({ family: "ZCOOL KuaiLe", url: staticFile("fonts/ZCOOLKuaiLe.woff2"), weight: "400" }),
]);
