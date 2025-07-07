import chainlit as cl
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv

load_dotenv()
# ✅ Setup Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_product_info(product_name):
    try:
        res = requests.get(
            "https://serpapi.com/search.json",
            params={"q": product_name, "engine": "google", "api_key": SERPAPI_KEY}
        )
        data = res.json()
        item = data.get("shopping_results", [{}])[0]
        return {
            "title": item.get("title"),
            "price": item.get("price"),
            "link": item.get("link"),
            "image": item.get("thumbnail"),
            "source": item.get("source")
        }
    except Exception as e:
        print("Error in fetch_product_info:", e)
        return None


async def stream_response(content: str):
    # Use Gemini's async content generation
    msg = cl.Message(content="")
    await msg.send()
    response = await model.generate_content_async(content)
    if hasattr(response, 'text'):
        msg.content = response.text
        await msg.update()


@cl.on_message
async def main_handler(msg: cl.Message):
    user_input = msg.content.lower().strip()
    history = cl.user_session.get("history") or []

    # 🔁 Compare Alternatives from Button or Message
    # 🔁 Compare Alternatives (natural triggers)
    if any(phrase in user_input for phrase in ["compare alternatives", "compare them", "compare above", "compare those", "compare options"]):
        if not history:
            await cl.Message(content="⚠️ No recent product to find alternatives for.").send()
            return

        last_product = history[-1]["product"]
        prompt = f"""
You are a product comparison expert.

The user previously asked about **{last_product}**.

Please do the following:
1. Identify 2–3 close **alternatives** to "{last_product}".
2. Create a **side-by-side comparison** of features, pros/cons, and pricing.
3. Highlight which might be a better choice for different user needs.
"""
        await stream_response(prompt)
        return

    # 🔁 Compare mode (e.g., "iPhone vs Samsung")
    if " vs " in user_input or user_input.startswith("compare "):
        products = user_input.replace("compare", "").split(" vs ")
        if len(products) >= 2:
            p1, p2 = products[0].strip(), products[1].strip()
            prompt = f"""
Compare these two products as a detailed product reviewer:

Product 1: {p1}
Product 2: {p2}

Include:
- 📝 Overview
- ✅ Pros & ❌ Cons of each
- 📊 Comparison Table
- 🏆 Which is better and why?
"""
            await stream_response(prompt)
            return

    # 📝 Summarization
    if "summarize" in user_input:
        if history:
            last = history[-1]["explanation"]
            summary = model.generate_content(f"Summarize this explanation:\n\n{last}").text.strip()
            await cl.Message(content=f"✂️ Summary:\n{summary}").send()
        else:
            await cl.Message(content="⚠️ No product explanation to summarize yet.").send()
        return

    # 🧠 Product explanation
    prompt = f"""
You are a product expert and reviewer.

Explain the product: **"{user_input}"** in detail.

Include:
1. 📝 Overview
2. ✅ Pros
3. ❌ Cons
4. 🔄 Alternatives
"""
    # Stream explanation (now just generate full response)
    stream_prompt = prompt
    full_explanation = ""
    msg = cl.Message(content="")
    await msg.send()
    response = await model.generate_content_async(stream_prompt)
    if hasattr(response, 'text'):
        msg.content = response.text
        full_explanation = response.text
        await msg.update()

    # Save in session
    history.append({"product": user_input, "explanation": full_explanation})
    cl.user_session.set("history", history)

    # Add Compare Alternatives button
    await cl.Message(
        content="🔍 Want to compare alternatives?",
        actions=[
            cl.Action(name="compare", label="🔄 Compare Alternatives", payload="compare alternatives")
        ]
    ).send()

    # 🛍️ Show product price/image
    info = fetch_product_info(user_input)
    if info:
        image_block = cl.Image(name="Product", display="inline", url=info['image']) if info.get('image') else None
        await cl.Message(
            content=f"🛍️ [{info['title']}]({info['link']})\n💵 {info['price']} from {info['source']}",
            elements=[image_block] if image_block else []
        ).send()
