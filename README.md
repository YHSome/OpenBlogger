# OpenBlogger

一个轻量级静态博客渲染引擎。Markdown 写文章，Python 一键生成完整站点。

## 快速开始

```bash
git clone --recurse-submodules https://github.com/YHSome/yhsome.github.io.git
cd yhsome.github.io
pip install -r requirements.txt
双击 控制台.bat → [3] 本地预览
```

## 项目结构

```
OpenBlogger/
├── renderer.py              # 核心渲染引擎
├── cli.py                   # 命令行工具
├── import_legacy.py         # Hexo 旧博客导入工具
├── Template/Default/        # HTML 模板（6 页）
│   ├── Homepage.html        # 首页：三栏布局 + 弹幕
│   ├── Directory.html       # 目录：搜索 + 标签过滤 + 年月分组
│   ├── Post.html            # 文章：侧栏 + 正文 + 评论
│   ├── Tag.html             # 标签：悬停展开文章列表
│   ├── Projects.html        # 项目：GitHub 仓库展示
│   └── Links.html           # 友链：旧项目导航
└── Plugins/Viewer/          # 内置插件
    ├── js/                  # 访问计数 + 评论系统
    └── tools/               # 页面编号管理
```

## 功能

| 功能 | 说明 |
|------|------|
| Markdown 渲染 | extra/codehilite/toc/sane_lists/smarty 扩展 |
| 元数据解析 | 文章头部 `key: value` 格式，自动补全日期/标题 |
| 增量构建 | 文件哈希缓存，只重建变更页面 |
| RSS + Sitemap | 自动生成 |
| 暗色模式 | 零闪屏（head 同步脚本） |
| 页面转场 | CSS cubic-bezier 弹入飞出 |
| 代码高亮 | Pygments |
| 友链项目 | 构建时自动复制 |
| 弹幕 | 全站评论滚动 |

## 模板变量

所有模板使用 Jinja2 语法。以下是各页面可用的主要变量：

**Post.html**
```
{{ title }} {{ date }} {{ tags }} {{ content }} {{ author }}
{{ prev_post }} {{ next_post }} {{ relative_root }}
{{ total_posts }} {{ total_words }} {{ sidebar_tags }}
{{ page_id }} {{ viewer_user }} {{ viewer_secret }}
```

**Homepage.html**
```
{{ site_title }} {{ site_description }}
{{ recent_posts }} {{ all_tags }} {{ total_posts }} {{ total_words }}
{{ max_page_id }} {{ relative_root }}
```

**Directory.html**
```
{{ all_posts }} {{ all_tags }} {{ active_tag }}
```

**Tag.html**
```
{{ tags_with_count }}  ← 含 posts 列表用于悬停弹出
```

**Projects.html**
```
{{ projects }}  ← 从 projects.json 加载
```

**Links.html**
```
{{ link_sections }}  ← 硬编码在 renderer 中
```

## Aurora 主题（新增）

`template/Aurora/` 是一套全新的现代化渲染模板，使用 Jinja2 模板继承
（`base.html` + 7 个页面 + 404 页），一处修改全站生效。

### 启用

```bash
python -m OpenBlogger.cli build --theme aurora --force
```

也可以在 `site.json` 中把 `"theme"` 改为 `"aurora"` 后直接 `python -m OpenBlogger.cli build`。

### 特性

| 页面 | 亮点 |
|------|------|
| 全局 base | 极光动态背景、毛玻璃导航、深浅色模式（深色下粒子/噪点自动降级）、滚动显现、阅读进度环返回按钮、打印样式、SEO/OG 元数据、无障碍跳转链接、系统"减少动效"支持、中文排版字体栈与抗锯齿优化 |
| 首页 | 渐变 Hero + 时段问候 + 打字机标语轮播、即时搜索（关键词高亮）、最近 6 篇卡片（含字数/阅读时长徽标）、精选项目、侧栏统计/按年归档/标签/动态 |
| 目录 | 搜索高亮、最近搜索记忆（localStorage）、标签/年份/日期筛选（pushState + 浏览器前进后退恢复）、按年归档卡片（迷你柱状图 + 点击联动筛选 + aria-pressed）、随机一篇、年份/月份导航、可交互日历、分批加载 |
| 标签 | 字号标签云、手风琴分区、一键全部展开/收起、URL 深链自动展开并高亮标签云 |
| 文章 | 面包屑导航、阅读进度条、自动目录（桌面侧栏 + 移动折叠）、相关阅读（共享标签推荐 + 最近文章兜底）、分享浮层（原生分享/复制/X/QQ/微博/Telegram）、图片灯箱与懒加载、代码复制、标题锚点、阅读时长、彩色评论头像 |
| 资源 | GitHub 项目卡片（搜索 + 语言筛选叠加 + Star 排序 + 随机项目 + 结果计数）、工具链接网格、GitHub 时间线 |
| 友链 | 分组卡片（圆形头像）、搜索 + 分组筛选联动、结果计数 |
| 更新动态 | 每次渲染强制重新抓取 GitHub 活动（force 绕过 10 分钟缓存，失败沿用旧数据）、概览统计、事件类型 + 仓库双筛选（组合生效、日期分组联动隐藏）、侧栏仓库列表与筛选双向联动（◎ 只看此仓库）、渐变时间线、分批展开 |
| 404 | 渐变大字 404 页面，一键返回首页/目录/标签 |

### 说明

- 需要渲染器支持 `Error.html`（renderer.py 已内置 404 输出映射，其他主题没有该模板时自动跳过，不影响旧主题）。
- 主题不依赖任何外部 CDN/字体，纯 HTML + CSS + 原生 JS。

## 插件系统

插件放在 `Plugins/` 目录（博客项目根），与 OpenBlogger 框架分离。

内置插件：
- **Viewer** (`OpenBlogger/Plugins/Viewer/`)：纯前端访问计数 + 评论，基于 TinyWebDB

博客专属插件示例：
- **GitHubProjects** (`Plugins/GitHubProjects/`)：拉取 GitHub 仓库列表展示

## CLI 命令

```bash
python -m OpenBlogger.cli build                # 构建站点
python -m OpenBlogger.cli build --force        # 强制全量重建
python -m OpenBlogger.cli build --theme modern # 使用指定主题
python -m OpenBlogger.cli serve                # 预览站点
python -m OpenBlogger.cli serve --port 9090    # 指定端口
python -m OpenBlogger.cli clean                # 清空输出
```

## 部署

```bash
# 将 Rendered/ 推送到 GitHub Pages
git subtree push --prefix Rendered origin gh-pages
```

或使用博客项目自带的 `deploy.bat` 一键部署。

## 依赖

- Python 3.9+
- markdown
- Jinja2
- Pygments
- beautifulsoup4（仅 import_legacy.py 需要）
- html2text（仅 import_legacy.py 需要）

## 许可

MIT
