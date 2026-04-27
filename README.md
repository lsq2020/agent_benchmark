# Benchmark Hub

统一的 benchmark 网站，合并了 `CGT` 和 `Protein` 两个赛道。用户可在同一站点内切换赛道、分别提交题目、审核题目和导出题库。

## 快速启动

```bash
cd /data/siqing/2026_workpalce/20260421_proteinmaster/webapp_benchmark
bash start.sh
bash start.sh 8080
```

首次启动会自动安装依赖，并在本地创建 `backend/benchmark_bench.db`。

本地打开：

```bash
http://localhost:5000
```

## 合并后的实现方式

- 前端只有一套页面，顶部增加 `CGT / Protein` 赛道切换。
- 后端只有一套 Flask API，通过请求头 `X-Track` 区分当前赛道。
- 数据库使用一张 `benchmark_questions` 表，通过 `track` 字段隔离两类数据。
- 每个赛道有独立的标题、领域、难度说明、占位提示和导出文件名前缀。

## 目录结构

```text
webapp_benchmark/
├── backend/
│   ├── app.py
│   ├── bench_config.py
│   ├── db.py
│   ├── validators.py
│   ├── export_utils.py
│   ├── requirements.txt
│   └── benchmark_bench.db
├── static/
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── app.js
│       └── constants.js
├── render.yaml
├── start.sh
└── README.md
```

## API 约定

- `GET /api/meta`：返回当前赛道配置和全部赛道列表
- `GET /api/stats`：返回当前赛道统计
- `GET /api/questions`：返回当前赛道题目
- `POST /api/questions`：在当前赛道下提交题目
- `POST /api/questions/<id>/review`：审核当前赛道题目
- `GET /api/questions/export?format=xlsx|json|md`：导出当前赛道已通过题目

请求头：

- `X-Role`: `submitter` 或 `reviewer`
- `X-User-Name`: 当前用户姓名
- `X-Track`: `cgt` 或 `protein`

## 部署说明

- 本地默认 SQLite，文件为 `backend/benchmark_bench.db`
- 生产环境建议配置 `DATABASE_URL` 使用 Postgres
- 默认表名为 `benchmark_questions`
- Render 配置已更新为 `benchmark-hub`

## Render 部署

### 方式 1：直接用仓库里的 `render.yaml`

1. 把 `webapp_benchmark` 推到 GitHub。
2. 在 Render 里选择 `Blueprint`。
3. 选中仓库后，Render 会读取 [render.yaml](/data/siqing/2026_workpalce/20260421_proteinmaster/webapp_benchmark/render.yaml)。
4. 会创建：
   - `benchmark-hub` Web Service
   - `benchmark-hub-db` Postgres

默认配置：

```bash
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

### 方式 2：手动创建

1. 新建一个 Render Postgres。
2. 新建一个 Python Web Service。
3. Build Command 填：

```bash
pip install -r backend/requirements.txt
```

4. Start Command 填：

```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT
```

5. 环境变量至少配置：

```bash
DATABASE_URL=<your-postgres-url>
TABLE_NAME=benchmark_questions
PYTHON_VERSION=3.12.4
```

## 上线检查

- 打开 `/api/health`，应返回 `{"status":"ok" ...}`。
- 打开首页后，顶部应能切换 `CGT` 和 `Protein`。
- 分别在两个赛道提交 1 条测试题，确认统计互不影响。
- Render 日志里应看到 `Database backend: Postgres; table: benchmark_questions`。

## 旧表迁移

如果 `cgt_questions` 和 `benchmark_questions` 在同一个 Postgres，可以直接执行：

```bash
cd backend
python migrate_legacy_tables.py --source cgt
```

只看将迁入多少条、不实际写入：

```bash
cd backend
python migrate_legacy_tables.py --source cgt --dry-run
```

同时迁移 `cgt_questions` 和 `protein_questions`：

```bash
cd backend
python migrate_legacy_tables.py --source all
```

## 生产建议

- 不要把本地 `backend/*.db` 文件提交到仓库。
- 生产环境只用 Postgres，不要依赖 Render 本地磁盘保存 SQLite。
- 如果后续要接真实登录，再把当前 `X-Role` / `X-User-Name` 头部方案替换成正式鉴权。
