export interface TextFieldProps {
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  align?: "left" | "right" | "center";
  /** VT323 for SCPI commands, addresses, numbers */
  mono?: boolean;
  width?: number | string;
  style?: React.CSSProperties;
}
export function TextField(props: TextFieldProps): JSX.Element;
