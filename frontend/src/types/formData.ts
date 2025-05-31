
// Shared wizard data contract used across components
export interface FormData {
  /* personal */
  age: number;
  rrspBalance: number;
  tfsaBalance: number;
  cppAmount: number;
  oasAmount: number;
  desiredSpending: number;
  expectedReturn: number;
  stdDevReturn: number;
  horizon: number;

  /* marital */
  married: boolean;
  spouseAge?: number;
  spouseRrspBalance?: number;
  spouseTfsaBalance?: number;
  spouseCppAmount?: number;
  spouseOasAmount?: number;

  /* advanced */
  bracketFillCeiling?: number;
  cppStartAge?: number;
  lumpSumAmount?: number;
  lumpSumYear?: number;
  emptyByAge?: number;

  /* wizard meta */
  goal: string; // UI label ("Maximize Spending"…)
  strategies: string[]; // array of strategy codes ["BF", "GM", …]
}

