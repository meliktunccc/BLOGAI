import streamlit as st
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Environment yükle
load_dotenv()

# Sayfa ayarları
st.set_page_config(
    page_title="BlogAI",
    page_icon="📝",
    layout="wide"
)

def load_blogs():
    """Kaydedilmiş blogları yükle"""
    try:
        with open('blogs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_blog(blog):
    """Blog kaydet"""
    blogs = load_blogs()
    blog['id'] = len(blogs) + 1
    blog['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    blogs.append(blog)
    
    with open('blogs.json', 'w', encoding='utf-8') as f:
        json.dump(blogs, f, ensure_ascii=False, indent=2)

def generate_blog(title, topic, keywords, word_count, tone, language_style, custom_prompt=""):
    """AI ile blog üret"""
    prompt = f"""
    Sen profesyonel bir blog yazarısın. Aşağıdaki kriterlere göre blog yazısı oluştur:
    
    📝 BLOG BİLGİLERİ:
    - Başlık: {title}
    - Konu/Kategori: {topic}
    - Anahtar Kelimeler: {keywords}
    - Uzunluk: {word_count}
    - Yazım Tonu: {tone}
    - Dil Stili: {language_style}
    - Özel İstek: {custom_prompt}
    
    📋 KURALLAR:
    1. Türkçe yazacaksın
    2. SEO uyumlu olacak
    3. Anahtar kelimeleri doğal bir şekilde dağıt
    4. Belirtilen uzunlukta yaz
    5. Belirtilen ton ve stilde yaz
    6. Başlıklar, alt başlıklar ve paragraflar kullan
    7. Okuyucu için değerli bilgiler ver
    
    Şimdi bu kriterlere göre kaliteli bir blog yazısı oluştur.
    """
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API Hatası: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Hata: {str(e)}"

# Ana uygulama
def main():
    st.title("🤖 BlogAI - Basit AI Blog Oluşturucu")
    st.markdown("---")
    
    # Sidebar - Menü
    menu = st.sidebar.selectbox("Menü", ["📝 Blog Oluştur", "📚 Bloglarım"])
    
    if menu == "📝 Blog Oluştur":
        st.header("📝 Yeni Blog Oluştur")
        
        # Form
        with st.form("blog_form"):
            # Ana bilgiler
            title = st.text_input("Blog Başlığı *", placeholder="Harika bir başlık...")
            
            # İki sütunlu düzen
            col1, col2 = st.columns(2)
            
            with col1:
                topic = st.selectbox("Konu/Kategori *", [
                    "Teknoloji", "Yapay Zeka", "Web Geliştirme", "Mobil Uygulama",
                    "Sağlık", "Spor", "Beslenme", "Yaşam Tarzı",
                    "İş Dünyası", "Girişimcilik", "Pazarlama", "Finans",
                    "Eğitim", "Öğrenme", "Kişisel Gelişim",
                    "Seyahat", "Yemek", "Hobi", "Sanat",
                    "Bilim", "Tarih", "Kültür", "Genel"
                ])
                
                word_count = st.selectbox("Kelime Sayısı", [
                    "Kısa (300-500 kelime)",
                    "Orta (500-800 kelime)", 
                    "Uzun (800-1200 kelime)",
                    "Çok Uzun (1200+ kelime)"
                ])
            
            with col2:
                tone = st.selectbox("Yazım Tonu", [
                    "Profesyonel", "Dostane", "Akademik", "Yaratıcı", 
                    "Teknik", "Eğlenceli", "Ciddi", "Samimi"
                ])
                
                language_style = st.selectbox("Dil Stili", [
                    "Basit ve Anlaşılır", "Teknik", "Günlük Konuşma",
                    "Akademik", "Blog Tarzı", "Haberci Dili"
                ])
            
            keywords = st.text_input("Anahtar Kelimeler *", placeholder="AI, teknoloji, gelecek (virgülle ayırın)")
            custom_prompt = st.text_area("Özel İstek (isteğe bağlı)", placeholder="Özel talimatlarınız...")
            
            submitted = st.form_submit_button("🚀 Blog Oluştur", type="primary")
            
            if submitted:
                if title and keywords:
                    with st.spinner("AI blog yazıyor... ⏳"):
                        content = generate_blog(title, topic, keywords, word_count, tone, language_style, custom_prompt)
                        
                        # Blog kaydet
                        blog = {
                            'title': title,
                            'topic': topic,
                            'keywords': keywords,
                            'word_count': word_count,
                            'tone': tone,
                            'language_style': language_style,
                            'content': content,
                            'custom_prompt': custom_prompt
                        }
                        save_blog(blog)
                        
                        st.success("✅ Blog başarıyla oluşturuldu!")
                        st.markdown("### 📄 Oluşturulan Blog:")
                        st.markdown(f"**Başlık:** {title}")
                        st.markdown(f"**Konu:** {topic}")
                        st.markdown(f"**Anahtar Kelimeler:** {keywords}")
                        st.markdown(f"**Uzunluk:** {word_count}")
                        st.markdown(f"**Ton:** {tone} | **Stil:** {language_style}")
                        st.markdown("---")
                        st.markdown(content)
                else:
                    st.error("❌ Lütfen başlık ve anahtar kelimeleri girin!")
    
    elif menu == "📚 Bloglarım":
        st.header("📚 Kaydedilmiş Bloglar")
        
        blogs = load_blogs()
        
        if not blogs:
            st.info("Henüz blog oluşturmamışsınız. 📝 Blog Oluştur sayfasına gidin!")
        else:
            for blog in reversed(blogs):  # En yeni önce
                with st.expander(f"📄 {blog['title']} - {blog['created_at']}"):
                    # Blog bilgilerini göster
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**🏷️ Konu:** {blog.get('topic', 'Belirtilmemiş')}")
                        st.markdown(f"**🔑 Anahtar Kelimeler:** {blog['keywords']}")
                        
                    with col_b:
                        st.markdown(f"**📏 Uzunluk:** {blog.get('word_count', 'Belirtilmemiş')}")
                        st.markdown(f"**🎭 Ton:** {blog.get('tone', 'Belirtilmemiş')}")
                    
                    if blog.get('custom_prompt'):
                        st.markdown(f"**💬 Özel İstek:** {blog['custom_prompt']}")
                    
                    st.markdown("---")
                    st.markdown(blog['content'])
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 İstatistikler**")
    blog_count = len(load_blogs())
    st.sidebar.metric("Toplam Blog", blog_count)

if __name__ == "__main__":
    main() 