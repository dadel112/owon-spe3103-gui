export interface ProgressBarProps {
  value?: number;
  max?: number;
  /** 20 discrete navy chunks (the era's look); false = solid fill */
  chunky?: boolean;
  height?: number;
  label?: React.ReactNode;
  style?: React.CSSProperties;
}
export function ProgressBar(props: ProgressBarProps): JSX.Element;
