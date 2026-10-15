import { Config } from "@remotion/cli/config";

// Headless Linux/CI has no GPU: SwiftShader-backed ANGLE renders WebGL deterministically on the CPU.
Config.setChromiumOpenGlRenderer("swangle");
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(95);
// PowerPoint-friendly MP4: H.264 High, yuv420p, AAC
Config.setCodec("h264");
Config.setCrf(17);
Config.setPixelFormat("yuv420p");
Config.setAudioCodec("aac");
Config.setAudioBitrate("192k");
Config.setConcurrency(4);
