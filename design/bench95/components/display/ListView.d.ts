export interface ListColumn { key: string; label: string; width?: number; align?: "left" | "right" | "center" }
export interface ListViewProps {
  columns?: ListColumn[];
  rows?: Array<Record<string, React.ReactNode>>;
  selectedIndex?: number;
  onSelect?: (index: number) => void;
  height?: number | string;
  /** VT323 rows for logs and measurement tables */
  mono?: boolean;
  style?: React.CSSProperties;
}
export function ListView(props: ListViewProps): JSX.Element;
