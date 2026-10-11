import React from 'react';
import {S0} from './S0';
import {S1} from './S1';

export const SCENE_COMPS: Record<string, React.FC<{len: number}>> = {
  's0-title': S0,
  's1-dark': S1,
};
