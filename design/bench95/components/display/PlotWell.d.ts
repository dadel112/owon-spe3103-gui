export interface PlotSeries { points: Array<{ x: number; y: number }>; color?: string; width?: number }
export interface PlotWellProps {
  /** points in 0..1 space, origin bottom-left */
  series?: PlotSeries[];
  height?: number;
  /** grid divisions per axis */
  grid?: number;
  color?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}
export function PlotWell(props: PlotWellProps): JSX.Element;
