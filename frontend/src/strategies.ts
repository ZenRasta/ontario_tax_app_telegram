export interface StrategyOption {
  code: string;
  label: string;
}

export const strategies: StrategyOption[] = [
  { code: 'BF', label: 'Bracket-Filling' },
  { code: 'GM', label: 'Gradual Meltdown' },
  { code: 'E65', label: 'Early RRIF @65' },
  { code: 'CD', label: 'CPP/OAS Delay' },
  { code: 'SEQ', label: 'Spousal Equalisation' },
  { code: 'IO', label: 'Interest-Offset Loan' },
  { code: 'LS', label: 'Lump-Sum Withdrawal' },
  { code: 'EBX', label: 'Empty-by-X' },
  { code: 'MIN', label: 'RRIF Minimum Only' },
];
