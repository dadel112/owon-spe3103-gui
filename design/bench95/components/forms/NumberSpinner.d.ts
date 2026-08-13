export interface NumberSpinnerProps {
  value: number;
  onChange?: (value: number) => void;
  step?: number;
  min?: number;
  max?: number;
  /** fixed decimal places — 3 for volts, 3 for amps */
  decimals?: number;
  /** unit suffix rendered inside the well, e.g. "V" */
  unit?: string;
  disabled?: boolean;
  width?: number;
  style?: React.CSSProperties;
}
export function NumberSpinner(props: NumberSpinnerProps): JSX.Element;
