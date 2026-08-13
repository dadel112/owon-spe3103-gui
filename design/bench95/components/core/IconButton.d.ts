export interface IconButtonProps {
  icon: string;
  /** tooltip / aria-label — always supply one */
  label: string;
  size?: number;
  /** latched state, drawn with the checkered face */
  active?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}
export function IconButton(props: IconButtonProps): JSX.Element;
