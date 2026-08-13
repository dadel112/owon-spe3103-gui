export interface ButtonProps {
  children?: React.ReactNode;
  icon?: string;
  onClick?: () => void;
  disabled?: boolean;
  /** the black 1px ring on the Enter-key button */
  isDefault?: boolean;
  /** hold the bevel inverted (latched toggle) */
  pressed?: boolean;
  size?: "sm" | "md" | "lg";
  block?: boolean;
  style?: React.CSSProperties;
}
export function Button(props: ButtonProps): JSX.Element;
