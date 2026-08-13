export interface MenuItem { label: string; shortcut?: string; disabled?: boolean }
export interface Menu { label: string; items?: Array<MenuItem | "-"> }
export interface MenuBarProps {
  menus?: Menu[];
  onSelect?: (menu: string, item: string) => void;
  style?: React.CSSProperties;
}
export function MenuBar(props: MenuBarProps): JSX.Element;
