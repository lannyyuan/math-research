import React, { createContext, useContext } from "react";

/**
 * Opacity multiplier for everything below it — used to ghost parts that are
 * not in focus (e.g. the radiator in front of the engine close-up) while
 * keeping them visible.
 */
const FadeCtx = createContext(1);
export const useFade = () => useContext(FadeCtx);
export const Fade: React.FC<{ readonly value: number; readonly children: React.ReactNode }> = ({ value, children }) => {
  const parent = useFade();
  return <FadeCtx.Provider value={parent * value}>{children}</FadeCtx.Provider>;
};
