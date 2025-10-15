import * as React from "react";
import * as RechartsPrimitive from "recharts";
import { cn } from "@/lib/utils";

// Simple chart exports without tooltip content to avoid type issues
export const ChartContainer = RechartsPrimitive.ResponsiveContainer;
export const ChartTooltip = RechartsPrimitive.Tooltip;
export const ChartLegend = RechartsPrimitive.Legend;
export const BarChart = RechartsPrimitive.BarChart;
export const Bar = RechartsPrimitive.Bar;
export const LineChart = RechartsPrimitive.LineChart;
export const Line = RechartsPrimitive.Line;
export const AreaChart = RechartsPrimitive.AreaChart;
export const Area = RechartsPrimitive.Area;
export const PieChart = RechartsPrimitive.PieChart;
export const Pie = RechartsPrimitive.Pie;
export const RadarChart = RechartsPrimitive.RadarChart;
export const Radar = RechartsPrimitive.Radar;
export const XAxis = RechartsPrimitive.XAxis;
export const YAxis = RechartsPrimitive.YAxis;
export const CartesianGrid = RechartsPrimitive.CartesianGrid;
export const Cell = RechartsPrimitive.Cell;
