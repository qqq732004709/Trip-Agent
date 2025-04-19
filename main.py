import streamlit as st
from agent.trip_agent import TripAgent

def render_itinerary(itinerary):
    """Render the itinerary as HTML cards"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h1 style="color: #2e86c1; text-align: center;">{itinerary['destination']} {itinerary['days']}日游</h1>
    """
    for day in itinerary['plan']:
        html += f"""
        <div style="background: #f8f9f9; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h2 style="color: #2874a6;">第{day['day']}天: {day['title']}</h2>
            <ul style="padding-left: 20px;">
        """
        for activity in day['activities']:
            html += f"<li>{activity}</li>"
        html += """
            </ul>
        </div>
        """
    html += "</div>"
    return html

def main():
    st.title("旅行规划助手")
    
    # User input
    user_input = st.text_area("请输入您的旅行需求（例如：我想要一个青岛的三日游行程，想吃海鲜、看日出、喝啤酒）")
    
    if st.button("生成行程"):
        if not user_input:
            st.warning("请输入旅行需求")
            return
            
        # Initialize agent (placeholder - will be implemented in trip_agent.py)
        agent = TripAgent()
        
        # Get itinerary from agent
        itinerary = agent.generate_itinerary(user_input)
        
        # Render itinerary
        st.components.v1.html(render_itinerary(itinerary), height=800)

if __name__ == "__main__":
    main()
