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
    print("📈 首页全球 6 城房价看板已更新为今日最新估值！\n")

except Exception as e:
    print(f"⚠️ 获取房价数据失败，跳过: {e}\n")


# ---------------------------------------------------------
# 模块二：动态感知热点，生成 7 篇高客单价房产长文
# ---------------------------------------------------------
print("🧠 正在让 AI 智囊团分析今日趋势，构思 7 个爆款房产科技话题...")
topic_prompt = """
You are an elite Real Estate Tech Trend Analyst. Based on the latest market trends, generate exactly 7 highly engaging, cutting-edge, and specific blog post topics about "Real Estate AI, PropTech, and Broker Automation".
Avoid generic topics. Focus on high ROI strategies, virtual staging, AI CRM, predictive analytics, and social media AI algorithms.
Output ONLY a valid JSON array of strings. No markdown, no extra text.
Example: ["How top 1% realtors are using AI voice agents for cold calling", "The exact ChatGPT prompt sequence to double your open house leads"]
"""

try:
    topic_response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system", "content": "Output ONLY a valid JSON array of strings."},
            {"role": "user", "content": topic_prompt}
        ],
        temperature=0.8,
        timeout=30.0
    )
    niche_topics = json.loads(clean_json_response(topic_response.choices[0].message.content))
    
    # 确保只取 7 个话题
    if isinstance(niche_topics, list) and len(niche_topics) > 0:
        niche_topics = niche_topics[:7]
        print(f"✅ 成功生成 {len(niche_topics)} 个今日热点话题：")
        for t in niche_topics:
            print(f" - {t}")
    else:
        raise ValueError("AI 返回的话题格式不正确")

except Exception as e:
    print(f"⚠️ 动态获取话题失败，启用紧急备用话题库: {e}")
    # 备用库，防止 API 偶尔抽风导致当天不发文
    niche_topics = [
        "Top AI tools for luxury real estate lead generation in 2026",
        "How elite brokers use ChatGPT to write high-converting property descriptions",
        "Automating real estate email marketing campaigns with AI algorithms",
        "Best AI CRM software for top-tier real estate brokerages",
        "Using AI for predictive real estate market analysis and off-market properties",
        "AI virtual staging tools: Transforming empty properties to maximize ROI",
        "AI-powered social media content creation strategies for realtors"
    ]

MAX_RETRIES = 3
all_cards_html = ""
current_year = datetime.now().year # 动态获取当前年份

for index, topic in enumerate(niche_topics):
    print(f"\n🚀 正在生成文章 {index + 1}/{len(niche_topics)}: [{topic}]")
    
    # 核心升级：严控单引号，防止双引号破坏 JSON 结构导致程序静默崩溃
    prompt = f"""
    You are a veteran Real Estate Tech consultant and data analyst. Write a comprehensive tech blog post (at least 600 words) strictly about: "{topic}".
    
    CRITICAL FORMATTING RULES (FAILURE IS NOT AN OPTION):
    1. Output ONLY valid HTML inside the "content" field. ABSOLUTELY NO MARKDOWN. Do not use **bold** or #. Use <strong>, <h2>, <h3>, <p>, <ul>, <li>.
    2. Start the "content" with a visually distinct summary box. You MUST use SINGLE QUOTES for all HTML attributes to avoid breaking the JSON format. Example:
       <div class='p-6 bg-[#0a0f1c] border border-gold/20 rounded-xl mb-8'>
         <h3 class='text-gold font-bold uppercase tracking-widest text-xs mb-4'>Key Takeaways</h3>
         <ul class='space-y-2'><li>...</li></ul>
       </div>
    3. Do NOT use double quotes (") inside the HTML content string. Use single quotes instead.
    4. Ensure the tone is authoritative, analytical, and tailored for top 1% elite real estate brokers. Focus on ROI.
    
    Output ONLY a valid JSON object:
    {{
      "title": "A highly clickable, professional title for elite brokers",
      "category": "One word: TOOLS, MARKETING, or ANALYTICS",
      "description": "Two sentences explaining how this strategy drives ROI.",
      "read_time": "e.g., 6 min",
      "image_prompt": "A SHORT, 5-10 word prompt for an AI image generator (e.g., 'Luxury modern penthouse interior glowing data')",
      "content": "The full article body formatted in valid HTML per the rules above. Do NOT include <html> or <body>."
    }}
    """
    
    data = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "You are a rigid HTML generator. Output ONLY JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                timeout=60.0 
            )
            data = json.loads(clean_json_response(response.choices[0].message.content))
            print(f"✅ 成功: {data['title']}")
            break  
        except Exception as e:
            print(f"⚠️ 第 {attempt + 1} 次尝试失败: {e}")
            time.sleep(5) 
            
    if data:
        date_str = datetime.now().strftime('%b %d')
        
        # 核心修复：1. 限制提示词长度防报错 2. 加入随机种子强制每次生成全新的图 3. 动态备用图库
        raw_image_desc = data.get('image_prompt', 'luxury real estate modern interior tech')
        clean_image_desc = re.sub(r'[^a-zA-Z0-9\s]', '', raw_image_desc).strip() # 只保留字母数字和空格
        encoded_image_prompt = urllib.parse.quote(clean_image_desc)
        
        # 加入随机种子，彻底打断 Pollinations 的缓存机制
        random_seed = random.randint(1, 9999999)
        random_image = f"https://image.pollinations.ai/prompt/{encoded_image_prompt}?width=800&height=500&nologo=true&seed={random_seed}"
        
        # 备用防爆底图库
        fallback_pool = [
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=800&auto=format&fit=crop"
        ]
        fallback_image = random.choice(fallback_pool)

        safe_title = "".join([c if c.isalnum() else "-" for c in data['title'].lower()])
        safe_title = re.sub(r'-+', '-', safe_title).strip('-')
        file_name = f"{safe_title}.html"
        
        os.makedirs('articles', exist_ok=True)
        
        # 带有 YMYL 免责声明的单页 HTML 模板
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
        .article-body h2 {{ font-size: 1.8rem; font-weight: 900; font-family: 'Playfair Display', serif; color: #ffffff; margin-top: 3rem; margin-bottom: 1.2rem; }}
        .article-body h3 {{ font-size: 1.4rem; font-weight: 700; color: #f1f5f9; margin-top: 2rem; margin-bottom: 1rem; }}
        .article-body p {{ margin-bottom: 1.8rem; font-size: 1.125rem; line-height: 1.8; color: #94a3b8; }}
        .article-body ul {{ list-style-type: square; padding-left: 1.5rem; margin-bottom: 1.8rem; color: #94a3b8; }}
        .article-body li {{ margin-bottom: 0.8rem; line-height: 1.6; }}
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
            <img src="{random_image}" onerror="this.onerror=null;this.src='{fallback_image}';" alt="Cover" class="w-full h-auto object-cover opacity-80 grayscale-[20%] hover:grayscale-0 transition-all duration-700">
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
    
    <footer class="border-t border-slate-800/50 py-12 bg-[#020305] mt-10">
        <div class="max-w-4xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
            <div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                &copy; {current_year} Axiom PropTech Intelligence.
            </div>
            <div class="flex gap-6 text-[10px] font-bold uppercase tracking-widest text-slate-500">
                <a href="../about.html" class="hover:text-gold transition-colors">About</a>
                <a href="../privacy.html" class="hover:text-gold transition-colors">Privacy Policy</a>
                <a href="../terms.html" class="hover:text-gold transition-colors">Terms of Service</a>
            </div>
        </div>
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
                                <img src="{random_image}" onerror="this.onerror=null;this.src='{fallback_image}';" alt="{data['title']}" loading="lazy" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 grayscale group-hover:grayscale-0">
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
        # 主页防撑爆机制，保留最新 21 篇
        article_blocks = html_content.split('<!-- AI Generated Article -->')
        if len(article_blocks) > 22: 
            kept_blocks = article_blocks[:22] 
            html_content = '<!-- AI Generated Article -->'.join(kept_blocks)

        updated_html = html_content.replace(anchor, f"{anchor}\n{all_cards_html}", 1)
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print("\n🎉 成功：全量高质文章、防爆图与合规页脚已注入完毕！")
    else:
        print("\n❌ 致命错误：在 index.html 中找不到锚点 <!-- AI_ARTICLE_ANCHOR -->！请检查首页代码。")
        sys.exit(1)
else:
    print("\n❌ 严重错误：7个话题全部生成失败，没有任何文章被渲染。请检查上面的错误日志！")
    sys.exit(1)
