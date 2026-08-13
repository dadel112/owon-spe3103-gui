export interface LedProps {
  on?: boolean;
  color?: "green" | "amber" | "red";
  label?: React.ReactNode;
  /** 530ms stepped blink for alarms */
  blink?: boolean;
  size?: number;
  style?: React.CSSProperties;
}
export function Led(props: LedProps): JSX.Element;
