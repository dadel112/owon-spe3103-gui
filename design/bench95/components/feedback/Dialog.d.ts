export interface DialogProps {
  title?: string;
  kind?: "info" | "warning" | "error" | "question";
  message?: React.ReactNode;
  detail?: React.ReactNode;
  buttons?: string[];
  defaultButton?: string;
  onButton?: (button: string) => void;
  width?: number;
  children?: React.ReactNode;
}
export function Dialog(props: DialogProps): JSX.Element;
