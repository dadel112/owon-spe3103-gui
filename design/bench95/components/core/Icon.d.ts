export interface IconProps {
  /** pixelarticons icon name, e.g. "power", "zap", "save" */
  name: string;
  /** px; use multiples of 8 for crisp pixels (16 is the UI default) */
  size?: number;
  /** hex colour; omit for the default black glyph */
  color?: string;
  title?: string;
  style?: React.CSSProperties;
}
export function Icon(props: IconProps): JSX.Element;
