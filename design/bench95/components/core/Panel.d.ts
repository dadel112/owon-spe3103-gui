export interface PanelProps {
  /** group-box caption that breaks the top rule */
  label?: string;
  /** draw the 1px frame sunken instead of raised */
  inset?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
}
export function Panel(props: PanelProps): JSX.Element;
