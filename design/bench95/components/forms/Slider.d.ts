export interface SliderProps {
  value?: number;
  min?: number;
  max?: number;
  step?: number;
  onChange?: (value: number) => void;
  /** number of tick marks under the track; 0 hides them */
  ticks?: number;
  disabled?: boolean;
  width?: number;
  style?: React.CSSProperties;
}
export function Slider(props: SliderProps): JSX.Element;
