declare module "react-chartjs-2" {
  import React from "react";
  import { ChartData, ChartOptions } from "chart.js";

  export interface LineProps {
    data: ChartData<"line", number[], unknown>;
    options?: ChartOptions<"line">;
  }

  export const Line: React.FC<LineProps>;
}
