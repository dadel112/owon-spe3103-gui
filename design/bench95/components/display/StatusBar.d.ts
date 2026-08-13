export interface StatusPane {
  text?: React.ReactNode;
  icon?: React.ReactNode;
  width?: number;
  grow?: string;
  tone?: "default" | "danger";
}
export interface StatusBarProps {
  panes?: Array<string | StatusPane>;
  style?: React.CSSProperties;
}
export function StatusBar(props: StatusBarProps): JSX.Element;
