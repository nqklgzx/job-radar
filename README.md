# 生物医学工程 × 嵌入式招聘雷达

基于 [Jasmine-Liu-min/job-radar](https://github.com/Jasmine-Liu-min/job-radar) 定制，保留原抓取、去重、审核导入、投递看板与静态工作台。

- 仓库：https://github.com/nqklgzx/job-radar ，部署分支 `main`
- 在线工作台：https://nqklgzx.github.io/job-radar/
- 首屏：高匹配；支持今日新增、全部岗位、嵌入式/MCU、医疗电子/硬件、深圳/大湾区、2027/2028届、即将截止。
- 不自动投递，不需要 VPS，本地关机不影响 GitHub Actions。

## 匹配与数据边界

`config/profiles.json` 使用上游已有字段和画像键 `ai-data-product`，键保留以兼容现有代码，画像内容已改为医疗嵌入式方向。

九类方向：嵌入式软件、固件/MCU、BSP/Driver、Embedded Linux、医疗电子、硬件研发、FPGA/DSP、医学信号处理、其他生医工研发。

沿用数值评分，不是百分制：80 分及以上且有目标角色标签进入高匹配；目标岗位名、技能、医工行业、公司及城市加分。深圳/广州/东莞/珠海优先，其他城市保留。销售/运营/Java/Web 等按标题降权，混合研发岗不因“售后”二字被删除。无目标角色岗位最多 59 分。

C 语言须有明确编程语境，CAN 等英文技能按词边界匹配。2027/2028届只按招聘文本识别；无明确届别留空。普通实习不标为暑期。学历保留来源描述，未设置个人学历硬筛选。

去重主键仍为规范化公司＋岗位＋城市，URL 参数不同但主键相同可合并。未知公司别名不做模糊合并；跨源公司全称/简称差异仍可能重复，保留人工检查。抓取失败的来源保留旧数据，信源健康显示失败与抓取量异常。

## 自动运行

| 文件 | 工作流 | 北京时间 |
|---|---|---|
| `.github/workflows/sync.yml` | `job-radar-sync` | 每日 07:00 快扫 |
| `.github/workflows/slow.yml` | `job-radar-slow` | 周三、周日 09:47 慢源补扫 |
| `.github/workflows/pages.yml` | `job-radar-pages` | 同步成功或展示代码更新后部署 |

定时使用 `timezone: Asia/Shanghai`。快扫不安装浏览器，慢扫安装 Playwright Chromium。两条数据工作流共用并发组，避免同时写回冲突。云端 Python 3.12；Pages 把 `data/jobs.html` 打包到 `public/index.html`，由 Actions 发布。

手动刷新：仓库 `Actions → job-radar-sync → Run workflow → main → Run workflow`。慢源同理。健康页必须结合工作流结果查看：工作流成功不代表所有网站都成功。

## 本地 Windows

本次使用已安装 Python 3.10，核心仅标准库，无需 Node。建议隔离环境；中文 requirements 文件使用 UTF-8 模式：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -X utf8 -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 -m playwright install chromium
.\.venv\Scripts\python.exe -X utf8 scripts/sync_plan.py fast
.\.venv\Scripts\python.exe -X utf8 scripts/sync_plan.py slow
.\.venv\Scripts\python.exe -X utf8 scripts/sync_plan.py rescore
.\.venv\Scripts\python.exe -X utf8 scripts/smoke_test.py
.\.venv\Scripts\python.exe -X utf8 scripts/send_notify.py --dry-run
```

工作台：`data/jobs.html`，直接双击打开。投递状态/备注在浏览器 localStorage，不提交到仓库。

## 信源维护

`config/sources.csv` 是正式信源，复用国家大学生就业平台、国聘、央企公告、高校就业网、官网与 ATS、牛客/实习僧。接口、登录墙、反爬导致的失败显示在健康页，不绕过验证码。

已复用雅培 Workday，新增 Philips 官方公开招聘源。Philips 参数来自官方招聘页 `tenant`/`siteId`，并实际验证公开 API。其它医疗企业登记在 `config/source_backlog.csv`；`research` 表示待接入，不代表已覆盖官网。空 URL 表示尚未核实。

| 要调整什么 | 真实文件 |
|---|---|
| 画像关键词、地区、推送最低分 | `config/profiles.json` |
| 主动搜索词 | `config/role_keywords.json`（沿用既有组键） |
| 分类、公司优先级 | `job_radar/role_rules.py` |
| 评分权重 | `job_radar/score.py` |
| 来源/公司官网 | `config/sources.csv` |
| 待核实企业 | `config/source_backlog.csv` |
| 校招/实习阶段 | `job_radar/workbench_rules.py` |
| 工作台 | `scripts/export_html.py` |
| 推送筛选 | `scripts/notify_preview.py` |
| 发送通道 | `scripts/send_notify.py` |
| 定时 | `.github/workflows/sync.yml`、`slow.yml` |

保留牛客/公众号/就业群审核导入：

```powershell
python -X utf8 scripts/nowcoder_discover.py --limit-per-keyword 6 --replace
python -X utf8 scripts/import_feed.py --preset nowcoder --text data/inbox/nowcoder_discovered.txt --review-html data/import_preview_nowcoder.html
python -X utf8 scripts/import_feed.py --review-json job_import_review.json
```

## 可选推送

未配置 webhook 时只生成 `data/notify_preview.md`，不会真实发送。新增日期按北京时间判断，已过期及已推送项跳过；发送成功后才写 `data/notify_state.json`。现有发送器支持飞书、企业微信，未实现 Email。

要启用推送：仓库 `Settings → Secrets and variables → Actions → New repository secret`，添加已有名称 `FEISHU_WEBHOOK_URL` 或 `WECHAT_WEBHOOK_URL`（别名 `WECOM_WEBHOOK_URL`）。不要把 webhook 发到公开仓库。`.env` 已忽略，但本项目不自动加载它；本地通过环境变量设置。

Pages 设置：`Settings → Pages → Build and deployment → Source → GitHub Actions`。本次已通过 API 配置。

## 维护约定

核心数据流：`sources.csv → adapter RawJob → normalize → dedup → industry/role/score → jobs.json → export_html.py → jobs.html`。

`data/jobs.json` 是当前岗位库，`data/jobs_archive.json` 为下线归档，`data/health_report.json` 与 `data/source_state.json` 保存健康状况。未推送机制继续使用原有 `dedup_key`，不更改历史主键。不得把学历未知、日期缺失或泛研发描述解读成已确认符合申请资格。
