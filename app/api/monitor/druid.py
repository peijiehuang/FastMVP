import sys

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.config import settings
from app.db.session import engine

router = APIRouter()


@router.get("/login.html", response_class=HTMLResponse)
async def druid_monitor_page():
    """Database monitoring page replacing Java Druid monitor."""
    import sqlalchemy
    import fastapi

    pool = engine.pool
    # Mask password in display URL
    import re
    display_url = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", str(settings.DATABASE_URL))

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>数据监控 - {settings.APP_NAME}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f0f2f5; margin: 0; padding: 20px; color: #333; }}
.container {{ max-width: 900px; margin: 0 auto; }}
h1 {{ color: #1890ff; border-bottom: 2px solid #1890ff; padding-bottom: 10px; }}
.card {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 20px;
         box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
.card h2 {{ margin-top: 0; color: #333; font-size: 18px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 10px 15px; text-align: left; border-bottom: 1px solid #f0f0f0; }}
th {{ color: #888; font-weight: 500; width: 200px; }}
.badge {{ display: inline-block; padding: 2px 10px; border-radius: 4px;
          background: #e6f7ff; color: #1890ff; font-size: 13px; }}
.badge-green {{ background: #f6ffed; color: #52c41a; }}
.info {{ color: #888; font-size: 13px; margin-top: 10px; }}
</style>
</head>
<body>
<div class="container">
<h1>数据监控 - Python SQLAlchemy</h1>
<div class="card">
  <h2>数据源信息</h2>
  <table>
    <tr><th>数据库类型</th><td>MySQL (aiomysql)</td></tr>
    <tr><th>连接地址</th><td>{display_url}</td></tr>
    <tr><th>ORM 框架</th><td>SQLAlchemy {sqlalchemy.__version__}</td></tr>
  </table>
</div>
<div class="card">
  <h2>连接池状态</h2>
  <table>
    <tr><th>连接池类型</th><td><span class="badge">QueuePool (Async)</span></td></tr>
    <tr><th>连接池大小</th><td>{pool.size()}</td></tr>
    <tr><th>已签出连接</th><td>{pool.checkedout()}</td></tr>
    <tr><th>已签入连接</th><td>{pool.checkedin()}</td></tr>
    <tr><th>溢出连接</th><td>{pool.overflow()}</td></tr>
    <tr><th>池状态摘要</th><td><span class="badge badge-green">{pool.status()}</span></td></tr>
  </table>
</div>
<div class="card">
  <h2>应用信息</h2>
  <table>
    <tr><th>应用名称</th><td>{settings.APP_NAME}</td></tr>
    <tr><th>Python 版本</th><td>{sys.version.split()[0]}</td></tr>
    <tr><th>FastAPI 版本</th><td>{fastapi.__version__}</td></tr>
    <tr><th>调试模式</th><td>{'开启' if settings.DEBUG else '关闭'}</td></tr>
  </table>
</div>
<p class="info">本页面替代 Java 版 Druid 数据源监控，展示 SQLAlchemy 连接池实时状态。刷新页面可获取最新数据。</p>
</div>
</body>
</html>"""
    return HTMLResponse(content=html)
