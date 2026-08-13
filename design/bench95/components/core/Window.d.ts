export interface WindowProps {
  /** omit entirely for a frame with no caption bar */
  title?: string;
  icon?: string;
  active?: boolean;
  variant?: "classic" | "xp";
  buttons?: Array<"minimize" | "maximize" | "close">;
  onButton?: (button: string) => void;
  width?: number | string;
  height?: number | string;
  /** adds the classic 8px dialog gutter around children */
  padded?: boolean;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}
export function Window(props: WindowProps): JSX.Element;
