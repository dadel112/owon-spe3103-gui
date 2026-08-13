export interface SelectOption { value: string; label: string }
export interface SelectProps {
  value?: string;
  options?: Array<string | SelectOption>;
  onChange?: (value: string) => void;
  disabled?: boolean;
  width?: number;
  style?: React.CSSProperties;
}
export function Select(props: SelectProps): JSX.Element;
