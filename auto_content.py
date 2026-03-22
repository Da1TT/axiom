import os
import json
import re
import sys
import time
import urllib.parse
from openai import OpenAI
from datetime import datetime
import random

# ==========================================
# Axiom PropTech - 自动化发文、数据大盘与Sitemap引擎
# ==========================================

api_key = os.environ.get("AI_API_KEY")
api_base = os.environ.get("AI_API_BASE")

if not api_base or api_base.strip() == "":
    api_base = "https://api.moonshot.cn/v1"

if not api_key:
    print("❌ 致命错误：找不到 AI_API_KEY，请检查 GitHub Secrets！")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)

def clean_json_response(text):
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    return text.strip()

def update_sitemap(url_path):
    sitemap_file = 'sitemap.xml'
    # ⚠️ 部署时，请把此处换成你新站的域名
    base_url = "https://axiomproptech.com"
    full_url = f"{base_url}/{url_path}"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    new_url_node = f"""
    <url>
        <loc>{full_url}</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>"""

    if not os.path.exists(sitemap_file):
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>{new_url_node}
</urlset>"""
    else:
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if full_url not in content:
            sitemap_content = content.replace('</urlset>', f'{new_url_node}\n</urlset>')
        else:
            sitemap_content = content

    with open(sitemap_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)


# ---------------------------------------------------------
# 模块一：生成每日全球 6 大枢纽房价大盘并更新主页
# ---------------------------------------------------------
print("\n📊 正在获取每日全球 6 大枢纽房价动态...")
data_prompt = """
You are a Global Real Estate Data Analyst. Provide realistic estimates for today's Average Price per Square Meter (in USD) for premium real estate in major global cities.
Output ONLY a valid JSON object:
{
  "nyc_price": "e.g. $15,200",
  "nyc_trend": "e.g. ↑ +1.2%",
  "london_price": "e.g. $13,500",
  "london_trend": "e.g. ↓ -0.5%",
  "dubai_price": "e.g. $7,800",
  "dubai_trend": "e.g. ↑ +4.5%",
  "tokyo_price": "e.g. $9,100",
  "tokyo_trend": "e.g. ↑ +2.1%",
  "beijing_price": "e.g. $11,500",
  "beijing_trend": "e.g. ↓ -1.0%",
  "singapore_price": "e.g. $16,300",
  "singapore_trend": "e.g. ↑ +0.8%",
  "insight": "Write a 1-sentence sharp insight about global housing market trends today."
}
"""

try:
    data_response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "Output ONLY JSON."},
            {"role": "user", "content": data_prompt}
        ],
        temperature=0.8
    )
    
    market_json = json.loads(clean_json_response(data_response.choices[0].message.content))
    print(f"✅ 大盘数据获取成功！")
    
    # 组装奢华版数据看板 HTML
    new_data_html = f"""
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> New York</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['nyc_price']} <span class="text-[10px] text-rose-400 font-sans font-medium">{market_json['nyc_trend']}</span></p>
                </div>
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> London</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['london_price']} <span class="text-[10px] text-emerald-400 font-sans font-medium">{market_json['london_trend']}</span></p>
                </div>
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> Dubai</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['dubai_price']} <span class="text-[10px] text-rose-400 font-sans font-medium">{market_json['dubai_trend']}</span></p>
                </div>
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> Tokyo</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['tokyo_price']} <span class="text-[10px] text-rose-400 font-sans font-medium">{market_json['tokyo_trend']}</span></p>
                </div>
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> Beijing</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['beijing_price']} <span class="text-[10px] text-emerald-400 font-sans font-medium">{market_json['beijing_trend']}</span></p>
                </div>
                <div class="border-l border-gold/50 pl-4 bg-dark/20 py-2">
                    <p class="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1 flex items-center gap-1"><i data-lucide="map-pin" class="w-3 h-3 text-gold/50"></i> Singapore</p>
                    <p class="text-xl font-serif font-black text-white flex items-center gap-2">{market_json['singapore_price']} <span class="text-[10px] text-rose-400 font-sans font-medium">{market_json['singapore_trend']}</span></p>
                </div>
            </div>
            <div class="mt-6 bg-dark border border-white/5 p-4 text-xs text-slate-400 font-mono border-l-2 border-l-gold flex items-start gap-3">
                <i data-lucide="globe" class="w-4 h-4 text-gold flex-shrink-0 mt-0.5"></i> 
                <p><strong class="text-white font-sans uppercase tracking-widest text-[10px] mr-2">Global Insight:</strong> {market_json['insight']}</p>
            </div>"""

    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    pattern = r'<!-- MARKET_DATA_ANCHOR_START -->.*?<!-- MARKET_DATA_ANCHOR_END -->'
    replacement = f'<!-- MARKET_DATA_ANCHOR_START -->\n{new_data_html}\n            <!-- MARKET_DATA_ANCHOR_END -->'
    updated_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)
    print("📈 首页大盘更新完毕！\n")

except Exception as e:
    print(f"⚠️ 获取房价数据失败，跳过: {e}\n")


# ---------------------------------------------------------
# 模块二：生成 10 篇高客单价 B2B 房产长文
# ---------------------------------------------------------
niche_topics = [
    "Top AI tools for luxury real estate lead generation in 2026",
    "How elite brokers use ChatGPT to write high-converting property descriptions",
    "Automating real estate email marketing campaigns with AI algorithms",
    "Best AI CRM software for top-tier real estate brokerages",
    "Using AI for predictive real estate market analysis and off-market properties",
    "AI virtual staging tools: Transforming empty properties to maximize ROI",
    "How real estate agents can use AI chatbots for 24/7 high-net-worth client support",
    "AI-powered social media content creation strategies for realtors",
    "Streamlining real estate contract analysis with AI legal assistants",
    "Generating realistic architectural renders with Midjourney for property developers"
]

MAX_RETRIES = 3
all_cards_html = ""

for index, topic in enumerate(niche_topics):
    print(f"🚀 正在生成文章 {index + 1}/10: [{topic}]")
    
    prompt = f"""
    You are a veteran Real Estate Tech consultant and data analyst. Your writing style is highly authoritative, analytical, and tailored for top 1% real estate brokers.
    Write a comprehensive tech blog post (at least 450 words) strictly about: "{topic}".
    CRITICAL RULES: No AI cliches ("Revolutionize", "Landscape"). Focus on ROI, data, and institutional-grade strategies.
    Output ONLY a valid JSON object:
    {{
      "title": "A highly clickable, professional title for elite brokers",
      "category": "One word: TOOLS, MARKETING, or ANALYTICS",
      "description": "Two sentences explaining how this strategy drives ROI.",
      "read_time": "e.g., 6 min",
      "image_prompt": "A prompt for an AI image generator describing a realistic, ultra-luxury real estate tech cover photo (e.g., 'Minimalist modern luxury penthouse interior with subtle glowing digital data graphs, obsidian and gold tones, cinematic lighting')",
      "content": "The full article body formatted in valid HTML. Use <h2>, <p>, <ul>. Do NOT include <html> or <body>."
    }}
    """
    
    data = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "Output ONLY JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                timeout=60.0 
            )
            data = json.loads(clean_json_response(response.choices[0].message.content))
            print(f"✅ 成功: {data['title']}")
            break  
        except Exception as e:
            time.sleep(5) 
            
    if data:
        date_str = datetime.now().strftime('%b %d')
        image_desc = data.get('image_prompt', 'minimalist luxury penthouse interior dark mode gold accents tech')
        encoded_image_prompt = urllib.parse.quote(image_desc)
        random_image = f"https://image.pollinations.ai/prompt/{encoded_image_prompt}?width=800&height=500&nologo=true"

        safe_title = "".join([c if c.isalnum() else "-" for c in data['title'].lower()])
        safe_title = re.sub(r'-+', '-', safe_title).strip('-')
        file_name = f"{safe_title}.html"
        
        os.makedirs('articles', exist_ok=True)
        
        # 带有 YMYL 免责声明的单页 HTML 模板 (Axiom 黑金主题)
        article_page_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - Axiom PropTech</title>
    <meta name="description" content="{data['description']}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
        tailwind.config = {{ theme: {{ extend: {{ colors: {{ dark: '#030508', navy: '#0a0f1c', gold: '#d4af37' }} }}, fontFamily: {{ sans: ['Inter', 'sans-serif'], serif: ['Playfair Display', 'serif'] }} }} }}
    </script>
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #030508; color: #cbd5e1; }}
        .article-body h2 {{ font-size: 1.8rem; font-weight: 900; font-family: 'Playfair Display', serif; color: #ffffff; margin-top: 2.5rem; margin-bottom: 1rem; }}
        .article-body p {{ margin-bottom: 1.5rem; font-size: 1.125rem; line-height: 1.8; color: #94a3b8; }}
        .article-body ul {{ list-style-type: square; padding-left: 1.5rem; margin-bottom: 1.5rem; color: #94a3b8; }}
        .article-body li {{ margin-bottom: 0.5rem; }}
        .article-body strong {{ color: #ffffff; font-weight: 600; }}
        .article-body a {{ color: #d4af37; text-decoration: none; border-bottom: 1px solid rgba(212,175,55,0.3); padding-bottom: 1px; }}
    </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-gold/30 selection:text-white">
    <nav class="border-b border-white/5 p-6 bg-dark/90 backdrop-blur-xl sticky top-0 z-50">
        <div class="max-w-4xl mx-auto flex items-center justify-between">
            <a href="../index.html" class="text-slate-400 hover:text-gold transition-colors flex items-center gap-2 font-bold uppercase tracking-widest text-xs">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Back to Intelligence
            </a>
            <div class="flex items-center gap-2">
                <div class="w-6 h-6 border border-gold/30 rounded-full flex items-center justify-center"><i data-lucide="hexagon" class="w-3 h-3 text-gold"></i></div>
                <span class="text-white font-serif font-black tracking-[0.1em] uppercase text-sm">Axiom<span class="text-gold">.</span></span>
            </div>
        </div>
    </nav>

    <main class="max-w-3xl mx-auto px-6 py-16 w-full flex-grow">
        <div class="mb-10 pb-8 border-b border-slate-800/50">
            <span class="text-gold border border-gold/30 px-3 py-1 font-bold text-[10px] tracking-[0.2em] uppercase">{data['category']}</span>
            <h1 class="text-4xl md:text-5xl font-serif font-black text-white mt-8 mb-8 leading-[1.15]">{data['title']}</h1>
            
            <div class="flex items-center justify-between border-t border-slate-800 pt-6">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-full bg-navy border border-slate-700 flex items-center justify-center">
                        <i data-lucide="user" class="w-4 h-4 text-gold"></i>
                    </div>
                    <div>
                        <p class="text-xs font-bold text-white uppercase tracking-widest">Axiom Editorial Desk</p>
                        <p class="text-[10px] text-slate-500 font-mono mt-1">Published on {date_str}</p>
                    </div>
                </div>
                <div class="text-slate-400 text-xs font-mono border border-slate-800 bg-navy px-3 py-1 rounded">
                    {data['read_time']} read
                </div>
            </div>
        </div>

        <div class="mb-12 rounded border border-white/5 overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)] relative">
            <img src="{random_image}" alt="Cover" class="w-full h-auto object-cover opacity-80 grayscale-[20%] hover:grayscale-0 transition-all duration-700">
            <div class="absolute inset-0 bg-gradient-to-t from-dark/50 to-transparent"></div>
        </div>

        <article class="article-body">
            {data['content']}
        </article>

        <!-- YMYL 免责声明 -->
        <div class="mt-20 p-6 bg-navy border border-slate-800 rounded-sm">
            <p class="text-[11px] text-slate-500 leading-relaxed font-mono">
                <strong class="text-slate-300">Compliance Disclaimer:</strong> This intelligence report was generated and compiled via autonomous AI models for educational purposes within the PropTech sector. It does not constitute financial, investment, or legal real estate advice. Real estate professionals must conduct independent due diligence.
            </p>
        </div>
    </main>
    <footer class="border-t border-white/5 py-10 text-center text-slate-600 text-[10px] uppercase tracking-widest font-bold bg-[#020305]">
        &copy; 2024 Axiom PropTech Intelligence. All rights reserved.
    </footer>
    <script>lucide.createIcons();</script>
</body>
</html>"""
        with open(f"articles/{file_name}", "w", encoding='utf-8') as f:
            f.write(article_page_html)
            
        update_sitemap(f"articles/{file_name}")

        # 生成插入主页的卡片 HTML
        new_article_html = f"""
                    <!-- AI Generated Article -->
                    <a href="articles/{file_name}" class="block group">
                        <article class="flex flex-col md:flex-row gap-8 bg-transparent p-0 transition-all duration-300">
                            <div class="w-full md:w-64 h-48 overflow-hidden flex-shrink-0 relative border border-slate-800">
                                <img src="{random_image}" alt="{data['title']}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 grayscale group-hover:grayscale-0">
                                <div class="absolute inset-0 bg-dark/20"></div>
                            </div>
                            <div class="flex flex-col justify-center py-2">
                                <div class="flex items-center gap-3 mb-4 text-[9px] font-bold uppercase tracking-[0.2em]">
                                    <span class="text-gold border border-gold/30 px-2 py-1">{data['category']}</span>
                                </div>
                                <h3 class="text-2xl font-black text-white group-hover:text-gold transition-colors mb-4 leading-tight font-serif">{data['title']}</h3>
                                <p class="text-slate-400 text-sm line-clamp-2 leading-relaxed mb-6">{data['description']}</p>
                                <div class="flex items-center text-[10px] text-slate-500 font-bold uppercase tracking-widest gap-4">
                                    <span class="flex items-center gap-1.5"><i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date_str}</span>
                                    <span class="flex items-center gap-1.5"><i data-lucide="clock" class="w-3.5 h-3.5"></i> {data['read_time']} READ</span>
                                </div>
                            </div>
                        </article>
                    </a>"""
        
        all_cards_html += new_article_html + "\n"
        time.sleep(8)

if all_cards_html:
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    anchor = "<!-- AI_ARTICLE_ANCHOR -->"
    if anchor in html_content:
        # 主页防撑爆机制，只保留最新的 21 篇文章
        article_blocks = html_content.split('<!-- AI Generated Article -->')
        if len(article_blocks) > 22: 
            kept_blocks = article_blocks[:22] 
            html_content = '<!-- AI Generated Article -->'.join(kept_blocks)

        updated_html = html_content.replace(anchor, f"{anchor}\n{all_cards_html}")
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("\n🎉 成功：全量文章与 Sitemap 已注入完毕！")
else:
    sys.exit(1)
