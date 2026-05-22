# pip install -qU langchain "langchain[google-genai]"
from langchain.agents import create_agent
from langchain_core.tools import tool
import requests


@tool("get_products", description="Get the products that the store offers")
def get_products():
    """Get the products that the store offers"""
    url = "https://api.escuelajs.co/api/v1/products"
    request = requests.get(url)
    products = request.json()
    return " | ".join([f"{product['title']} -> {product['price']}" for product in products])


@tool("get_wether", description="Get the wether of a city")
def get_wether(city : str):
    response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1")
    data = response.json()
    latitude = data['results'][0]['latitude']
    longitude = data['results'][0]['longitude']
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true")
    data = response.json()
    response = f"The wether in {city} is {data['current_weather']['temperature']}C with {data['current_weather']['windspeed']}k/m of winds."
    return response


tools = [get_products, get_wether]


system_prompt = """
Eres un asistente de ventas que ayuda a los clientes a encontrar los productos que necesitan y dar el clima de una cuidad.

Tus tools son :
- get_products : para obtener los prodictos que afrece la tienda
- get_wether : para obtener el clima de una cuidad
"""


agent = create_agent(
    model="google_genai:gemini-3-flash-preview",
    tools=tools , 
    system_prompt=system_prompt,
)