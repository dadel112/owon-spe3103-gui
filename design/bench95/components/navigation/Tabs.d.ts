export interface TabItem { value: string; label: string }
export interface TabsProps {
  tabs?: Array<string | TabItem>;
  value?: string;
  onChange?: (value: string) => void;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
}
export function Tabs(props: TabsProps): JSX.Element;
