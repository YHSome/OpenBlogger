"""
GitHubActivity 插件 — 近七天 GitHub 活动记录抓取工具。

用法:
    from OpenBlogger.Plugins.GitHubActivity.fetch import fetch
    fetch(user="YHSome", force=True)   # force=True 绕过 10 分钟缓存
或在构建时自动抓取（每次渲染一次）:
    python -m OpenBlogger.cli build --theme aurora --force
"""

__version__ = "1.0.0"
