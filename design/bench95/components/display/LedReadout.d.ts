export interface LedReadoutProps {
  value: number | string;
  unit?: string;
  /** small pixel caption inside the well, e.g. "OUTPUT VOLTAGE" */
  label?: string;
  color?: "green" | "amber" | "red";
  size?: "sm" | "md" | "lg";
  /** fixed decimals when value is a number */
  digits?: number;
  /** dim the digits: instrument output disabled */
  off?: boolean;
  style?: React.CSSProperties;
}
export function LedReadout(props: LedReadoutProps): JSX.Element;
