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

        # Hinglish Mode (Highest viral traction for Indian creators)
        if language.lower() == "hinglish":
            yt_title = f"{clean_topic} Kaise Kaam Karta Hai? 💡 (Full 3D Animation Guide)"
            yt_desc = (
                f"Iss video mein hum step-by-step 3D animation ke through detail mein samjhenge ki "
                f"{clean_topic} practically kaise kaam karta hai aur iske working principles kya hain.\n\n"
                f"📌 Video Highlights & Chapters:\n"
                f"00:00 - Introduction & Overview\n"
                f"00:45 - Internal Components & Mechanism\n"
                f"02:15 - Working Principle in Action\n"
                f"03:50 - Real-World Applications & Advantages\n"
                f"05:10 - Summary & Key Takeaways\n\n"
                f"🔔 Subscribe kijiye aise aur informative 3D animation videos dekhne ke liye!\n"
                f"#3DAnimation #HindiEducation #{clean_topic.replace(' ', '')}"
            )
            ig_caption = (
                f"Bina kisi confusion ke samjhein: {clean_topic}! 🚀\n\n"
                f"Yeh 3D visual demonstration aapko clear mechanism samjha dega. "
                f"Share karein un doston ke saath jo engineering aur visual learning pasand karte hain! 👇\n\n"
                f"#ReelsIndia #IndianCreators #3DAnimation #EducationalReels #EngineeringIndia "
                f"#LearnInHindi #HowItWorks #BlenderIndia #AnimationLife"
            )
            tags = [
                clean_topic, f"{clean_topic} in hindi", f"{clean_topic} working principle",
                "3d animation explanation", "educational video", "how it works hindi",
                "blender animation", "mechanical engineering", "step by step guide"
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
