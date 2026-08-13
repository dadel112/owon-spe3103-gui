export interface TaskBarProps {
  startLabel?: string;
  tasks?: Array<string | { label: string; icon?: string }>;
  activeTask?: string;
  onTask?: (label: string) => void;
  onStart?: () => void;
  /** icon names shown in the tray */
  tray?: string[];
  clock?: string;
  style?: React.CSSProperties;
}
export function TaskBar(props: TaskBarProps): JSX.Element;
