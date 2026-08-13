export interface TooltipProps {
  text: React.ReactNode;
  side?: "top" | "bottom" | "right";
  children: React.ReactNode;
}
export function Tooltip(props: TooltipProps): JSX.Element;
