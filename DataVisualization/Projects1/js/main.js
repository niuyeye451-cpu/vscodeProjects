// 1. 常量与配置
const MEDAL_COLORS = { gold: "#e8c547", silver: "#9aa8bc", bronze: "#c17f4a" };
const baseTextStyle = { color: "#b8c5d8", fontFamily: "Noto Sans SC, sans-serif" };

// 2. 初始化 ECharts 实例
const charts = {
  stacked: echarts.init(document.getElementById("chart-stacked"), null, { renderer: "canvas" }),
  pie: echarts.init(document.getElementById("chart-pie"), null, { renderer: "canvas" }),
  bar: echarts.init(document.getElementById("chart-bar"), null, { renderer: "canvas" })
};

// 3. 数据解析函数
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    const parts = line.split(",");
    if (parts.length < 7) continue;
    
    rows.push({
      rank: parseInt(parts[0], 10),
      country: parts[1],
      gold: parseInt(parts[2], 10),
      silver: parseInt(parts[3], 10),
      bronze: parseInt(parts[4], 10),
      total: parseInt(parts[5], 10),
      flag: parts.slice(6).join(",")
    });
  }
  return rows;
}

// 4. 渲染图表核心函数
function renderCharts(data) {
  const top10 = data.slice(0, 10);
  const top8 = data.slice(0, 8);
  const top12 = data.slice(0, 12);

  // 渲染顶部数据卡片
  let sumG = 0, sumS = 0, sumB = 0;
  top10.forEach(r => {
    sumG += r.gold;
    sumS += r.silver;
    sumB += r.bronze;
  });
  
  document.getElementById("sum-gold").textContent = String(sumG);
  document.getElementById("sum-silver").textContent = String(sumS);
  document.getElementById("sum-bronze").textContent = String(sumB);
  document.getElementById("country-count").textContent = String(data.length);

  const countries10 = top10.map(r => r.country);

  // 渲染堆叠柱状图
  charts.stacked.setOption({
    backgroundColor: "transparent",
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: "rgba(12, 18, 34, 0.92)", borderColor: "rgba(120, 160, 220, 0.3)", textStyle: { color: "#e8edf5" } },
    legend: { data: ["金牌", "银牌", "铜牌"], bottom: 8, textStyle: baseTextStyle, itemGap: 16 },
    grid: { left: "3%", right: "4%", bottom: "18%", top: "8%", containLabel: true },
    xAxis: { type: "category", data: countries10, axisLabel: { ...baseTextStyle, rotate: countries10.length > 8 ? 28 : 0, interval: 0 }, axisLine: { lineStyle: { color: "rgba(120, 160, 220, 0.25)" } } },
    yAxis: { type: "value", name: "枚", nameTextStyle: baseTextStyle, splitLine: { lineStyle: { color: "rgba(120, 160, 220, 0.12)" } }, axisLabel: baseTextStyle },
    series: [
      { name: "金牌", type: "bar", stack: "medals", itemStyle: { color: MEDAL_COLORS.gold }, data: top10.map(r => r.gold) },
      { name: "银牌", type: "bar", stack: "medals", itemStyle: { color: MEDAL_COLORS.silver }, data: top10.map(r => r.silver) },
      { name: "铜牌", type: "bar", stack: "medals", itemStyle: { color: MEDAL_COLORS.bronze, borderRadius: [4, 4, 0, 0] }, data: top10.map(r => r.bronze) }
    ]
  });

  // 渲染饼图
  charts.pie.setOption({
    backgroundColor: "transparent",
    tooltip: { trigger: "item", formatter: "{b}<br/>奖牌数：{c} ({d}%)", backgroundColor: "rgba(12, 18, 34, 0.92)", borderColor: "rgba(120, 160, 220, 0.3)", textStyle: { color: "#e8edf5" } },
    legend: { type: "scroll", orient: "vertical", right: "2%", top: "middle", textStyle: { ...baseTextStyle, fontSize: 11 } },
    series: [{
      name: "奖牌占比", type: "pie", radius: ["38%", "62%"], center: ["40%", "50%"],
      itemStyle: { borderRadius: 6, borderColor: "#0c1222", borderWidth: 2 },
      label: { show: true, formatter: "{b}\n{d}%", color: "#d0dae8", fontSize: 11 },
      data: top8.map(r => ({ name: r.country, value: r.total }))
    }],
    color: ["#5b9bd5", "#e8c547", "#70ad47", "#ed7d31", "#9e7cc9", "#4472c4", "#ffc000", "#91a437"]
  });

  // 渲染横向条形图
  charts.bar.setOption({
    backgroundColor: "transparent",
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: "rgba(12, 18, 34, 0.92)", borderColor: "rgba(120, 160, 220, 0.3)", textStyle: { color: "#e8edf5" } },
    grid: { left: "3%", right: "8%", bottom: "3%", top: "3%", containLabel: true },
    xAxis: { type: "value", splitLine: { lineStyle: { color: "rgba(120, 160, 220, 0.12)" } }, axisLabel: baseTextStyle },
    yAxis: { type: "category", data: top12.map(r => r.country).reverse(), axisLabel: baseTextStyle, axisLine: { lineStyle: { color: "rgba(120, 160, 220, 0.25)" } } },
    series: [{
      name: "奖牌总数", type: "bar",
      data: top12.map(r => r.total).reverse(),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: "#3d6fa8" }, { offset: 1, color: "#5b9bd5" }
        ]),
        borderRadius: [0, 6, 6, 0]
      },
      label: { show: true, position: "right", color: "#b8c5d8", formatter: "{c}" }
    }]
  });
}

// 5. 主程序启动逻辑
async function initApp() {
  // 监听窗口缩放
  window.addEventListener("resize", () => {
    Object.values(charts).forEach(chart => chart.resize());
  });

  try {
    const res = await fetch("medals_countries.csv");
    if (!res.ok) throw new Error(`无法加载 CSV（HTTP ${res.status}）`);
    const text = await res.text();
    const data = parseCSV(text);
    
    if (!data.length) throw new Error("CSV 解析结果为空");
    renderCharts(data);
  } catch (err) {
    const el = document.getElementById("load-error");
    el.classList.add("visible");
    el.textContent = `加载失败：${err.message || String(err)}。请使用本地服务器打开本目录（例如：npx serve 或 VS Code Live Server）。`;
  }
}

// 启动
initApp();