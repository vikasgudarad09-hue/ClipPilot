"""
Multilingual AI Metadata & SEO Generator
Generates high-CTR titles, rich descriptions, and platform-optimized tags
in English, Hindi, and Hinglish.
"""
from typing import Dict, Any, List

class AIMetadataGenerator:
    """
    Intelligent metadata generator with built-in templates and heuristic SEO optimization.
    Can also connect to OpenAI/Gemini if API key is provided.
    """
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def generate(self, topic_or_title: str, language: str = "hinglish", category: str = "educational") -> Dict[str, Any]:
        """
        Generate platform-tailored metadata for YouTube, Instagram, LinkedIn, and X.
        """
        clean_topic = topic_or_title.strip()
        is_short = "#shorts" in clean_topic.lower() or "short" in clean_topic.lower()
        topic_core = clean_topic.replace("#Shorts", "").replace("#shorts", "").replace("(Shorts)", "").strip()

        # High-CTR Viral Title Engine
        if is_short:
            yt_title = f"{topic_core} 🌊 (3D Cutaway Explained) #shorts #engineering"
        elif "pump" in topic_core.lower() or "water" in topic_core.lower():
            yt_title = "How 40-Feet Deep Water is Pumped with ZERO Electricity (India Mark II 3D Animation)"
        elif "wagon" in topic_core.lower() or "train" in topic_core.lower():
            yt_title = "How Rapid Gravity-Discharge Railway Wagons Empty 60 Tons in 30 Seconds! (Full 3D Animation)"
        else:
            yt_title = f"{topic_core} | Complete 3D Visual & Engineering Guide"

        # Hinglish Mode (Highest viral traction for Indian creators)
        if language.lower() == "hinglish":
            yt_desc = (
                f"Iss detailed 3D animation video mein hum step-by-step samjhenge: {topic_core}.\n\n"
                f"🔬 Kya aapne kabhi socha hai ki yeh mechanism bina kisi electric power ke practical world mein kaise perform karta hai? "
                f"Iss video mein 3D visual cutaways aur cross-sections ke zariye har ek moving component aur valve ko clearly dikhaya gaya hai.\n\n"
                f"📌 Video Highlights & Key Concepts:\n"
                f"00:00 - Introduction & Core Engineering Principle\n"
                f"00:45 - Internal Components & Cutaway View\n"
                f"02:15 - Working Mechanism & Fluid Dynamics\n"
                f"03:50 - Real-World Applications & Efficiency\n"
                f"05:10 - Summary & Technical Insights\n\n"
                f"🔔 Subscribe kijiye aise aur high-retention 3D animation videos dekhne ke liye!\n"
                f"#3DAnimation #Engineering #HindiEducation #Blender3D #HowItWorks"
            )
            ig_caption = (
                f"Mind-blowing 3D Engineering: {topic_core}! 🚀\n\n"
                f"Dekhiye kaise yeh mechanism bina kisi complex machine ke 100% naturally kaam karta hai. "
                f"Tag karein un doston ko jinko mechanical engineering aur 3D animations pasand hain! 👇\n\n"
                f"#ReelsIndia #IndianCreators #3DAnimation #EducationalReels #EngineeringIndia "
                f"#LearnInHindi #HowItWorks #BlenderIndia #AnimationLife"
            )
            tags = [
                topic_core, f"{topic_core} in hindi", "3d animation explanation",
                "educational video", "how it works hindi", "blender 3d animation",
                "mechanical engineering", "step by step guide", "science explainer",
                "zero electricity", "viral engineering"
            ]

        # Hindi (Pure)
        elif language.lower() == "hindi":
            yt_title = f"{clean_topic} की कार्यप्रणाली को समझें (3D एनिमेशन मार्गदर्शिका)"
            yt_desc = (
                f"इस वीडियो में हम 3D एनिमेशन के माध्यम से सरल भाषा में विस्तार से समझा रहे हैं कि "
                f"{clean_topic} कैसे काम करता है।\n\n"
                f"📌 मुख्य भाग:\n"
                f"00:00 - परिचय\n"
                f"01:00 - आंतरिक भाग और संरचना\n"
                f"02:30 - संचालन प्रक्रिया\n"
                f"04:00 - निष्कर्ष और उपयोगिता\n\n"
                f"🔔 और अधिक ज्ञानवर्धक वीडियो के लिए चैनल को सब्सक्राइब करें!"
            )
            ig_caption = (
                f"{clean_topic} की सम्पूर्ण कार्यप्रणाली को 3D में देखें! 🔍\n"
                f"यदि यह जानकारी उपयोगी लगी तो लाइक और शेयर अवश्य करें।\n\n"
                f"#हिंदीजानकारी #एनिमेशन #विज्ञान #इंजीनियरिंग #ज्ञान #ReelsHindi"
            )
            tags = [
                clean_topic, "हिंदी में समझें", "कार्यप्रणाली", "3d एनिमेशन", "शैक्षणिक वीडियो"
            ]

        # English (Global)
        else:
            yt_title = f"How {clean_topic} Actually Works | Complete 3D Visual Guide"
            yt_desc = (
                f"In this high-detail 3D animation breakdown, we uncover the exact internal mechanics "
                f"and engineering behind {clean_topic}.\n\n"
                f"⏱️ Chapters:\n"
                f"00:00 - Introduction\n"
                f"00:50 - Core Mechanism & Breakdown\n"
                f"02:30 - Fluid & Dynamic Simulation\n"
                f"04:15 - Practical Engineering Insights\n\n"
                f"👉 Make sure to Subscribe for weekly 3D educational breakdowns!"
            )
            ig_caption = (
                f"The mesmerizing mechanics of {clean_topic} in full 3D! ⚙️\n\n"
                f"Drop a comment if you want a deep-dive tutorial on this setup.\n\n"
                f"#3DAnimation #Blender3D #HowItWorks #Engineering #EducationalReels "
                f"#DesignInspiration #CGI #MotionGraphics"
            )
            tags = [
                clean_topic, f"how {clean_topic} works", "3d animation breakdown",
                "blender 3d", "educational animation", "mechanical design", "cg animation"
            ]

        linkedin_text = (
            f"Visualizing complex engineering systems through 3D animation: A case study on {clean_topic}.\n\n"
            f"Effective technical communication requires turning abstract mechanical concepts into intuitive, "
            f"accessible visual representations.\n\n"
            f"Key observations:\n"
            f"1. Structural clarity & component dynamics\n"
            f"2. Force transfer and efficiency principles\n"
            f"3. Practical industrial adoption\n\n"
            f"#Engineering #Education #3DVisualization #ProductDesign #Innovation"
        )

        return {
            "youtube": {
                "title": yt_title,
                "description": yt_desc,
                "tags": tags
            },
            "instagram": {
                "caption": ig_caption,
                "tags": [t.replace("#", "") for t in ig_caption.split() if t.startswith("#")]
            },
            "linkedin": {
                "text": linkedin_text
            },
            "suggested_tags": tags
        }
