import React, { useRef, useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import type { EChartsOption } from 'echarts';
import { SCIENTIFIC_COLORS, PUBLICATION_THEME } from '../../types';
import { Download } from 'lucide-react';

interface ScientificChartProps {
  option: EChartsOption;
  height?: number;
  title?: string;
  subtitle?: string;
  caption?: string;
  showToolbox?: boolean;
  onDownload?: () => void;
  className?: string;
  loading?: boolean;
}

export const ScientificChart: React.FC<ScientificChartProps> = ({
  option,
  height = 400,
  title,
  subtitle,
  caption,
  showToolbox = true,
  onDownload,
  className = '',
  loading = false,
}) => {
  const chartRef = useRef<ReactECharts>(null);

  // Merge with publication theme — titles are NEVER rendered on the chart canvas.
  // Titles and subtitles are handled as HTML elements above the chart.
  const mergedOption = useMemo<EChartsOption>(() => ({
    ...PUBLICATION_THEME,
    ...option,
    title: { show: false },
    tooltip: {
      trigger: 'axis',
      ...PUBLICATION_THEME.tooltip,
      ...(option.tooltip as object),
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: SCIENTIFIC_COLORS.neutral,
        },
      },
    },
    toolbox: showToolbox ? {
      feature: {
        saveAsImage: {
          title: 'Export PNG',
          pixelRatio: 3,
          excludeComponents: ['toolbox'],
        },
        dataZoom: {
          title: { zoom: 'Zoom', back: 'Reset' },
        },
        restore: { title: 'Reset' },
      },
      right: 20,
      top: 10,
    } : undefined,
    grid: {
      ...PUBLICATION_THEME.grid,
      ...(option.grid as object),
    },
  }), [option, title, subtitle, showToolbox]);

  const handleDownload = () => {
    if (chartRef.current) {
      const chartInstance = chartRef.current.getEchartsInstance();
      const url = chartInstance.getDataURL({
        type: 'png',
        pixelRatio: 3,
        backgroundColor: '#fff',
      });
      
      const link = document.createElement('a');
      link.download = `${title || 'chart'}_${new Date().toISOString().slice(0, 10)}.png`;
      link.href = url;
      link.click();
    }
    onDownload?.();
  };

  return (
    <div className={`publication-figure ${className}`}>
      {(title || subtitle) && (
        <div className="mb-2">
          {title && (
            <h3 className="text-base font-semibold text-slate-800 dark:text-slate-100">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{subtitle}</p>
          )}
        </div>
      )}
      <div className="relative">
        <ReactECharts
          ref={chartRef}
          option={mergedOption}
          style={{ height: `${height}px` }}
          notMerge={true}
          lazyUpdate={true}
          showLoading={loading}
          loadingOption={{
            text: 'Computing...',
            color: SCIENTIFIC_COLORS.primary,
            textColor: SCIENTIFIC_COLORS.neutral,
            maskColor: 'rgba(255, 255, 255, 0.8)',
          }}
        />
        
        {/* Custom download button */}
        {showToolbox && (
          <button
            onClick={handleDownload}
            className="absolute top-2 right-2 p-2 rounded-lg
              bg-white/80 hover:bg-white shadow-sm
              transition-all hover:shadow-md
              group"
            title="Download high-res PNG"
          >
            <Download className="w-4 h-4 text-slate-500 group-hover:text-primary-500" />
          </button>
        )}
      </div>
      
      {caption && (
        <p className="publication-figure-caption">
          {caption}
        </p>
      )}
    </div>
  );
};

// Preset chart configurations for common use cases
export const createLineChartOption = (
  xData: number[],
  series: Array<{
    name: string;
    data: number[];
    color?: string;
    smooth?: boolean;
    areaStyle?: boolean;
  }>,
  config: {
    xAxisName?: string;
    yAxisName?: string;
    xAxisUnit?: string;
    yAxisUnit?: string;
    markLines?: Array<{ value: number; label: string; color?: string }>;
    markAreas?: Array<{ start: number; end: number; color?: string; label?: string }>;
  } = {}
): EChartsOption => ({
  xAxis: {
    type: 'value',
    name: config.xAxisName ? `${config.xAxisName}${config.xAxisUnit ? ` (${config.xAxisUnit})` : ''}` : undefined,
    nameLocation: 'middle',
    nameGap: 30,
    ...PUBLICATION_THEME.xAxis,
  },
  yAxis: {
    type: 'value',
    name: config.yAxisName ? `${config.yAxisName}${config.yAxisUnit ? ` (${config.yAxisUnit})` : ''}` : undefined,
    nameLocation: 'middle',
    nameGap: 45,
    ...PUBLICATION_THEME.yAxis,
  },
  series: series.map((s, i) => {
    const color = s.color || (Object.values(SCIENTIFIC_COLORS)[i % 8] as string);
    return {
      name: s.name,
      type: 'line' as const,
      data: xData.map((x, j) => [x, s.data[j]]),
      smooth: s.smooth ?? true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: {
        width: 2.5,
        color,
      },
      itemStyle: {
        color,
      },
      areaStyle: s.areaStyle ? {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `${color}40` },
            { offset: 1, color: `${color}05` },
          ],
        },
      } : undefined,
      markLine: config.markLines ? {
        symbol: 'none',
        data: config.markLines.map(ml => ({
          yAxis: ml.value,
          label: {
            formatter: ml.label,
            position: 'end' as const,
          },
          lineStyle: {
            type: 'dashed' as const,
            color: ml.color || SCIENTIFIC_COLORS.danger,
          },
        })),
      } : undefined,
      markArea: config.markAreas ? {
        data: config.markAreas.map(ma => [{
          xAxis: ma.start,
          itemStyle: { color: ma.color || 'rgba(239, 68, 68, 0.1)' },
        }, {
          xAxis: ma.end,
        }]),
      } : undefined,
    };
  }),
  legend: {
    show: series.length > 1,
    top: 5,
    right: 50,
    textStyle: { color: '#475569' },
  },
});

export const createGaugeChartOption = (
  value: number,
  config: {
    min?: number;
    max?: number;
    title?: string;
    unit?: string;
    thresholds?: Array<{ value: number; color: string }>;
  } = {}
): EChartsOption => {
  const { min = 0, max = 100, title, unit, thresholds } = config;
  
  const defaultThresholds = [
    { value: 0.3, color: SCIENTIFIC_COLORS.success },
    { value: 0.7, color: SCIENTIFIC_COLORS.warning },
    { value: 1, color: SCIENTIFIC_COLORS.danger },
  ];

  return {
    series: [{
      type: 'gauge',
      min,
      max,
      progress: { show: true, width: 18 },
      axisLine: {
        lineStyle: {
          width: 18,
          color: (thresholds || defaultThresholds).map(t => [t.value, t.color]),
        },
      },
      axisTick: { show: false },
      splitLine: { length: 10, lineStyle: { width: 2, color: '#999' } },
      axisLabel: { distance: 25, color: '#64748b', fontSize: 11 },
      anchor: { show: true, size: 20, itemStyle: { borderWidth: 2 } },
      pointer: {
        length: '70%',
        width: 6,
        itemStyle: { color: 'auto' },
      },
      title: {
        show: !!title,
        offsetCenter: [0, '70%'],
        fontSize: 14,
        color: '#475569',
      },
      detail: {
        valueAnimation: true,
        fontSize: 28,
        fontWeight: 'bold',
        offsetCenter: [0, '40%'],
        formatter: unit ? `{value} ${unit}` : '{value}',
        color: 'auto',
      },
      data: [{ value, name: title }],
    }],
  };
};

export const createHeatmapOption = (
  xData: string[] | number[],
  yData: string[] | number[],
  data: number[][],
  config: {
    xAxisName?: string;
    yAxisName?: string;
    colorMin?: string;
    colorMax?: string;
  } = {}
): EChartsOption => ({
  tooltip: {
    position: 'top',
    formatter: (params: any) => {
      return `${params.data[0]}, ${params.data[1]}: <strong>${params.data[2].toFixed(2)}</strong>`;
    },
  },
  xAxis: {
    type: 'category',
    data: xData,
    name: config.xAxisName,
    splitArea: { show: true },
  },
  yAxis: {
    type: 'category',
    data: yData,
    name: config.yAxisName,
    splitArea: { show: true },
  },
  visualMap: {
    min: Math.min(...data.flat()),
    max: Math.max(...data.flat()),
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: 10,
    inRange: {
      color: config.colorMin && config.colorMax 
        ? [config.colorMin, config.colorMax]
        : SCIENTIFIC_COLORS.sequential,
    },
  },
  series: [{
    type: 'heatmap',
    data: data.flatMap((row, i) => 
      row.map((val, j) => [xData[j], yData[i], val])
    ),
    label: { show: false },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)',
      },
    },
  }],
});

export default ScientificChart;
