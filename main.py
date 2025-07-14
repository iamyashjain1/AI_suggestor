import chainlit as cl
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

allowed_ports = [3000, 5173]
allow_origins = [f"http://localhost:{port}" for port in allowed_ports] + \
                [f"http://127.0.0.1:{port}" for port in allowed_ports]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add proper CORS settings to allow frontend access with credentials


import google.generativeai as genai
from typing import Optional, Dict, List
import re
import asyncio
from datetime import datetime
import json

# Configure Gemini
genai.configure(api_key="AIzaSyCNQF9HwY19SVbmErBNNJ9RxG7KgDaNE8M")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

# Bot Configuration
BOT_NAME = "ShopMate"
BOT_EMOJI = "🛒"

# Enhanced Product Analysis Prompts
def generate_product_description_prompt(product_name: str) -> str:
    """Generate a comprehensive product description prompt"""
    return f"""
You are ShopMate, a professional shopping assistant like a Flipkart expert. Create a detailed product description for: "{product_name}".

Format your response EXACTLY as follows:

🎯 PRODUCT OVERVIEW:
Write a compelling 3-4 sentence introduction about the product that highlights its main appeal and market position.

⭐ KEY FEATURES & SPECIFICATIONS:
• Primary feature with specific details and emoji
• Technical specification with numbers/details and emoji
• Unique selling point with emoji
• Performance/quality aspect with emoji
• Design/build quality with emoji

✅ MAJOR ADVANTAGES:
• Advantage 1 with detailed explanation
• Advantage 2 with detailed explanation
• Advantage 3 with detailed explanation
• Advantage 4 with detailed explanation

❌ POTENTIAL DRAWBACKS:
• Limitation 1 with context
• Limitation 2 with context
• Limitation 3 with context

💰 PRICING & VALUE:
• Price Range: ₹[X,XXX - Y,XXX] (Current Indian market)
• Value Proposition: [Explain if it's worth the price]
• Best Deals: [Mention where to find best prices]

👥 IDEAL FOR:
• [Target audience 1] - [Why it's perfect for them]
• [Target audience 2] - [Why it's perfect for them]
• [Target audience 3] - [Why it's perfect for them]

🌟 EXPERT RATING: [X.X/5.0] ⭐
Verdict: [2-3 sentence summary of overall recommendation]

Keep it comprehensive yet under 400 words. Use specific details and avoid generic statements.
"""

def generate_product_suggestion_prompt(user_requirements: str) -> str:
    """Generate personalized product suggestions based on user requirements"""
    return f"""
You are ShopMate, acting like a professional Flipkart sales expert. Based on these requirements: "{user_requirements}", suggest 4 specific real products with detailed analysis.

Format your response EXACTLY as follows:

🎯 UNDERSTANDING YOUR NEEDS:
[Summarize what the user is looking for in 2-3 sentences]

💡 MY TOP RECOMMENDATIONS:

## 1. 🥇 [Brand + Full Product Name]
💰 Price: ₹[X,XXX - Y,XXX]
⭐ Rating: [X.X/5] ([Y,XXX+ reviews])
🎯 Perfect Match Because: [Explain why this fits their needs]
🔥 Best Feature: [Highlight the standout feature]
📦 Availability: [Stock status and delivery info]

## 2. 🥈 [Brand + Full Product Name]
💰 Price: ₹[X,XXX - Y,XXX]
⭐ Rating: [X.X/5] ([Y,XXX+ reviews])
🎯 Perfect Match Because: [Explain why this fits their needs]
🔥 Best Feature: [Highlight the standout feature]
📦 Availability: [Stock status and delivery info]

## 3. 🥉 [Brand + Full Product Name]
💰 Price: ₹[X,XXX - Y,XXX]
⭐ Rating: [X.X/5] ([Y,XXX+ reviews])
🎯 Perfect Match Because: [Explain why this fits their needs]
🔥 Best Feature: [Highlight the standout feature]
📦 Availability: [Stock status and delivery info]

## 4. 💎 [Brand + Full Product Name] (Premium Choice)
💰 Price: ₹[X,XXX - Y,XXX]
⭐ Rating: [X.X/5] ([Y,XXX+ reviews])
🎯 Perfect Match Because: [Explain why this fits their needs]
🔥 Best Feature: [Highlight the standout feature]
📦 Availability: [Stock status and delivery info]

---

🏆 MY PERSONAL RECOMMENDATION:
Based on your requirements, I'd personally recommend [Product Name] because [detailed reasoning].

🛒 NEXT STEPS:
1. Compare these options in detail
2. Check current offers and discounts
3. Read recent customer reviews
4. Consider extended warranty options

Keep under 500 words with real, currently available products.
"""

def generate_comparison_prompt(product1: str, product2: str) -> str:
    """Generate comprehensive product comparison with visual elements"""
    return f"""
You are ShopMate, a professional product comparison expert. Create a detailed comparison between "{product1}" and "{product2}".

Format your response EXACTLY as follows:

# 🥊 {product1} vs {product2}

## 🏆 QUICK VERDICT
Winner: {product1} / {product2} / It's a tie!
Reason: [1-2 sentence explanation]

## 📊 DETAILED COMPARISON

### 💰 PRICING
| Aspect | {product1} | {product2} |
|--------|-------------|-------------|
| Current Price | ₹[X,XXX] | ₹[X,XXX] |
| Value Rating | [X/10] ⭐ | [X/10] ⭐ |
| Best Deals | [Platform/offer] | [Platform/offer] |

### 🔧 SPECIFICATIONS & PERFORMANCE
| Feature | {product1} | {product2} |
|---------|-------------|-------------|
| Key Spec 1 | [Details] | [Details] |
| Key Spec 2 | [Details] | [Details] |
| Performance | [Rating/10] | [Rating/10] |
| Build Quality | [Rating/10] | [Rating/10] |

### 👥 USER EXPERIENCE
| Aspect | {product1} | {product2} |
|--------|-------------|-------------|
| Ease of Use | [Rating/10] | [Rating/10] |
| Customer Rating | [X.X/5] ([Y,XXX reviews]) | [X.X/5] ([Y,XXX reviews]) |
| After-Sales | [Rating/10] | [Rating/10] |

## 🎯 DETAILED ANALYSIS

### 🟢 {product1} - STRENGTHS
• [Strength 1 with explanation]
• [Strength 2 with explanation]
• [Strength 3 with explanation]

### 🔴 {product1} - WEAKNESSES
• [Weakness 1 with context]
• [Weakness 2 with context]

### 🟢 {product2} - STRENGTHS
• [Strength 1 with explanation]
• [Strength 2 with explanation]
• [Strength 3 with explanation]

### 🔴 {product2} - WEAKNESSES
• [Weakness 1 with context]
• [Weakness 2 with context]

## 🎯 PERSONALIZED RECOMMENDATIONS

Choose {product1} if you:
• [Scenario 1]
• [Scenario 2]
• [Scenario 3]

Choose {product2} if you:
• [Scenario 1]
• [Scenario 2]
• [Scenario 3]

## 📈 FINAL SCORE BREAKDOWN

Overall Performance: {product1} [X/10] | {product2} [X/10]
Value for Money:     {product1} [X/10] | {product2} [X/10]
User Experience:     {product1} [X/10] | {product2} [X/10]
Future-Proofing:     {product1} [X/10] | {product2} [X/10]

🏆 FINAL RECOMMENDATION:
[Detailed 2-3 sentence recommendation based on analysis]

Keep under 600 words with accurate, helpful comparisons.
"""

# Enhanced Follow-up Button Functions

def create_main_action_buttons():
    """Create main action buttons with Flipkart styling"""
    return [
        cl.Action(
            name="describe",
            value="describe",
            payload={"action": "describe"},
            description="Get detailed product information",
            label="📱 Product Description"
        ),
        cl.Action(
            name="suggest",
            value="suggest",
            payload={"action": "suggest"},
            description="Get personalized product suggestions",
            label="🎯 Product Suggestions"
        ),
        cl.Action(
            name="compare",
            value="compare",
            payload={"action": "compare"},
            description="Compare two products",
            label="⚖ Product Comparison"
        )
    ]

def create_description_followup_buttons(product_name: str):
    """Create follow-up buttons for product description"""
    return [
        cl.Action(
            name="detailed_specs",
            value=f"detailed_specs_{product_name}",
            payload={"action": "detailed_specs", "product": product_name},
            description="Get technical specifications",
            label="🔧 Detailed Specs"
        ),
        cl.Action(
            name="user_reviews",
            value=f"user_reviews_{product_name}",
            payload={"action": "user_reviews", "product": product_name},
            description="See what users say",
            label="⭐ User Reviews"
        ),
        cl.Action(
            name="alternatives",
            value=f"alternatives_{product_name}",
            payload={"action": "alternatives", "product": product_name},
            description="Find similar products",
            label="🔍 Alternatives"
        ),
        cl.Action(
            name="best_deals",
            value=f"best_deals_{product_name}",
            payload={"action": "best_deals", "product": product_name},
            description="Find best prices",
            label="💰 Best Deals"
        )
    ]

def create_suggestion_followup_buttons():
    """Create follow-up buttons for product suggestions"""
    return [
        cl.Action(
            name="compare_suggestions",
            value="compare_suggestions",
            payload={"action": "compare_suggestions"},
            description="Compare suggested products",
            label="⚖ Compare These"
        ),
        cl.Action(
            name="refine_search",
            value="refine_search",
            payload={"action": "refine_search"},
            description="Refine your requirements",
            label="🎯 Refine Search"
        ),
        cl.Action(
            name="budget_options",
            value="budget_options",
            payload={"action": "budget_options"},
            description="Show budget alternatives",
            label="💸 Budget Options"
        ),
        cl.Action(
            name="premium_options",
            value="premium_options",
            payload={"action": "premium_options"},
            description="Show premium alternatives",
            label="💎 Premium Options"
        )
    ]

def create_comparison_followup_buttons():
    """Create follow-up buttons for product comparison"""
    return [
        cl.Action(
            name="detailed_comparison",
            value="detailed_comparison",
            payload={"action": "detailed_comparison"},
            description="Get more detailed analysis",
            label="🔍 Deeper Analysis"
        ),
        cl.Action(
            name="pros_cons",
            value="pros_cons",
            payload={"action": "pros_cons"},
            description="Detailed pros and cons",
            label="✅❌ Pros & Cons"
        ),
        cl.Action(
            name="similar_comparisons",
            value="similar_comparisons",
            payload={"action": "similar_comparisons"},
            description="Compare with other products",
            label="🔄 More Comparisons"
        )
    ]

# Session Management
class ChatSession:
    def __init__(self):
        self.mode = None
        self.comparison_product1 = None
        self.last_product = None
        self.last_suggestions = []
        self.user_preferences = {}
    
    def set_mode(self, mode: str):
        self.mode = mode
    
    def get_mode(self):
        return self.mode
    
    def reset_mode(self):
        self.mode = None
        self.comparison_product1 = None

# Enhanced Follow-up Handlers
def generate_detailed_specs_prompt(product_name: str) -> str:
    """Generate detailed specifications prompt"""
    return f"""
You are ShopMate. Provide comprehensive technical specifications for: "{product_name}".

Format as:
## 🔧 Detailed Specifications - {product_name}

📐 DIMENSIONS & BUILD:
• Size: [dimensions]
• Weight: [weight]
• Material: [material details]
• Colors: [available colors]

⚡ PERFORMANCE SPECS:
• [Key performance metrics with numbers]
• [Processing/speed details]
• [Capacity/storage details]
• [Battery/power details if applicable]

🔌 CONNECTIVITY & FEATURES:
• [Connection options]
• [Special features]
• [Compatibility info]

📦 PACKAGE CONTENTS:
• [What's included in the box]

🛡 WARRANTY & SUPPORT:
• [Warranty information]
• [Service support details]

Keep detailed but under 300 words.
"""

def generate_user_reviews_prompt(product_name: str) -> str:
    """Generate user reviews summary prompt"""
    return f"""
You are ShopMate. Summarize user reviews and feedback for: "{product_name}".

Format as:
## ⭐ User Reviews Summary - {product_name}

📊 OVERALL RATING: [X.X/5] based on [X,XXX+] reviews

👍 WHAT USERS LOVE:
• [Most praised feature 1] - "[Sample positive quote]"
• [Most praised feature 2] - "[Sample positive quote]"
• [Most praised feature 3] - "[Sample positive quote]"

👎 COMMON COMPLAINTS:
• [Common issue 1] - "[Sample negative quote]"
• [Common issue 2] - "[Sample negative quote]"

💡 USER TIPS:
• [Helpful tip from users 1]
• [Helpful tip from users 2]

🎯 VERDICT FROM REAL USERS:
[2-3 sentence summary of overall user sentiment]

Keep realistic and balanced, under 250 words.
"""

def generate_best_deals_prompt(product_name: str) -> str:
    """Generate best deals prompt"""
    return f"""
You are ShopMate. Find the best deals and offers for: "{product_name}".

Format as:
## 💰 Best Deals - {product_name}

🔥 CURRENT BEST OFFERS:
• Flipkart: ₹[X,XXX] - [Special offer/discount]
• Amazon: ₹[X,XXX] - [Special offer/discount]  
• Other Platform: ₹[X,XXX] - [Special offer/discount]

💳 PAYMENT OFFERS:
• [Bank offer 1]
• [Credit card offer]
• [EMI options]

🎁 BUNDLE DEALS:
• [Bundle option 1]
• [Bundle option 2]

📅 UPCOMING SALES:
• [Next sale event and expected discount]

💡 MONEY-SAVING TIPS:
• [Tip 1 for getting best price]
• [Tip 2 for getting best price]

🏆 RECOMMENDED PURCHASE:
Buy from [Platform] at ₹[X,XXX] because [reason].

Keep practical and actionable, under 200 words.
"""

# Main Chat Functions
@cl.on_chat_start
async def start():
    """Initialize chat with clean Flipkart-themed welcome"""
    # Initialize session
    cl.user_session.set("chat_session", ChatSession())
    
    welcome_msg = f"""# 🛒 Welcome to {BOT_NAME}
Your AI Shopping Assistant - Powered by Flipkart Intelligence

## 🎯 How I Can Help You:

📱 Product Descriptions: Get detailed insights about any product
🎯 Smart Suggestions: Find products based on your needs & budget  
⚖ Product Comparisons: Compare products with detailed analysis

---

Choose an option below to get started! 👇
"""
    
    await cl.Message(
        content=welcome_msg,
        actions=create_main_action_buttons()
    ).send()

# Enhanced Action Handlers
@cl.action_callback("describe")
async def on_describe_action(action):
    """Handle product description requests"""
    session = cl.user_session.get("chat_session")
    session.set_mode("describe")
    
    msg = """
## 📱 Product Description Service

Just type the name of any product and I'll provide you with:
- Comprehensive overview and key features
- Detailed pros and cons analysis  
- Pricing information and value assessment
- Target audience recommendations
- Expert rating and verdict

Example: "iPhone 15 Pro", "Samsung Galaxy S24", "MacBook Air M2"
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

@cl.action_callback("suggest")
async def on_suggest_action(action):
    """Handle product suggestion requests"""
    session = cl.user_session.get("chat_session")
    session.set_mode("suggest")
    
    msg = """
## 🎯 Product Suggestion Service

Tell me what you're looking for and I'll suggest the best products for you!

Include details like:
- What type of product you need
- Your budget range
- Specific requirements or preferences
- Intended use case

Example: "Gaming laptop under ₹80,000", "Smartphone with good camera under ₹25,000", "Wireless earbuds for gym"
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

@cl.action_callback("compare")
async def on_compare_action(action):
    """Handle product comparison requests"""
    session = cl.user_session.get("chat_session")
    session.set_mode("compare")
    
    msg = """
## ⚖ Product Comparison Service

I'll help you compare two products with:
- Detailed specification comparison
- Performance analysis with ratings
- Pros and cons breakdown
- Personalized recommendations
- Final verdict with scoring

Enter the first product you want to compare:
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

# Enhanced Follow-up Action Handlers
@cl.action_callback("detailed_specs")
async def on_detailed_specs_action(action):
    """Handle detailed specifications request"""
    # Extract product name from action value
    product_name = action.value.replace("detailed_specs_", "")
    await process_followup_query("detailed_specs", product_name)

@cl.action_callback("user_reviews")
async def on_user_reviews_action(action):
    """Handle user reviews request"""
    # Extract product name from action value
    product_name = action.value.replace("user_reviews_", "")
    await process_followup_query("user_reviews", product_name)

@cl.action_callback("alternatives")
async def on_alternatives_action(action):
    """Handle alternatives request"""
    # Extract product name from action value
    product_name = action.value.replace("alternatives_", "")
    session = cl.user_session.get("chat_session")
    session.set_mode("suggest")
    await process_product_query(f"alternatives to {product_name}")

@cl.action_callback("best_deals")
async def on_best_deals_action(action):
    """Handle best deals request"""
    # Extract product name from action value
    product_name = action.value.replace("best_deals_", "")
    await process_followup_query("best_deals", product_name)

# Additional follow-up handlers for suggestion buttons
@cl.action_callback("compare_suggestions")
async def on_compare_suggestions_action(action):
    """Handle compare suggestions request"""
    session = cl.user_session.get("chat_session")
    session.set_mode("compare")
    
    msg = """
### ⚖ Compare Products
Enter the first product you want to compare:
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

@cl.action_callback("refine_search")
async def on_refine_search_action(action):
    """Handle refine search request"""
    session = cl.user_session.get("chat_session")
    session.set_mode("suggest")
    
    msg = """
### 🎯 Refine Your Search
Tell me more specific requirements:
- Preferred brand or features
- Exact budget range
- Specific use case or needs
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

@cl.action_callback("budget_options")
async def on_budget_options_action(action):
    """Handle budget options request"""
    session = cl.user_session.get("chat_session")
    session.set_mode("suggest")
    
    msg = """
### 💸 Budget Options
What's your budget range and what type of product are you looking for?
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

@cl.action_callback("premium_options")
async def on_premium_options_action(action):
    """Handle premium options request"""
    session = cl.user_session.get("chat_session")
    session.set_mode("suggest")
    
    msg = """
### 💎 Premium Options
What premium product are you looking for? I'll show you the best high-end options!
"""
    await cl.Message(content=msg, actions=create_main_action_buttons()).send()

# Core Processing Functions
async def process_followup_query(query_type: str, product_name: str):
    """Process follow-up queries"""
    msg = cl.Message(content="🔍 Getting detailed information...")
    await msg.send()
    try:
        if query_type == "detailed_specs":
            prompt = generate_detailed_specs_prompt(product_name)
        elif query_type == "user_reviews":
            prompt = generate_user_reviews_prompt(product_name)
        elif query_type == "best_deals":
            prompt = generate_best_deals_prompt(product_name)
        else:
            raise ValueError(f"Unknown query type: {query_type}")
        response = model.generate_content(prompt)
        await msg.update(response.text)
        await cl.Message(
            content="Need more help? 👇",
            actions=create_main_action_buttons()
        ).send()
    except Exception as e:
        await msg.update("😅 Sorry, I couldn't process that request. Please try again with a different product or be more specific!")
        await cl.Message(
            content="Let's try something else! 👇",
            actions=create_main_action_buttons()
        ).send()

async def process_product_query(user_input: str):
    """Process product queries with enhanced error handling"""
    session = cl.user_session.get("chat_session")
    mode = session.get_mode()
    
    # Show loading message
    msg = cl.Message(content="🔍 Analyzing products...")
    await msg.send()
    
    try:
        # Generate response based on mode
        if mode == "describe":
            prompt = generate_product_description_prompt(user_input)
            session.last_product = user_input
        elif mode == "suggest":
            prompt = generate_product_suggestion_prompt(user_input)
        elif mode == "compare":
            if not session.comparison_product1:
                session.comparison_product1 = user_input
                msg.content = f"✅ First product: {user_input}\n\n📝 Now enter the second product to compare:"
                await msg.update()

                return
            else:
                prompt = generate_comparison_prompt(session.comparison_product1, user_input)
        else:
            # Default to description
            prompt = generate_product_description_prompt(user_input)
            session.last_product = user_input
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Update with final response
        msg.content = response.text.strip()
        await msg.update()

        
        # Show appropriate follow-up buttons
        if mode == "describe":
            await cl.Message(
                content="Want to know more? 👇",
                actions=create_description_followup_buttons(session.last_product)
            ).send()
        elif mode == "suggest":
            await cl.Message(
                content="What would you like to do next? 👇",
                actions=create_suggestion_followup_buttons()
            ).send()
        elif mode == "compare":
            await cl.Message(
                content="Want more analysis? 👇",
                actions=create_comparison_followup_buttons()
            ).send()
        
        # Reset session
        session.reset_mode()
        
        # Show main buttons for next action
        await cl.Message(
            content="---\n*Start a new search?* 👇",
            actions=create_main_action_buttons()
        ).send()
        
    except Exception as e:
        msg.content= "😅 Sorry, I couldn't process that request. Please try again with a different product or be more specific!"
        await msg.update()
        session.reset_mode()
        await cl.Message(
            content="Let's try again! 👇",
            actions=create_main_action_buttons()
        ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Enhanced message handling"""
    user_input = message.content.strip()
    session = cl.user_session.get("chat_session")
    
    # Handle empty input
    if not user_input:
        await cl.Message(
            content="Please tell me what you're looking for! 😊",
            actions=create_main_action_buttons()
        ).send()
        return
    
    # Handle greetings
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'thanks', 'thank you']
    if any(greeting in user_input.lower() for greeting in greetings):
        if 'thank' in user_input.lower():
            response = "You're welcome! 😊 I'm always here to help you find the perfect products!"
        else:
            response = f"Hello! 👋 I'm {BOT_NAME}, your AI shopping assistant! How can I help you find the perfect product today?"
        
        await cl.Message(
            content=response,
            actions=create_main_action_buttons()
        ).send()
        return
    
    # Handle cases where mode is not set - default to description
    if not session.get_mode():
        session.set_mode("describe")
    
    # Process the query
    await process_product_query(user_input)

if __name__ == "__main__":
    cl.run()