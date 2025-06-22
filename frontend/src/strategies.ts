
export type GoalEnum =
  | 'minimize_tax'
  | 'maximize_spending'
  | 'preserve_estate'
  | 'simplify';

export type StrategyCodeEnum =
  | 'BF'
  | 'GM'
  | 'E65'
  | 'CD'
  | 'SEQ'
  | 'IO'
  | 'LS'
  | 'EBX'
  | 'MIN';

export interface StrategyMeta {
  code: StrategyCodeEnum;
  label: string;
  blurb: string;
  default_complexity: number;
  typical_goals: GoalEnum[];
}

export const ALL_STRATEGIES: StrategyMeta[] = [
  {
    code: 'BF',
    label: 'Bracket-Filling',
    blurb: 'Cap taxable income at a chosen ceiling.',
    default_complexity: 2,
    typical_goals: ['minimize_tax', 'simplify'],
  },
  {
    code: 'GM',
    label: 'Gradual Meltdown',
    blurb: 'Withdraw just enough each year to meet spending.',
    default_complexity: 1,
    typical_goals: ['maximize_spending', 'simplify'],
  },
  {
    code: 'E65',
    label: 'Early RRIF @65',
    blurb: 'Convert RRSP early for pension credits & income splitting.',
    default_complexity: 2,
    typical_goals: ['minimize_tax'],
  },
  {
    code: 'CD',
    label: 'CPP/OAS Delay',
    blurb: 'Delay government pensions; bridge spending with RRIF.',
    default_complexity: 3,
    typical_goals: ['maximize_spending'],
  },
  {
    code: 'SEQ',
    label: 'Spousal Equalisation',
    blurb: 'Even out taxable income between spouses.',
    default_complexity: 3,
    typical_goals: ['minimize_tax'],
  },
  {
    code: 'IO',
    label: 'Interest-Offset Loan',
    blurb: 'Use deductible interest to offset RRIF tax.',
    default_complexity: 5,
    typical_goals: ['minimize_tax'],
  },
  {
    code: 'LS',
    label: 'Lump-Sum Withdrawal',
    blurb: 'One-time large withdrawal in a specified year.',
    default_complexity: 2,
    typical_goals: ['simplify'],
  },
  {
    code: 'EBX',
    label: 'Empty-by-X',
    blurb: 'Systematically deplete RRIF by a target age.',
    default_complexity: 2,
    typical_goals: ['preserve_estate', 'minimize_tax'],
  },
  {
    code: 'MIN',
    label: 'RRIF Minimum Only',
    blurb: 'Withdraw only the CRA-mandated minimum each year.',
    default_complexity: 1,
    typical_goals: ['simplify', 'preserve_estate'],
  },
];

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
