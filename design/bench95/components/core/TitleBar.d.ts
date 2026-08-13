export interface TitleBarProps {
  title: string;
  /** icon name shown at the left of the bar */
  icon?: string;
  /** inactive bars go grey and lose the gradient */
  active?: boolean;
  /** "classic" = navy→blue horizontal, "xp" = 22px vertical blue */
  variant?: "classic" | "xp";
  buttons?: Array<"minimize" | "maximize" | "close">;
  onButton?: (button: string) => void;
  children?: React.ReactNode;
}
export function TitleBar(props: TitleBarProps): JSX.Element;
