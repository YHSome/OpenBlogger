# -*- coding: utf-8 -*-
"""Aurora theme QA (run from any cwd; starts its own local server)."""
import http.server
import json
import os
import re
import socketserver
import threading
import time
import urllib.parse
import functools

from playwright.sync_api import sync_playwright

ROOT = r'C:\Users\YHSome\Projects\OtherProjects\Blog\Rendered'
PORT = 8099
KEY = '\u7ea2\u697c\u68a6'          # 红楼梦
MARK = '\u7ea2\u697c'               # 红楼


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    time.sleep(0.5)
    base = f'http://127.0.0.1:{PORT}/'
    report = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append('PAGEERROR: ' + str(e)[:120]))
        page.on('console', lambda m: errors.append('CONSOLE: ' + m.text[:120]) if m.type == 'error' else None)

        # ── 目录页：搜索红楼梦 ──
        page.goto(base + 'directory.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(500)
        base_info = page.evaluate('''() => ({
            cards: document.querySelectorAll('#postList .post-card').length,
            hasCard: document.body.innerHTML.indexOf('\\u7ea2\\u697c\\u68a6') > -1
        })''')
        page.fill('#searchInput', MARK)
        page.wait_for_timeout(300)
        search = page.evaluate('''() => ({
            visible: [...document.querySelectorAll('#postList .post-card')]
                .filter(c => !c.classList.contains('hidden')).length,
            marks: document.querySelectorAll('#postList mark').length,
            titles: [...document.querySelectorAll('#postList .post-card:not(.hidden) h3')]
                .map(h => h.textContent.trim())
        })''')
        page.fill('#searchInput', '')
        page.wait_for_timeout(200)

        # ── 目录页：月份跳转与标签筛选 ──
        months = page.evaluate('() => document.querySelectorAll("#monthJump a").length')
        TAG = '\u8bb2\u7a3f\u548c\u5f81\u6587'  # 讲稿和征文
        page.click('#filterBar .filter-chip[data-tag="' + TAG + '"]')
        page.wait_for_timeout(250)
        tag_filter = page.evaluate('''() =>
            [...document.querySelectorAll('#postList .post-card')]
                .filter(c => !c.classList.contains('hidden')).length''')

        # ── 文章页：TOC / 锚点 / 代码复制 ──
        posts = os.listdir(os.path.join(ROOT, 'posts'))
        code_post = None
        for pf in posts:
            html = open(os.path.join(ROOT, 'posts', pf), encoding='utf-8').read()
            if '<div class="codehilite">' in html and re.search(r'<h2 id=', html):
                code_post = pf
                break
        page.goto(base + 'posts/' + urllib.parse.quote(code_post), wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(700)
        post = page.evaluate('''() => ({
            toc: document.querySelectorAll('#tocBox a').length,
            anchors: document.querySelectorAll('.post-body .heading-anchor').length,
            copyBtns: document.querySelectorAll('.post-body .code-copy').length,
            readTime: document.getElementById('readTime').textContent
        })''')
        copy_state = None
        if post['copyBtns']:
            page.click('.post-body .code-copy')
            page.wait_for_timeout(250)
            copy_state = page.evaluate('() => document.querySelector(".post-body .code-copy").textContent')

        # ── 首页搜索 ──
        page.goto(base + 'index.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(400)
        first = page.evaluate('() => document.querySelector("#postList .post-card h2").textContent')
        page.fill('#searchInput', first[:4])
        page.wait_for_timeout(250)
        home_search = page.evaluate('''() => ({
            visible: [...document.querySelectorAll('#postList .post-card')]
                .filter(c => !c.classList.contains('hidden')).length,
            marks: document.querySelectorAll('#postList mark').length
        })''')

        report = {
            'errors': errors,
            'directory_base': base_info,
            'directory_search': search,
            'months': months,
            'tag_filter_visible': tag_filter,
            'post': post,
            'copy_state': copy_state,
            'home_search': home_search,
        }

        # ── 第 4 轮：返回顶部进度环 ──
        page.goto(base + 'directory.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(300)
        page.evaluate('() => window.scrollTo(0, document.documentElement.scrollHeight)')
        page.wait_for_timeout(300)
        ring = page.evaluate('''() => {
            const c = document.querySelector('#backToTop .bt-progress');
            return { visible: document.getElementById('backToTop').classList.contains('visible'),
                     offset: c.style.strokeDashoffset };
        }''')
        report['progress_ring'] = ring

        # ── 资源页语言筛选 ──
        page.goto(base + 'resources.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(400)
        res_filter = page.evaluate('''() => {
            const chips = [...document.querySelectorAll('#projFilter .filter-chip')];
            const counts = chips.map(c => c.dataset.lang);
            return { chips: counts, cards: document.querySelectorAll('.project-grid .res-card').length };
        }''')
        page.click('#projFilter .filter-chip[data-lang="Python"]')
        page.wait_for_timeout(200)
        res_filter_after = page.evaluate('''() =>
            [...document.querySelectorAll('.project-grid .res-card')]
                .filter(c => c.style.display !== 'none').length''')
        report['resources_filter'] = res_filter
        report['resources_filter_python_visible'] = res_filter_after

        # ── 标签页全部展开 ──
        page.goto(base + 'tags.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(400)
        tag_before = page.evaluate('() => document.querySelectorAll(".tag-section.open").length')
        page.click('#tagToggleAll')
        page.wait_for_timeout(300)
        tag_after = page.evaluate('''() => ({
            open: document.querySelectorAll('.tag-section.open').length,
            label: document.getElementById('tagToggleAll').textContent
        })''')
        report['tag_toggle'] = {'before': tag_before, 'after': tag_after}

        # ── 首页问候语 ──
        page.goto(base + 'index.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(300)
        report['greeting'] = page.evaluate('() => document.getElementById("greetBadge").textContent')

        # ── 第 5 轮：404 页面 ──
        import urllib.request as _ur
        try:
            _req = _ur.Request(base + 'nonexistent.html', headers={'Connection': 'close'})
            with _ur.urlopen(_req, timeout=10) as _r:
                _status = _r.status
        except Exception:
            _status = 404
        page.goto(base + '404.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(300)
        report['error_page'] = {
            'status': _status,
            'code': page.evaluate('() => document.querySelector(".error-code").textContent'),
            'buttons': page.evaluate('() => document.querySelectorAll(".error-btn").length'),
        }

        # ── 年份筛选 ──
        page.goto(base + 'directory.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(400)
        year_chips = page.evaluate('() => [...document.querySelectorAll("#yearBar .filter-chip")].map(c => c.dataset.year + ":" + c.textContent.trim())')
        page.click('#yearBar .filter-chip[data-year="2026"]')
        page.wait_for_timeout(250)
        year_visible = page.evaluate('''() =>
            [...document.querySelectorAll('#postList .post-card')]
                .filter(c => !c.classList.contains('hidden')).length''')
        report['year_filter'] = {'chips': year_chips, 'visible_2026': year_visible}

        # ── 资源页 Star 排序 ──
        page.goto(base + 'resources.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(400)
        before_order = page.evaluate('''() =>
            [...document.querySelectorAll('.project-grid .res-card .res-name')].map(e => e.textContent.trim()).slice(0, 3)''')
        page.click('#projSort')
        page.wait_for_timeout(250)
        after_order = page.evaluate('''() =>
            [...document.querySelectorAll('.project-grid .res-card .res-name')].map(e => e.textContent.trim()).slice(0, 3)''')
        report['star_sort'] = {'before': before_order, 'after': after_order,
                               'label': page.evaluate('() => document.getElementById("projSort").textContent')}

        # ── 第 6 轮：目录阅读百分比 + 表格滚动容器 + 首页引导链接 ──
        page.goto(base + 'posts/' + urllib.parse.quote(code_post), wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(600)
        toc_pct0 = page.evaluate('() => document.getElementById("tocPct").textContent')
        page.evaluate('() => window.scrollTo(0, document.documentElement.scrollHeight / 2)')
        page.wait_for_timeout(300)
        toc_pct_mid = page.evaluate('() => document.getElementById("tocPct").textContent')
        table_wrap = page.evaluate('() => document.querySelectorAll(".post-body .table-wrap").length')
        page.goto(base + 'index.html', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(300)
        all_link = page.evaluate('''() => {
            const a = document.querySelector('.all-posts-link a');
            return a ? a.textContent.trim() : null;
        }''')
        report['toc_pct'] = {'top': toc_pct0, 'mid': toc_pct_mid}
        report['table_wrap'] = table_wrap
        report['all_posts_link'] = all_link

        browser.close()
    httpd.shutdown()
    print(json.dumps(report, ensure_ascii=True, indent=1))


if __name__ == '__main__':
    main()
